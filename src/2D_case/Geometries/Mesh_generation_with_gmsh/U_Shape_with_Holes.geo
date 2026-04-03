SetFactory("Built-in");

// ======================================================
// Scaled U-shaped domain with 2 circular holes near upper borders
// This is a uniform triangular mesh
// ======================================================

h  = 0.01;  
r1 = 1.0;    
r2  = 0.75;
H0    = 1;

rh = 0.02;

// Place holes near upper left/right borders (inside the top band)
c1 =  0.875;          // right hole x
c2 = -0.875;          // left hole x
yh = H0 - 0.10;       // near top boundary but safely inside

// ---------------- Points ----------------
Point(11) = {0, 0, 0, h};   // center of arcs

// Outer boundary
Point(1) = {-r1, H0, 0, h};
Point(2) = {-r1, 0, 0, h};
Point(3) = {0, -r1, 0, h};
Point(4) = {r1, 0, 0, h};
Point(5) = {r1, H0, 0, h};

// Inner boundary
Point(6)  = {r2, H0, 0, h};
Point(7)  = {r2, 0, 0, h};
Point(8)  = {0, -r2, 0, h};
Point(9)  = {-r2, 0, 0, h};
Point(10) = {-r2, H0, 0, h};

// ---------------- U-shape boundary curves ----------------
// Outer side
Line(1)   = {1, 2};           // outer left vertical
Circle(5) = {2, 11, 3};       // outer left arc
Circle(6) = {3, 11, 4};       // outer right arc
Line(11)  = {4, 5};           // outer right vertical

// Top bridge + inner side
Line(12)  = {5, 6};           // top right thickness
Line(13)  = {6, 7};           // inner right vertical
Circle(8) = {7, 11, 8};       // inner right arc
Circle(9) = {8, 11, 9};       // inner left arc
Line(3)   = {9, 10};          // inner left vertical
Line(4)   = {10, 1};          // top left thickness

// ---------------- Hole 1 (right, upper) ----------------
Point(20) = {c1, yh, 0, h};
Point(21) = {c1+rh, yh, 0, h};
Point(22) = {c1, yh+rh, 0, h};
Point(23) = {c1-rh, yh, 0, h};
Point(24) = {c1, yh-rh, 0, h};

Circle(201) = {21, 20, 22};
Circle(202) = {22, 20, 23};
Circle(203) = {23, 20, 24};
Circle(204) = {24, 20, 21};
Curve Loop(21) = {201,202,203,204};

// ---------------- Hole 2 (left, upper) ----------------
Point(30) = {c2, yh, 0, h};
Point(34) = {c2+rh, yh, 0, h};
Point(35) = {c2, yh+rh, 0, h};
Point(36) = {c2-rh, yh, 0, h};
Point(37) = {c2, yh-rh, 0, h};

Circle(301) = {34, 30, 35};
Circle(302) = {35, 30, 36};
Circle(303) = {36, 30, 37};
Circle(304) = {37, 30, 34};
Curve Loop(31) = {301,302,303,304};

// ---------------- Surface with 2 holes ----------------
Curve Loop(100) = {1, 5, 6, 11, 12, 13, 8, 9, 3, 4};
Plane Surface(100) = {100, 21, 31};

// ---------------- Uniform triangular mesh controls ----------------
Mesh.CharacteristicLengthMin = h;
Mesh.CharacteristicLengthMax = h;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Mesh.Algorithm = 6; // Frontal-Delaunay (2D triangles)

// ---------------- Physical groups (FreeFEM-style numeric labels) ----------------
Physical Curve(101) = {1, 5, 6, 11};          // OUTER
Physical Curve(102) = {13, 8, 9, 3};          // INNER
Physical Curve(103) = {4};                    // LEFT TOP LINE
Physical Curve(104) = {12};                   // RIGHT TOP LINE

Physical Curve(1030) = {301,302,303,304};     // HOLE LEFT
Physical Curve(1040) = {201,202,203,204};     // HOLE RIGHT

Physical Surface(200) = {100};                // DOMAIN

// ---------------- FreeFEM compatibility ----------------
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;

// ---------------- Mesh ----------------
Mesh 2;
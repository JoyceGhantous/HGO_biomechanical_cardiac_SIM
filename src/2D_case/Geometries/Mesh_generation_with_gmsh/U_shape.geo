SetFactory("Built-in");

// ======================================================
// 2D U-shaped domain 
// Uniform triangular mesh
// ======================================================

// ---------- Parameters ----------
h  = 0.01;  
r1 = 1.0;    
r2  = 0.75;
H    = 1;

// ---------- Points ----------
Point(11) = {0, 0, 0, h};   // center of arcs

// Outer boundary
Point(1) = {-r1, H, 0, h};
Point(2) = {-r1, 0, 0, h};
Point(3) = {0, -r1, 0, h};
Point(4) = {r1, 0, 0, h};
Point(5) = {r1, H, 0, h};

// Inner boundary
Point(6)  = {r2, H, 0, h};
Point(7)  = {r2, 0, 0, h};
Point(8)  = {0, -r2, 0, h};
Point(9)  = {-r2, 0, 0, h};
Point(10) = {-r2, H, 0, h};

// ---------- Boundary curves (single closed loop) ----------
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

Curve Loop(100) = {1, 5, 6, 11, 12, 13, 8, 9, 3, 4};
Plane Surface(100) = {100};

// ---------- Uniform triangular meshing controls ----------
Mesh.CharacteristicLengthMin = h;
Mesh.CharacteristicLengthMax = h;

// Disable automatic size changes from curvature / points / boundary extension
Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

// (Optional) choose 2D mesher: 5=Delaunay, 6=Frontal-Delaunay
Mesh.Algorithm = 6;

// No recombination => triangles
// Recombine Surface{...};   <-- DO NOT use

// ---------- Physical groups ----------

Physical Curve(101) = {1, 5, 6, 11};          // OUTER
Physical Curve(102) = {13, 8, 9, 3};          // INNER
Physical Curve(103) = {4};                    // LEFT TOP THICKNESS
Physical Curve(104) = {12};                   // RIGHT TOP THICKNESS

Physical Surface(200) = {100};                // DOMAIN

// ---------- Mesh ----------
Mesh 2;
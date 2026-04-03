// Gmsh .geo generated from the provided FreeFEM script
// Geometry: demi-coquille cylindrique (demi-anneau extrudé suivant z)

SetFactory("Built-in");

// -------------------- Parameters --------------------

R1    = 1.0;    // outer radius
R2    = 0.75;   // inner radius
H     = 2.0;    // cylinder height
h     = 0.05;   // step 

Nz   = Round(H / h);        

// -------------------- 2D --------------------

Point(1) = {-R1,  0,   0, h}; // outer left
Point(2) = { 0,  -R1,  0, h}; // outer bottom
Point(3) = { R1,  0,   0, h}; // outer right

Point(4) = { R2,  0,   0, h}; // inner right
Point(5) = { 0,  -R2,  0, h}; // inner bottom
Point(6) = {-R2,  0,   0, h}; // inner left

Point(7) = { 0,   0,   0, h}; // center

// Outer arc: (-R1,0) -> (R1,0) through the lower half-plane
Circle(1) = {1, 7, 2};
Circle(2) = {2, 7, 3};

// Right segment: (R1,0) -> (R2,0)
Line(3) = {3, 4};

// Inner arc: (R2,0) -> (-R2,0) through the lower half-plane
Circle(4) = {4, 7, 5};
Circle(5) = {5, 7, 6};

// Left segment: (-R2,0) -> (-R1,0)
Line(6) = {6, 1};

// Create the 2D surface
Curve Loop(1) = {1, 2, 3, 4, 5, 6};
Plane Surface(1) = {1};

// -------------------- 3D extrusion --------------------

out[] = Extrude {0, 0, H} {
  Surface{1};
  Layers{Nz};
};

// Uniform target mesh size
Mesh.CharacteristicLengthMin = h;
Mesh.CharacteristicLengthMax = h;


// -------------------- Physical groups --------------------
Physical Surface(20)  = {1};                 // bottom
Physical Surface(10)  = {out[0]};            // top

Physical Surface(101) = {out[2], out[3]};    // outer arc
Physical Surface(104) = {out[4]};            // right
Physical Surface(102) = {out[5], out[6]};    // inner arc
Physical Surface(103) = {out[7]};            // left

Physical Volume(1)    = {out[1]};

// ======================================================
// 3D HALF CUP = x >= 0 half of lower hemispherical shell
// Outer radius r1, inner radius r2 (same as 2D code)
// Uniform tetrahedral mesh 
// ======================================================

SetFactory("OpenCASCADE");

// ---------------- Parameters ----------------
h  = 0.01;   // reference size from 2D code
h3 = 0.03;   // 3D target tet size (use h for very fine mesh, but expensive)

r2 = 0.75;
r1 = 1.0;

L = 5.0;
eps = 1e-6;
tolPick = 0.03;

// ---------------- Geometry ----------------
// Outer and inner spheres
vOuter = newv; Sphere(vOuter) = {0,0,0,r1};
vInner = newv; Sphere(vInner) = {0,0,0,r2};

// Lower half clipping (z <= 0)
vBoxLower1 = newv;
Box(vBoxLower1) = {-L,-L,-L, 2*L,2*L, L};
vOuterLower() = BooleanIntersection{ Volume{vOuter}; Delete; }{ Volume{vBoxLower1}; Delete; };

vBoxLower2 = newv;
Box(vBoxLower2) = {-L,-L,-L, 2*L,2*L, L};
vInnerLower() = BooleanIntersection{ Volume{vInner}; Delete; }{ Volume{vBoxLower2}; Delete; };

// Full lower shell
vCupFull() = BooleanDifference{ Volume{vOuterLower(0)}; Delete; }{ Volume{vInnerLower(0)}; Delete; };

// Half cut (x >= 0)
vBoxHalf = newv;
Box(vBoxHalf) = {0,-L,-L, L,2*L,2*L};

vCupHalf() = BooleanIntersection{ Volume{vCupFull(0)}; Delete; }{ Volume{vBoxHalf}; Delete; };

// ---------------- Uniform tetra mesh controls ----------------
Mesh.CharacteristicLengthMin = h3;
Mesh.CharacteristicLengthMax = h3;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Mesh.Algorithm3D = 1; // Delaunay
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 0; // avoid Netgen-not-compiled error

// ---------------- Physical labels (FreeFEM) ----------------
// DOMAIN volume
Physical Volume(200) = {vCupHalf()};   // DOMAIN

// Probe-based labels
// Outer curved surface probe (x>0, z<0)
xo = 0.6*r1;
yo = 0.2*r1;
zo = -Sqrt(1.0 - 0.6*0.6 - 0.2*0.2)*r1;
sOuter() = Surface In BoundingBox{xo-tolPick, yo-tolPick, zo-tolPick,
                                  xo+tolPick, yo+tolPick, zo+tolPick};

// Inner curved surface probe
xi = 0.6*r2;
yi = 0.2*r2;
zi = -Sqrt(1.0 - 0.6*0.6 - 0.2*0.2)*r2;
sInner() = Surface In BoundingBox{xi-tolPick, yi-tolPick, zi-tolPick,
                                  xi+tolPick, yi+tolPick, zi+tolPick};

// Symmetry plane x = 0
sSym() = Surface In BoundingBox{-eps, -r1-eps, -r1-eps, eps, r1+eps, eps};

// Top opening plane z = 0
sTop() = Surface In BoundingBox{-eps, -r1-eps, -eps, r1+eps, r1+eps, eps};
// The above can catch the symmetry plane intersection if eps too large;
// safer version below (use this one instead):
sTop() = Surface In BoundingBox{0-eps, -r1-eps, -eps, r1+eps, r1+eps, eps};

// FreeFEM-like labels (similar style)
Physical Surface(101) = {sOuter()}; // OUTER
Physical Surface(102) = {sInner()}; // INNER
Physical Surface(103) = {sSym()};   // LEFT / SYMMETRY
Physical Surface(105) = {sTop()};   // TOP CUT / RIM

// Optional all boundary
// sAll() = Boundary{ Volume{vCupHalf(0)}; };
// Physical Surface(199) = {sAll()}; // ALL BOUNDARY

// ---------------- FreeFEM compatibility ----------------
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;

// Generate mesh
Mesh 3;
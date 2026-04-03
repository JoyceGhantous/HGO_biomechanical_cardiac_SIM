// ======================================================
// 3D FULL CUP SYMMETRIC = lower hemispherical shell
// Outer radius r1, inner radius r2 (same as 2D code)
// Uniform tetrahedral mesh 
// ======================================================

SetFactory("OpenCASCADE");

// ---------------- Parameters ----------------
h  = 0.01;   // reference size from 2D code
h3 = 0.03;   // 3D target tet size (use h for very fine mesh, but expensive)

r2 = 0.75;   // inner radius
r1 = 1.0;    // outer radius

L = 5.0;     // big box extent for clipping
eps = 1e-6;

// selection tolerances for labeling surfaces
tolPick = 0.03;   // should be << (r1-r2)=0.25

// ---------------- Geometry ----------------
// Outer sphere
vOuter = newv;
Sphere(vOuter) = {0,0,0,r1};

// Inner sphere
vInner = newv;
Sphere(vInner) = {0,0,0,r2};

// Keep lower half (z <= 0)
vBoxLower1 = newv;
Box(vBoxLower1) = {-L,-L,-L, 2*L,2*L, L}; // z in [-L,0]
vOuterLower() = BooleanIntersection{ Volume{vOuter}; Delete; }{ Volume{vBoxLower1}; Delete; };

vBoxLower2 = newv;
Box(vBoxLower2) = {-L,-L,-L, 2*L,2*L, L};
vInnerLower() = BooleanIntersection{ Volume{vInner}; Delete; }{ Volume{vBoxLower2}; Delete; };

// Shell volume = outer lower half - inner lower half
vCup() = BooleanDifference{ Volume{vOuterLower(0)}; Delete; }{ Volume{vInnerLower(0)}; Delete; };

// ---------------- Uniform tetra mesh controls ----------------
Mesh.CharacteristicLengthMin = h3;
Mesh.CharacteristicLengthMax = h3;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Mesh.Algorithm3D = 1; // Delaunay
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 0; // avoid error if Netgen optimizer not compiled

// ---------------- Physical labels (FreeFEM) ----------------
// DOMAIN volume
Physical Volume(200) = {vCup()};   // DOMAIN

// Surface picking using bounding boxes around probe points
// Outer curved surface probe (point on outer sphere, z<0)
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

// Top opening plane (z = 0)
sTop() = Surface In BoundingBox{-r1-eps, -r1-eps, -eps, r1+eps, r1+eps, eps};

// FreeFEM-like labels (similar style)
Physical Surface(101) = {sOuter()}; // OUTER
Physical Surface(102) = {sInner()}; // INNER
Physical Surface(105) = {sTop()};   // TOP CUT / RIM

// Optional "all boundary" label (comment out if not needed)
// sAll() = Boundary{ Volume{vCup(0)}; };
// Physical Surface(199) = {sAll()}; // ALL BOUNDARY

// ---------------- FreeFEM compatibility ----------------
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;

// Generate mesh
Mesh 3;
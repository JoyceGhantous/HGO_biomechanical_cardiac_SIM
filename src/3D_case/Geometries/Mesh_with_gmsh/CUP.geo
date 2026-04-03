SetFactory("OpenCASCADE");

// ======================================================
// FULL CUP (truncated ellipsoidal shell) + infarct region
// Uniform tetrahedral mesh (quasi-uniform)
// ======================================================

// ---------------- Parameters ----------------
// Geometry
aOut = 18;    // outer ellipsoid x-radius
bOut = 15;    // outer ellipsoid y-radius
cOut = 28;    // outer ellipsoid z-radius

aIn  = 13.5;  // inner ellipsoid x-radius
bIn  = 11.0;  // inner ellipsoid y-radius
cIn  = 24.0;  // inner ellipsoid z-radius

zCut = 10;    // truncate at z = zCut (keep z <= zCut)
L    = 100;   // large box extent for booleans

// Infarct (spherical patch intersecting the wall)
xInf =  9.0;
yInf =  3.5;
zInf = -8.0;
rInf =  6.2;

// Meshing (uniform tetra target size)
h3 = 2.0;     // decrease for finer mesh (e.g. 1.5)

// Keep rotations off by default to preserve robust bbox labels
tiltX = 0*Pi/180;
tiltZ = 0*Pi/180;

eps = 1e-3;

// ---------------- Mesh controls (uniform tetra) ----------------
Mesh.CharacteristicLengthMin = h3;
Mesh.CharacteristicLengthMax = h3;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Mesh.Algorithm3D = 1;   // Delaunay
Mesh.Optimize = 1;

// Do NOT enable Netgen optimizer unless your Gmsh build supports it
Mesh.OptimizeNetgen = 0;

// ======================================================
// 1) Build truncated shell
// ======================================================

// Outer ellipsoid
vOuter = newv;
Sphere(vOuter) = {0, 0, 0, 1};
Dilate {{0,0,0}, {aOut, bOut, cOut}} { Volume{vOuter}; }

// Inner ellipsoid
vInner = newv;
Sphere(vInner) = {0, 0, 0, 1};
Dilate {{0,0,0}, {aIn, bIn, cIn}} { Volume{vInner}; }

// Clip outer by top box (keep z <= zCut)
vTopBox1 = newv;
Box(vTopBox1) = {-L, -L, -L, 2*L, 2*L, zCut + L};
vOutClip() = BooleanIntersection{ Volume{vOuter}; Delete; }{ Volume{vTopBox1}; Delete; };

// Clip inner by top box
vTopBox2 = newv;
Box(vTopBox2) = {-L, -L, -L, 2*L, 2*L, zCut + L};
vInClip() = BooleanIntersection{ Volume{vInner}; Delete; }{ Volume{vTopBox2}; Delete; };

// Shell wall = outer - inner
vWall() = BooleanDifference{ Volume{vOutClip(0)}; Delete; }{ Volume{vInClip(0)}; Delete; };

// ======================================================
// 2) Infarct subregion (keep infarct volume alive!)
// ======================================================
vSph = newv;
Sphere(vSph) = {xInf, yInf, zInf, rInf};

// Intersect sphere with wall -> infarct volume
vInfarct() = BooleanIntersection{ Volume{vWall(0)}; }{ Volume{vSph}; Delete; };

// Healthy wall = wall - infarct
// IMPORTANT: no Delete on vInfarct()
vHealthy() = BooleanDifference{ Volume{vWall(0)}; Delete; }{ Volume{vInfarct()}; };

// ======================================================
// 3) Optional rotation (for visualization only)
// ======================================================
Rotate {{1,0,0}, {0,0,0}, tiltX} { Volume{vHealthy()}; Volume{vInfarct()}; }
Rotate {{0,0,1}, {0,0,0}, tiltZ} { Volume{vHealthy()}; Volume{vInfarct()}; }

// ======================================================
// 4) Physical labels
// ======================================================
Physical Volume("HealthyWall")   = {vHealthy()};
Physical Volume("InfarctRegion") = {vInfarct()};

// All boundary surfaces
sAll() = Boundary{ Volume{vHealthy(0), vInfarct(0)}; };
Physical Surface("AllBoundary") = {sAll()};

// Top cut surface (best with tiltX=tiltZ=0)
sTop() = Surface In BoundingBox{-L, -L, zCut - eps, L, L, zCut + eps};
Physical Surface("TopCut") = {sTop()};

// ======================================================
// 5) Mesh
// ======================================================
Mesh 3;
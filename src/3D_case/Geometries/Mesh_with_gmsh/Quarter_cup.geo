SetFactory("OpenCASCADE");

// ======================================================
// HALF CUP (x >= 0) scaled truncated ellipsoidal shell + infarct
// Uniform-ish tetrahedral mesh + labels
// Scaled to be compatible with 2D dimensions ~ O(1)
// ======================================================

// ---------------- Parameters ----------------
// Geometry (scaled)
aOut = 1.00;
bOut = 0.85;
cOut = 1.45;

aIn  = 0.78;
bIn  = 0.65;
cIn  = 1.20;

// Top cut (keep z <= zCut)
zCut = 0.50;

// Boolean helper box size
L = 5.0;

// Half selection
keepXPositive = 1;

// Infarct (on kept half, intersects shell)
xInf =  0.55;
yInf =  0.18;
zInf = -0.35;
rInf =  0.24;

// Meshing (uniform tetra target size)
h3 = 0.08;

// Keep rotations off for robust bbox labels
tiltX = 0*Pi/180;
tiltZ = 0*Pi/180;

eps = 1e-4;

// ---------------- Mesh controls ----------------
Mesh.CharacteristicLengthMin = h3;
Mesh.CharacteristicLengthMax = h3;

Mesh.MeshSizeFromPoints = 0;
Mesh.MeshSizeFromCurvature = 0;
Mesh.MeshSizeExtendFromBoundary = 0;

Mesh.Algorithm3D = 1;   // Delaunay
Mesh.Optimize = 1;
Mesh.OptimizeNetgen = 0; // avoid Netgen error on builds without Netgen

// ======================================================
// 1) Build full truncated shell
// ======================================================

// Outer ellipsoid
vOuter = newv;
Sphere(vOuter) = {0, 0, 0, 1};
Dilate {{0,0,0}, {aOut, bOut, cOut}} { Volume{vOuter}; }

// Inner ellipsoid
vInner = newv;
Sphere(vInner) = {0, 0, 0, 1};
Dilate {{0,0,0}, {aIn, bIn, cIn}} { Volume{vInner}; }

// Top clipping boxes (keep z <= zCut)
vTopBox1 = newv;
Box(vTopBox1) = {-L, -L, -L, 2*L, 2*L, zCut + L};
vOutClip() = BooleanIntersection{ Volume{vOuter}; Delete; }{ Volume{vTopBox1}; Delete; };

vTopBox2 = newv;
Box(vTopBox2) = {-L, -L, -L, 2*L, 2*L, zCut + L};
vInClip() = BooleanIntersection{ Volume{vInner}; Delete; }{ Volume{vTopBox2}; Delete; };

// Shell wall
vWall() = BooleanDifference{ Volume{vOutClip(0)}; Delete; }{ Volume{vInClip(0)}; Delete; };

// ======================================================
// 2) Infarct region
// ======================================================
vSph = newv;
Sphere(vSph) = {xInf, yInf, zInf, rInf};

// Intersect sphere with wall -> infarct
vInfarct() = BooleanIntersection{ Volume{vWall(0)}; }{ Volume{vSph}; Delete; };

// Healthy wall = wall - infarct (keep infarct alive)
vHealthy() = BooleanDifference{ Volume{vWall(0)}; Delete; }{ Volume{vInfarct()}; };

// ======================================================
// 3) Half cut (x >= 0)
// ======================================================
vHalfBox = newv;
If (keepXPositive)
  Box(vHalfBox) = {0, -L, -L, L, 2*L, 2*L};
Else
  Box(vHalfBox) = {-L, 0, -L, 2*L, L, 2*L};
EndIf

vHealthyHalf() = BooleanIntersection{ Volume{vHealthy(0)}; Delete; }{ Volume{vHalfBox}; };
vInfarctHalf() = BooleanIntersection{ Volume{vInfarct(0)}; Delete; }{ Volume{vHalfBox}; };

// ======================================================
// 4) Optional rotation (for visualization only)
// ======================================================
Rotate {{1,0,0}, {0,0,0}, tiltX} { Volume{vHealthyHalf()}; Volume{vInfarctHalf()}; }
Rotate {{0,0,1}, {0,0,0}, tiltZ} { Volume{vHealthyHalf()}; Volume{vInfarctHalf()}; }

// ======================================================
// 5) Physical labels
// ======================================================
Physical Volume("HealthyWall")   = {vHealthyHalf()};
Physical Volume("InfarctRegion") = {vInfarctHalf()};

// All surfaces
sAll() = Boundary{ Volume{vHealthyHalf(0), vInfarctHalf(0)}; };
Physical Surface("AllBoundary") = {sAll()};

// Symmetry plane
If (keepXPositive)
  sSym() = Surface In BoundingBox{-eps, -L, -L, eps, L, zCut + L};
Else
  sSym() = Surface In BoundingBox{-L, -eps, -L, L, eps, zCut + L};
EndIf
Physical Surface("SymmetryPlane") = {sSym()};

// Top cut
sTop() = Surface In BoundingBox{-L, -L, zCut - eps, L, L, zCut + eps};
Physical Surface("TopCut") = {sTop()};

// Optional FreeFEM compatibility
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;

// ======================================================
// 6) Mesh
// ======================================================
Mesh 3;
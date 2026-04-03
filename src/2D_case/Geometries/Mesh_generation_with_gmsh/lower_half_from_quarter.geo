// ============================================================
// PARAMETERS
// ============================================================
h   = 0.01;
r1  = 1.0;
r2  = 0.85;
c1  = r2 + (r1 - r2) * 0.5;
rh  = 0.01;
yh  = -0.10;
p   = 0.3;

// ============================================================
// DERIVED GEOMETRY
// ============================================================
demi_angle = (p / 100.0) * 180.0 / 2.0;
angleB     = (-90.0 + demi_angle) * 3.14159265358979 / 180.0;
xB         = r2 * Cos(angleB);
yB         = r2 * Sin(angleB);

// ============================================================
// POINTS
// ============================================================
Point(1) = {0,    0,   0, h};   // centre O = (0,0,0)
Point(3) = {0,   -r1,  0, h};   // outer bottom (-90 deg)
Point(6) = {0,   -r2,  0, h};   // inner bottom (-90 deg)
Point(2) = {r1,   0,   0, h};   // outer right  (0 deg)
Point(5) = {r2,   0,   0, h};   // inner right  (0 deg)
Point(9) = {xB,  yB,   0, h};   // right boundary of segment 105 with a chosen angle via the percentage p 

// ============================================================
// CURVES — RIGHT HALF
// ============================================================
Circle(2)  = {2, 1, 3};   // outer arc
Line(10)   = {3, 6};      // Y-axis cut (shared after symmetry)
Circle(40) = {6, 1, 9};   // inner small arc (segment %)
Circle(4)  = {9, 1, 5};   // inner big arc
Line(31)   = {5, 2};      // top horizontal cut (y=0)

// ============================================================
// HOLE — RIGHT
// ============================================================
Point(20) = {c1,      yh,      0, h};
Point(21) = {c1+rh,   yh,      0, h};
Point(22) = {c1,      yh+rh,   0, h};
Point(23) = {c1-rh,   yh,      0, h};
Point(24) = {c1,      yh-rh,   0, h};
Circle(201) = {21, 20, 22};
Circle(202) = {22, 20, 23};
Circle(203) = {23, 20, 24};
Circle(204) = {24, 20, 21};

// ============================================================
// SURFACES
// ============================================================
Curve Loop(21) = {201, 202, 203, 204};
Curve Loop(11) = {2, 10, 40, 4, 31};
Plane Surface(11) = {11, 21};

// ============================================================
// SYMMETRY + EXACT MIRRORED MESH
// ============================================================
left[] = Symmetry {1, 0, 0, 0} { Duplicata{ Surface{11}; } };
ReverseMesh Surface{11};

Coherence;
Periodic Surface {left[0]} = {11} Affine
{-1, 0, 0, 0,
  0, 1, 0, 0,
  0, 0, 1, 0};


// ============================================================
// PHYSICAL GROUPS - LABELS FOR FREEFEM++
// ============================================================
Physical Curve(101)  = {2, 4, 31};              // bord droit
Physical Curve(102)  = {206, 209, 210};         // bord gauche
Physical Curve(103)  = {10};                    // axe Y partagé
Physical Curve(105)  = {40};                    // segment % droit
Physical Curve(106)  = {208};                   // segment % gauche
Physical Curve(1040) = {201, 202, 203, 204};    // trou droit
Physical Curve(1030) = {211, 212, 213, 214};    // trou gauche

Physical Surface(1000) = {11, left[0]};         // domaine complet

// ============================================================
// MESH SETTINGS
// ============================================================
Mesh 2;                     // Lance la génération du maillage en 2 dimensions
Mesh.ElementOrder   = 1;    // Définit l'ordre des éléments du maillage
Mesh.MshFileVersion = 2.2;  // Fixe la version du format de fichier .msh utilisée lors de l'export
Mesh.SaveAll        = 0;    // Contrôle quels éléments sont sauvegardés dans le fichier .msh :
                            // 0 → seuls les éléments appartenant à des entités physiques

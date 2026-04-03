// This gmsh code generates a mesh for the lower half of a ring,
// with an inner radius of 0.75 and an outer radius of 1.0.
// The mesh includes 2 holes of :
//  - 0.04 diameter,
//  - centered at ( 0.875, -0.10) -> for the Right hole (1040)
//  - centered at (-0.875, -0.10) -> for the Left hole  (1030)
// A small 5% segment of the inner arc is labeled 105 (centered at bottom)

h = 0.01;
r2 = 0.85;
r1 = 1.0;
c1 = r2 + (r1-r2)*0.5;   // 0.875
c2 = -c1;
// trous
rh = 0.02;
yh = -0.10;

// 5% of inner arc = 5% of 180deg = 9deg = 0.05*Pi rad
// centered at -90deg (bottom of inner arc)
// so from -94.5deg to -85.5deg
// in radians: -94.5 * Pi/180 and -85.5 * Pi/180

angleA = -94.5 * 3.14159265358979 / 180.0;  // start of 105 segment
angleB = -85.5 * 3.14159265358979 / 180.0;  // end   of 105 segment

xA = r2 * Cos(angleA);   // point at -94.5 deg on inner arc
yA = r2 * Sin(angleA);

xB = r2 * Cos(angleB);   // point at -85.5 deg on inner arc
yB = r2 * Sin(angleB);

// centre
Point(1) = {0, 0, 0, h};

// outer boundary points (lower half)
Point(2) = { r1, 0, 0, h};
Point(3) = { 0,-r1, 0, h};
Point(4) = {-r1, 0, 0, h};

// inner boundary points (lower half)
Point(5) = { r2, 0, 0, h};
Point(6) = { 0,-r2, 0, h};   // bottom of inner arc
Point(7) = {-r2, 0, 0, h};

// Two new points splitting the inner arc for the 105 label
Point(8)  = {xA, yA, 0, h};  // -94.5 deg  (left boundary of 105 segment)
Point(9)  = {xB, yB, 0, h};  // -85.5 deg  (right boundary of 105 segment)

// outer arc
Circle(1) = {4, 1, 3};
Circle(2) = {3, 1, 2};

// right cut segment
Line(31) = {2, 5};

// inner arc — now split into 3 parts:
//   Circle(4)  : from Point(5) to Point(9)   [right portion, ~85.5 deg]
//   Circle(40) : from Point(9) to Point(8)   [5% middle segment -> label 105]
//   Circle(41) : from Point(8) to Point(7)   [left portion, ~85.5 deg]
Circle(4)  = {5, 1, 9};
Circle(40) = {9, 1, 8};
Circle(41) = {8, 1, 7};

// left cut segment
Line(61) = {7, 4};

// ===== trou droit =====
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

// ===== trou gauche =====
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

// surface avec trous
// Note: inner arc now uses 4, 40, 41 instead of 4, 5
Curve Loop(10) = {1, 2, 31, 4, 40, 41, 61};
Plane Surface(11) = {10, 21, 31};

// physicals pour FreeFEM
Physical Curve(101) = {1, 2};              // OUTER
Physical Curve(102) = {4, 41};            // INNER (excluding 105 segment)
Physical Curve(105) = {40};               // INNER 5% segment (bottom center)
Physical Curve(103) = {61};               // LEFT
Physical Curve(104) = {31};               // RIGHT
Physical Curve(1030) = {301,302,303,304}; // HOLE LEFT
Physical Curve(1040) = {201,202,203,204}; // HOLE RIGHT
Physical Surface(200) = {11};             // DOMAIN

// compat FreeFEM
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;
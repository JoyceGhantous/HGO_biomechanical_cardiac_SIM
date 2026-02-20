h = 0.01;

r2 = 0.75;
r1 = 1.0;

c1 = r2 + (r1-r2)*0.5;   // 0.875
c2 = -c1;

// trous
rh = 0.02;
yh = -0.10;

// centre
Point(1) = {0, 0, 0, h};

// outer boundary points (lower half)
Point(2) = { r1, 0, 0, h};
Point(3) = { 0,-r1, 0, h};
Point(4) = {-r1, 0, 0, h};

// inner boundary points (lower half)
Point(5) = { r2, 0, 0, h};
Point(6) = { 0,-r2, 0, h};
Point(7) = {-r2, 0, 0, h};

// outer arc
Circle(1) = {4, 1, 3};
Circle(2) = {3, 1, 2};

// right cut segment
Line(31) = {2, 5};

// inner arc
Circle(4) = {5, 1, 6};
Circle(5) = {6, 1, 7};

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
Curve Loop(10) = {1,2,31,4,5,61};
Plane Surface(11) = {10,21,31};

// physicals pour FreeFEM
Physical Curve(101) = {1,2};        // OUTER
Physical Curve(102) = {4,5};        // INNER
Physical Curve(103) = {61};         // LEFT
Physical Curve(104) = {31};         // RIGHT
Physical Curve(105) = {201,202,203,204}; // HOLE RIGHT
Physical Curve(106) = {301,302,303,304}; // HOLE LEFT
Physical Surface(200) = {11};       // DOMAIN

// compat FreeFEM
Mesh.ElementOrder = 1;
Mesh.MshFileVersion = 2.2;
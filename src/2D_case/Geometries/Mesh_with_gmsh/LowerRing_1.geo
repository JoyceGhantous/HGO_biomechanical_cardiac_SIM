h = 0.01;    // mesh size 
r2 = 0.75;     // inner radius
r1 = 1.0;     // outer radius

// center
Point(1) = {0, 0, 0, h};      

// outer boundary points (lower half)
Point(2) = { r1, 0, 0, h};    // outer right
Point(3) = { 0,-r1, 0, h};    // outer bottom
Point(4) = {-r1, 0, 0, h};    // outer left

// inner boundary points (lower half)
Point(5) = { r2, 0, 0, h};    // inner right
Point(6) = { 0,-r2, 0, h};    // inner bottom
Point(7) = {-r2, 0, 0, h};    // inner left

// Outer arc
Circle(1) = {4, 1, 3};        
Circle(2) = {3, 1, 2};         

// Right segment
Line(3) = {2, 5};  

// Inner arc 
Circle(4) = {5, 1, 6};        
Circle(5) = {6, 1, 7};    

// Left segment
Line(6) = {7, 4};  

// Surface
Curve Loop(10) = {1, 2, 3, 4, 5, 6};
Plane Surface(11) = {10};


//  labels in FreeFEM via gmshload
Physical Curve(101) = {1, 2};  // OUTER 
Physical Curve(102) = {4, 5};  // INNER 
Physical Curve(103) = {6};     // LEFT 
Physical Curve(104) = {3};     // RIGHT 

Physical Surface(200) = {11};  // DOMAIN

h = 0.01;    // mesh size 

r2 = 0.75;     // inner radius
r1 = 1.0;     // outer radius

eps = (r1-r2)*0.05;
c1 = r2+(r1-r2)*0.5;
c2 = -c1;

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

Point(8) = {c1+eps, 0, 0, h};    // right
Point(9) = {c1-eps, 0, 0, h};    // left

Point(10) = {c2+eps, 0, 0, h};    // right
Point(11) = {c2-eps, 0, 0, h};    // left


// Outer arc
Circle(1) = {4, 1, 3};        
Circle(2) = {3, 1, 2};         

// Right segment
Line(31) = {2, 8};  
Line(32) = {8, 9};  
Line(33) = {9, 5};  

// Inner arc 
Circle(4) = {5, 1, 6};        
Circle(5) = {6, 1, 7};    

// Left segment
Line(61) = {7, 10}; 
Line(62) = {10, 11}; 
Line(63) = {11, 4};  

// Surface
Curve Loop(10) = {1, 2, 31, 32, 33, 4, 5, 61, 62, 63};
Plane Surface(11) = {10};


//  labels in FreeFEM via gmshload
Physical Curve(101) = {1, 2};  // OUTER 
Physical Curve(102) = {4, 5};  // INNER 
Physical Curve(103) = {61, 63};  // LEFT 
Physical Curve(104) = {31, 33};  // RIGHT 

Physical Curve(1030) = {62};  // LEFT 
Physical Curve(1040) = {32};  // RIGHT 

Physical Surface(200) = {11};  // DOMAIN

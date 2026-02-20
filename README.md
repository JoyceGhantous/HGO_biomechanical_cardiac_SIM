# __HGO_biomechanical_cardiac_SIM__

**Author :** Joyce Ghantous  
**Date :**  2026    
**Version :** 1.0  

This is **FreeFEM++** code to simulate a **transversely isotropic hyperelastic** material (HGO-type behavior along the fiber direction).   

# __🎯 Objective__ 

The objective is to register cardiac data by transferring information (e.g., myocardial fiber directions) from MRI images to optical mapping images.    

This is done by modeling the heart tissue as a quasi-incompressible, transversely isotropic hyperelastic material and computing the displacement field u. This way we get a transformation phi(x) = x + u(x) that best maps the heart from its MRI resting configuration to its stretched/flattened optical-mapping configuration by minimizing the system’s total mechanical energy.   

### 📥 Install Freefem++ and run the Project :

First, you need to install :
- [FreeFEM](https://freefem.org) v4.15
  
To run the code, you need to choose a geometry and a force distribution:  

- `Resolution_2d_LR2.edp`: Dirichlet boundary condition on the left side of a half lower ring, and a Neumann load \((g_1,g_2)\) on the right side.  
- `Resolution_2d_LR2_OPPforces.edp`: same geometry, with opposite forces \((-g,0)\) on the left and \((g,0)\) on the right.  
- `Resolution_2d_LR3_OPPforces_on_Circles.edp`: same geometry, with opposite forces \((-g,0)\) applied on a small disk on the left and \((g,0)\) applied on a small disk on the right.  

The last case is closer to the experimental setup: wires are inserted into the heart and exit through small holes on each side.  
The wires then stretch the heart and position it for optical mapping imaging.   

    
```bash
  FreeFem++ Resolution_2d.edp <case_id>
```
where <case_id> is the number identifying the parameter set for this test case.   
You can choose a case number from 0 to 17. In addition, selecting 2009 or 2025 loads parameter sets taken from other biomedical articles.



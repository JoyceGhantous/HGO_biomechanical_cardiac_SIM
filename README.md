# __HGO_biomechanical_cardiac_SIM__

**Author :** Joyce Ghantous  
**Date :**  2026    
**Version :** 1.0  

This is **FreeFEM++** code to simulate a **transversely isotropic hyperelastic** material (HGO-type behavior along the fiber direction).   

# __🎯 Objective__ 

The objective is to register cardiac data by transferring information (e.g., myocardial fiber directions) from MRI images to optical mapping images.    
This is done by modeling the heart tissue as a quasi-incompressible, transversely isotropic hyperelastic material and computing the displacement field u.     
This way we get a transformation phi(x) = x + u(x) that best maps the heart from its MRI resting configuration to its stretched/flattened optical-mapping configuration by minimizing the system’s total mechanical energy.   

### 📥 Install Freefem++ and run the Project :

To run the simulation, you need to install :
- [FreeFEM](https://freefem.org) v4.15

Run:
  ```bash
  FreeFem++ Resolution_2d.edp



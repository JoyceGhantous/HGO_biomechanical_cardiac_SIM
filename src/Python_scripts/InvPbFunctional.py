import numpy as npc
from src.Python_scripts.run_command import runCommand

def compute_weights(target_vals, p):

    wi = np.abs(target_vals)**p
    return wi / np.sum(wi)

def objective(g, case, target_vals, weights, nb_proc,  verbosity=0):
    '''
        Compute the regularised objective function for the inverse problem.
        
        The objective function is defined as:
            J(g) = sum_i w_i * (x_i - target_vals_i)^2
            
        where:
            - x_i are the values obtained from FreeFEM for a given g
            - target_vals_i are the reference values obtained from FreeFEM for g_ref
            - w_i are the weights for the discrete weighted L2 norm    
    '''
    g = float(np.ravel(g)[0])
    t0 = time.perf_counter()

    out, vals_g, err, returncode = runCommand(
        f"ff-mpirun -np {nb_proc} Resolution_2d_MPI.edp -bcF {g} -case {case} -Inv 1 -ffddm_partitioner 2 -ffddm_overlap 1",
        verbose=False,
        stopOnFail=False
    )


    vals_g = np.asarray(vals_g, dtype=float)

    diff = vals_g - target_vals
    misfit = np.sum(weights * diff**2) 

    elapsed = time.perf_counter() - t0
    minutes, seconds = divmod(elapsed, 60)

    if verbosity > 0 :
        log = str(out) + "\n" + str(err)
        if "Line-search failed" in log:
            reason = "failure: line search failed"
        elif "converged" in log.lower():
            reason = "success: Newton converged"
        elif returncode != 0:
            reason = f"failure: FreeFEM returned code {returncode}"
        else:
            reason = "unknown stopping reason"
        print(
            f"g={g:.16g}, "
            f"cost function={misfit:.16e}, "
            f"Final Newton stopping reason: {reason}, "
            f"FF time = {minutes} min {seconds:.3f} s"
        )
    else :
        print(
                f"g={g:.16g}, "
                f"cost function={misfit:.16e}, "
                f"FF time = {minutes} min {seconds:.3f} s"
            )

    return misfit


# 

def objective_pixel_index(g, case, target_vals, weights, nb_proc, L, n_pixels=256, verbosity=0):
    """
        Objective function based on pixel indices : 
            J(g) = sum_i w_i * (P(x_i(g)) - P(x_i^target))^2
        where:
            P(x) = floor(x / dx)
            dx = L / n_pixels
    """
    g = float(np.ravel(g)[0])
    t0 = time.perf_counter()

    out, vals_g, err, returncode = runCommand(
        f"ff-mpirun -np {nb_proc} Resolution_2d_MPI.edp -bcF {g} -case {case} -Inv 1 -ffddm_partitioner 2 -ffddm_overlap 1",
        verbose=False,
        stopOnFail=False
    )

    dx = L / n_pixels

    vals_g = np.asarray(vals_g, dtype=float)
    pixel_g = np.floor(vals_g / dx)

    target_vals = np.asarray(target_vals, dtype=float)   
    pixel_target = np.floor(target_vals / dx)

    diff = pixel_g - pixel_target
    misfit = np.sum(weights * diff**2)

    elapsed = time.perf_counter() - t0
    minutes, seconds = divmod(elapsed, 60)

    if verbosity > 0:
        log = str(out) + "\n" + str(err)
        if "Line-search failed" in log:
            reason = "failure: line search failed"
        elif "converged" in log.lower():
            reason = "success: Newton converged"
        elif returncode != 0:
            reason = f"failure: FreeFEM returned code {returncode}"
        else:
            reason = "unknown stopping reason"

        print(
            f"g={g:.16g}, "
            f"cost function={misfit:.16e}, "
            f"Final Newton stopping reason: {reason}, "
            f"FF time = {minutes} min {seconds:.3f} s"
        )
    else:
        print(
            f"g={g:.16g}, "
            f"cost function={misfit:.16e}, "
            f"FF time = {minutes} min {seconds:.3f} s"
        )

    return misfit

# 

def objective_distance_to_pixel(g, case, target_vals, weights, nb_proc, L, n_pixels=256, verbosity=0):
    """
        Objective function based on the distance to the target pixel.

        The target pixel associated with x_i^target is the interval:
            [x_i^target - dx/2, x_i^target + dx/2]
        The contribution is zero if x_i(g) lies inside this interval.

        We consider :  
            J(g) = sum_i w_i * dist(x_i(g), pixel_i)^2
    """
    g = float(np.ravel(g)[0])
    t0 = time.perf_counter()

    out, vals_g, err, returncode = runCommand(
        f"ff-mpirun -np {nb_proc} Resolution_2d_MPI.edp -bcF {g} -case {case} -Inv 1 -ffddm_partitioner 2 -ffddm_overlap 1",
        verbose=False,
        stopOnFail=False
    )

    vals_g = np.asarray(vals_g, dtype=float)
    target_vals = np.asarray(target_vals, dtype=float)
    weights = np.asarray(weights, dtype=float)

    dx = L / n_pixels

    lower = target_vals - dx / 2
    upper = target_vals + dx / 2

    dist = np.maximum(0.0, np.maximum(lower - vals_g, vals_g - upper))

    misfit = np.sum(weights * dist**2)

    elapsed = time.perf_counter() - t0
    minutes, seconds = divmod(elapsed, 60)

    if verbosity > 0:
        log = str(out) + "\n" + str(err)
        if "Line-search failed" in log:
            reason = "failure: line search failed"
        elif "converged" in log.lower():
            reason = "success: Newton converged"
        elif returncode != 0:
            reason = f"failure: FreeFEM returned code {returncode}"
        else:
            reason = "unknown stopping reason"

        print(
            f"g={g:.16g}, "
            f"cost function={misfit:.16e}, "
            f"Final Newton stopping reason: {reason}, "
            f"FF time = {minutes} min {seconds:.3f} s"
        )
    else:
        print(
            f"g={g:.16g}, "
            f"cost function={misfit:.16e}, "
            f"FF time = {minutes} min {seconds:.3f} s"
        )

    return misfit
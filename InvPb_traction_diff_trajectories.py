"""
    This script does three things:
    - it runs a FreeFEM script,
    - it extracts the numeric values printed by that script,
    - it solves a small optimization problem in Python using those values as a target.

    To run this code : 
        uv run python InvPb_traction.py  
"""

import time
import numpy as np
import scipy.optimize as opt
import argparse

from src.Python_scripts.run_command import runCommand
import src.Python_scripts.InPb_post_treatment as post_treatment
from src.Python_scripts.InvPbFunctional import compute_weights, objective
from src.Python_scripts.InvPb_functions import make_history, make_callback

# --------------------------------------------------------------------------

LBFGSB_OPTIONS = {
    "ftol": 1e-6,
    "gtol": 1e-5,
    "maxls": 20,
    "maxiter": 100,
    "maxfun": 200,
    "finite_diff_rel_step": 1e-3,
}

BOUNDS = [(0.0, 3.0)]


# ---------------------------------------------------------------------------

def run_single_lbfgsb(initial_guess, case, target_vals, weights, nb_proc):
    history    = make_history()
    iter_count = [0]
    
    cost_0 = objective(np.array([initial_guess]), case, target_vals, weights, nb_proc)
    history["iteration"].append(0)
    history["g"].append(float(initial_guess))
    history["cost"].append(float(cost_0))

    callback = make_callback(history, iter_count)

    result = opt.minimize(
        objective,
        x0=np.array([initial_guess]),
        bounds=BOUNDS,
        args=(case, target_vals, weights, nb_proc),
        method="L-BFGS-B",
        jac="2-point",
        callback=callback,
        options=LBFGSB_OPTIONS,
    )

    g_final   = float(result.x[0])
    cost_final = float(result.fun)
    if not history["g"] or history["g"][-1] != g_final:
        history["iteration"].append(iter_count[0] + 1)
        history["g"].append(g_final)
        history["cost"].append(cost_final)

    return result, history

# --------------------------------------------------------------------------

def main():
    t0 = time.perf_counter()
    parser = argparse.ArgumentParser()
    parser.add_argument("--np", type=int, required=True)
    args = parser.parse_args()

    # --------------------------------------------------------------------------------------------

    p = 1
    case = 0
    g_ref = 1 
    g0_list = [0.1, 0.5, 1.5, 2.]
    Lx = 2.0

    # case = 2
    # g_ref = 2 
    # g0_list = [0.2, 0.5, 1., 1.5, 2.9]
    # Lx = 10

    # --------------------------------------------------------------------------------------------

    print("\nComputing the reference values from FreeFEM\n")
    out, exact_vals, err, returncode = runCommand(
        f"ff-mpirun -np {args.np} Resolution_2d_MPI.edp "
        f"-bcF {g_ref} -case {case} -Inv 1 -ffddm_partitioner 2 -ffddm_overlap 1",
        verbose=False,
        stopOnFail=False,
    )

    exact_vals = np.asarray(exact_vals, dtype=float)
    print(f"Exact values : {exact_vals}\n")

    Measure_error = np.random.uniform(-Lx/512,  Lx/512, size=exact_vals.shape)
    print(f"Measurement errors : {Measure_error}\n")

    target_vals = exact_vals + Measure_error
    print(f"Reference values : {target_vals}\n")

    weights     = compute_weights(target_vals, p)
    print(f"Weights          : {weights}\n")

    # --------------------------------------------------------------------------------------------

    all_histories = []
    all_results   = []

    for g0 in g0_list:
        print(f"\n{'='*60}")
        print(f"  Optimisation avec g0 = {g0}")
        print(f"{'='*60}\n")
        result, history = run_single_lbfgsb(g0, case, target_vals, weights, args.np)
        all_histories.append(history)
        all_results.append(result)
        post_treatment.print_optimization_summary(result, t0)

    # ---- sorties combinées ----
    post_treatment.plot_all_histories(all_histories, g0_list, output_dir=".")
    post_treatment.save_combined_csv(all_histories, g0_list, all_results, output_dir=".")

# --------------------------------------------------------------------------

if __name__ == "__main__":
    main()
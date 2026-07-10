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
    "ftol": 1e-5,
    "gtol": 1e-5,
    "maxls": 20,
    "maxiter": 100,
    "maxfun": 200,
    "finite_diff_rel_step": 1e-3,
}

# ---------------------------------------------------------------------------

def run_lBFGsb(initial_guess, case, target_vals, weights, BOUNDS, nb_proc, t0):
    """
        Lance l'optimisation pour un seul g0.
    """
    history    = make_history()
    iter_count = [0]
    callback   = make_callback(history, iter_count)

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

    post_treatment.print_optimization_summary(result, t0)
    post_treatment.save_history_and_plot(history, output_dir=".", prefix=f"InvPb_traction_g0_{initial_guess}", show_plot=True,)

def run_scalar(case, target_vals, weights, BOUNDS, nb_proc, t0):
    """
        minimize_scalar (méthode bornée).
    """
    t0 = time.perf_counter()
    history    = make_history()

    def f_scalar(g_val):
        g = np.array([g_val])
        cost = objective(g, case, target_vals, weights, nb_proc)

        history["iteration"].append(len(history["iteration"]) + 1)
        history["g"].append(float(g_val))
        history["cost"].append(float(cost))

        return cost

    result = opt.minimize_scalar(
        f_scalar,
        bounds=BOUNDS[0],
        method="bounded",
        options={"disp": 3, "xatol": 1e-4, "maxiter": 20},
    )

    post_treatment.print_optimization_summary(result, t0)
    post_treatment.save_history_and_plot(history, output_dir=".", prefix="InvPb_traction", show_plot=True,)


# --------------------------------------------------------------------------

def main():
    t0     = time.perf_counter()

    # --------------------------------------------------------------------------------------------

    parser = argparse.ArgumentParser()

    parser.add_argument("--case", type=int, required=True)
    parser.add_argument("--g_ref", type=float, required=True)
    parser.add_argument("--p", type=int, required=True)
    parser.add_argument("--np", type=int, required=True)
    parser.add_argument("--use_lbfgsb", type=str, choices=["y", "n"], required=True, help="Use L-BFGS-B method ? y/n")
    parser.add_argument("--g0", type=float, required=True)
    args = parser.parse_args()

    print("case =", args.case)
    print("g_ref =", args.g_ref)
    print("p =", args.p)
    print("np =", args.np)
    print("use_lbfgsb =", args.use_lbfgsb)
    if  args.use_lbfgsb =="y" :  
        print("g0 =", args.g0)

    if args.p < 0:
        raise ValueError("p must be >= 0")
    if args.np <= 0:
        raise ValueError("np must be strictly positive")

    BOUNDS = [(0.0, 3.0)]
    if args.case == 1 :
        BOUNDS = [(0.0, 300.)]
    
    Lx = 10
    if args.case == 0 :
        Lx = 1.0

    # --------------------------------------------------------------------------------------------

    print("\nComputing the reference values from FreeFEM\n")
    out, exact_vals, err, returncode = runCommand(
        f"ff-mpirun -np {args.np} Resolution_2d_MPI.edp "
        f"-bcF {args.g_ref} -case {args.case} -Inv 1 -ffddm_partitioner 2 -ffddm_overlap 1",
        verbose=False,
        stopOnFail=False,
    )

    exact_vals = np.asarray(exact_vals, dtype=float)
    print(f"Exact values : {exact_vals}\n")

    Measure_error = np.random.uniform(-Lx/512,  Lx/512, size=exact_vals.shape)
    print(f"Measurement errors : {Measure_error}\n")

    target_vals = exact_vals + Measure_error
    print(f"Reference values : {target_vals}\n")

    weights     = compute_weights(target_vals, args.p)
    print(f"Weights          : {weights}\n")

    print(f"Functional with noise : {objective(args.g_ref, args.case, target_vals, weights, args.np, verbosity=0)}\n")
    

    # --------------------------------------------------------------------------------------------

    print("Minimizing the objective function with respect to g\n")
    if args.use_lbfgsb =="y":
        run_lBFGsb(args.g0, args.case, target_vals, weights, BOUNDS, args.np, t0)
    else:
        run_scalar(args.case, target_vals, weights, BOUNDS, args.np, t0)

if __name__ == "__main__":
    main()
from pathlib import Path
import os
import time
import numpy as np
import csv
import matplotlib.cm as cm
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams.update({
    "text.usetex": False,

    "font.family": "serif",
    "font.serif": ["DejaVu Serif"],

    "mathtext.fontset": "stix",
    "font.size": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "legend.title_fontsize": 14,
})

def print_optimization_summary(result, t0):
    """Displays the optimization summary."""
    g_opt = float(np.atleast_1d(result.x)[0])

    print(" ")
    print("Success:", result.success)
    print("g*:", g_opt)
    print("J(g*):", result.fun)
    print("Iterations:", result.nit)
    print("Function evaluations:", result.nfev)
    print("Message:", result.message)

    print(" ")
    temps = time.perf_counter() - t0
    minutes, seconds = divmod(temps, 60)
    print(f"--------- Total time : {minutes} min {seconds:.2f} s ------------ \n")


def save_history_and_plot(history, output_dir=".", prefix="InvPb", show_plot=True):

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_path               = output_dir / f"{prefix}.txt"
    cost_png_path          = output_dir / f"{prefix}_cost.png"
    g_png_path             = output_dir / f"{prefix}_g.png"
    cost_loglog_png_path   = output_dir / f"{prefix}_cost_loglog.png"

    iteration = np.asarray(history["iteration"])
    g_save    = np.asarray(history["g"])
    cost_save = np.asarray(history["cost"])

    history_array = np.column_stack((iteration, g_save, cost_save))

    np.savetxt(
        txt_path,
        history_array,
        header="iteration g cost",
        fmt=["%d", "%.12f", "%.12f"],
    )
    print(f"Saved in: {txt_path}")

    # -------------------------------------------------------------------
    # Plot cost vs iteration
    # -------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(iteration, cost_save, marker="o", linewidth=1.5, markersize=3, label="Cost function")
    ax.set_xlabel(r"iterations")
    ax.set_ylabel(r"Functional $\mathrm{F(g)}$")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(cost_png_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close(fig)
    print(f"Figure saved in : {cost_png_path}")

    # -------------------------------------------------------------------
    # Plot g vs iteration
    # -------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(iteration, g_save, marker="o", linewidth=1.5, markersize=3, label="Minimizer")
    ax.set_xlabel(r"iterations")
    ax.set_ylabel(r"Force $\mathrm{g}$")
    ax.grid(True)
    fig.tight_layout()
    fig.savefig(g_png_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close(fig)
    print(f"Figure saved in : {g_png_path}")

    # -------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(5, 5))
    
    mask = (
        np.isfinite(iteration)
        & np.isfinite(cost_save)
        & (cost_save > 0)
    )
    
    if np.any(mask):
        ax.semilogy(iteration[mask], cost_save[mask], marker="o", linewidth=1.5, markersize=3, label="Cost function")
        ax.set_xlabel(r"iterations")
        ax.set_ylabel(r"Functional $\mathrm{F(g)}$")
        ax.grid(True)
        ax.legend()
    else:
        print(
            "Warning: cannot plot the cost on a semilogarithmic scale "
            "because there are no strictly positive cost values."
        )
    
    fig.tight_layout()
    fig.savefig(cost_loglog_png_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close(fig)
    print(f"Figure semi-log saved in : {cost_loglog_png_path}")

    # -------------------------------------------------------------------

    fig_paths = {
        "cost":       cost_png_path,
        "g":          g_png_path,
        "cost_loglog": cost_loglog_png_path,
    }

    return txt_path, fig_paths


def plot_all_functionals(histories, output_dir=".", output_file="InvPb_traction_all_functionals.png", show_plot=True):

    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(5, 5))

    for h in histories:
        cost = np.asarray(h["cost"], dtype=float)
        x    = h["iteration"] if len(h["iteration"]) == len(cost) else np.arange(len(cost))

        ax.plot(x, cost, marker="o", linewidth=1.5, markersize=3, label=f"g0={h['g0']:.2f}, g*={h['g_opt']:.6f}")

    ax.set_xlabel(r"iterations")
    ax.set_ylabel(r"Functional $\mathrm{F(g)}$")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()

    save_path = output_dir / output_file
    fig.savefig(save_path, dpi=180)
    if show_plot:
        plt.show()
    plt.close(fig)
    print(f"Figure all functionals saved in : {save_path}")


# ---------------------------------------------------------------------------

def plot_all_histories(all_histories: list[dict], g0_list: list[float], output_dir: str = "."):
    colors = cm.tab10(np.linspace(0, 1, len(g0_list)))

    fig_cost, ax_cost = plt.subplots(figsize=(5, 5))

    for hist, g0, color in zip(all_histories, g0_list, colors):
        iters = hist["iteration"]
        label = rf"$\mathrm{{g_0}} = {g0:.4g}$"

        ax_cost.semilogy(
            iters,
            hist["cost"],
            marker="o",
            markersize=3,
            linewidth=1.5,
            color=color,
            label=label
        )

    ax_cost.set_xlabel(r"iterations")
    ax_cost.set_ylabel(r"Functional $\mathrm{F(g)}$")
    ax_cost.grid(True)
    ax_cost.legend(fontsize=10, frameon=True)

    cost_path = os.path.join(output_dir, "InvPb_traction_multi_g0_cost.png")
    fig_cost.savefig(cost_path, dpi=180)
    print(f"\n Cost function plot saved in : {cost_path}")

    fig_g, ax_g = plt.subplots(figsize=(5, 5))

    for hist, g0, color in zip(all_histories, g0_list, colors):
        iters = hist["iteration"]
        label = rf"$\mathrm{{g_0}} = {g0:.4g}$"

        ax_g.plot(
            iters,
            hist["g"],
            marker="s",
            markersize=3,
            linewidth=1.5,
            color=color,
            label=label
        )

    ax_g.set_xlabel(r"iterations")
    ax_g.set_ylabel(r"Force $\mathrm{g}$")
    ax_g.grid(True)
    ax_g.legend(fontsize=10, frameon=True)

    g_path = os.path.join(output_dir, "InvPb_traction_multi_g0_g.png")
    fig_g.savefig(g_path, dpi=180)
    print(f"Plot of g values saved in : {g_path}")

    plt.show()

def save_combined_csv(all_histories: list[dict], g0_list: list[float],
                      all_results, output_dir: str = "."):
    csv_path = f"{output_dir}/InvPb_traction_multi_g0.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["g0", "iteration", "g", "cost"])
        for hist, g0 in zip(all_histories, g0_list):
            for it, g_val, cost in zip(hist["iteration"], hist["g"], hist["cost"]):
                writer.writerow([g0, it, g_val, cost])

        writer.writerow([])
        writer.writerow(["# RÉSUMÉ FINAL"])
        writer.writerow(["g0", "g_opt", "cost_final", "success", "message"])
        for res, g0 in zip(all_results, g0_list):
            g_opt = float(res.x[0]) if hasattr(res.x, "__len__") else float(res.x)
            writer.writerow([g0, g_opt, res.fun, res.success,
                             res.message.replace(",", ";")])

    print(f"CSV saved in  : {csv_path}")

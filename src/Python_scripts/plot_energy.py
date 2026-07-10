import os, sys
import numpy as np
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

# English labels for energy columns (index -> label)
ENERGY_COL_LABELS = {
    1: r"$\mathrm{E_{tot}}$",
    2: r"$\mathrm{E_{NH}}$",
    3: r"$\mathrm{E_{\exp}}$",
    4: r"$\mathrm{E_{fib}}$",
    5: r"$\mathrm{E_{comp}}$",
    6: r"$\mathrm{dE}$",
}

# ENERGY_COL_LABELS_3d = {
#     1: r"$\mathrm{E_{tot}}$",
#     2: r"$\mathrm{E_{NH}}$",
#     3: r"$\mathrm{E_{MR}}$",
#     4: r"$\mathrm{E_{\exp}}$",
#     5: r"$\mathrm{E_{fib}}$",
#     6: r"$\mathrm{E_{comp}}$",
#     7: r"$\mathrm{dE}$",
# }

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 src/Python_scripts/plot_energy.py <filename> [output_name] [--col k]")
        sys.exit(1)

    filename = sys.argv[1]
    outname  = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None

    # column to plot (default = 1)
    col = 1
    if "--col" in sys.argv:
        i = sys.argv.index("--col")
        col = int(sys.argv[i + 1])

    key = os.path.splitext(os.path.basename(filename))[0]

    data = np.loadtxt(filename, comments="#")
    if data.ndim == 1:
        data = data.reshape(1, -1)

    if col < 1 or col >= data.shape[1]:
        raise ValueError(
            f"Invalid --col {col}. File has {data.shape[1]} columns (0..{data.shape[1]-1})"
        )

    it = data[:, 0]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.grid(True)
    ax.set_xlabel(r"iterations")

    # choose nice label for energy, otherwise default to col{col}
    is_energy = key.startswith("energy")
    if is_energy:
        label = ENERGY_COL_LABELS.get(col, f"Column {col}")
        ylabel = r"Energy $\mathrm{E}$"

    ax.plot(it, data[:, col], marker="o", linewidth=1.5, markersize=3, label=label)
    ax.set_ylabel(ylabel)
    ax.legend()
    fig.tight_layout()

    if outname:
        fig.savefig(outname + ".png", dpi=180)
        print(f"Saved figure to {outname}.png")
    else:
        print("No output filename provided (plot not saved).")

    plt.show()
    plt.close(fig)

if __name__ == "__main__":
    main()

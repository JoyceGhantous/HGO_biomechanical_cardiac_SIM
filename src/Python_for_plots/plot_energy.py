import os, sys
import numpy as np
import matplotlib.pyplot as plt

# English labels for energy columns (index -> label)
ENERGY_COL_LABELS = {
    1: "Total energy",
    2: "Linear term",
    3: "Exponential term",
    4: "Fiber exponential term",
    5: "Compressible term",
    6: "First differential of the total energy",
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_energy.py <filename> [output_name] [--col k]")
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

    plt.figure()
    plt.grid(True)
    plt.xlabel("Iteration")

    # choose nice label for energy, otherwise default to col{col}
    is_energy = key.startswith("energy")
    if is_energy:
        label = ENERGY_COL_LABELS.get(col, f"Column {col}")
        ylabel = "Energy"
    else:
        label = f"col{col}"
        ylabel = "Value"

    plt.plot(it, data[:, col], marker="o", linewidth=1, label=label)
    plt.ylabel(ylabel)
    plt.title(f"{key}: {label} vs iteration")
    plt.legend()
    plt.tight_layout()

    if outname:
        plt.savefig(outname + ".png", dpi=200)
        print(f"Saved figure to {outname}.png")
    else:
        print("No output filename provided (plot not saved).")

    plt.show()

if __name__ == "__main__":
    main()

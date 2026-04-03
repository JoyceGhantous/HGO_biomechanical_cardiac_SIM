import os, sys
import numpy as np
import matplotlib.pyplot as plt

CFG = {
    "energy":       (2, "Energy", "Plot of the energy"),
    "L2Gradenergy": (2, "L2 Grad energy", "Plot of L2 norm of the gradient energy"),
    "volume":       (2, "Volume", "Plot of the volume"),
    "jacobian":     (3, "J", "Plot of the Jacobian determinant (min/max)"),
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot.py <filename> [output_name]")
        sys.exit(1)

    filename = sys.argv[1]
    outname  = sys.argv[2] if len(sys.argv) > 2 else None
    key = os.path.splitext(os.path.basename(filename))[0]

    data = np.loadtxt(filename, comments="#")
    if data.ndim == 1:  # single line file -> make it 2D
        data = data.reshape(1, -1)

    ncols, ylabel, title = CFG.get(key, (2, "Value", f"{key} vs iteration"))
    if data.shape[1] < ncols:
        raise ValueError(f"{key} file must have at least {ncols} columns")

    it = data[:, 0]

    plt.figure()
    plt.grid(True)
    plt.xlabel("Iteration")

    if key == "jacobian_":
        plt.plot(it, data[:, 1], marker="o", linewidth=1, label="min(J)")
        plt.plot(it, data[:, 2], marker="o", linewidth=1, label="max(J)")
        plt.legend()
    else:
        plt.plot(it, data[:, 1], marker="o", linewidth=1)

    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    if outname:
        plt.savefig(outname + ".png", dpi=200)
        print(f"Saved figure to {outname}.png")
    else:
        print("No output filename provided (plot not saved).")

    plt.show()

if __name__ == "__main__":
    main()

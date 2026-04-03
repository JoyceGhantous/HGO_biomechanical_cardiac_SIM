"""
plot_results.py
===============
Smart plotting tool for FreeFEM simulation results.
Understands the res/ folder structure and auto-discovers files.

USAGE EXAMPLES:
  # Plot all results for one test (auto-saves to plots/)
  python3 plot_results.py --test Test_OPP_forces_disks

  # Plot all results for all tests
  python3 plot_results.py --all

  # Plot a specific quantity for one test
  python3 plot_results.py --test Test_OPP_forces_disks --quantity energy

  # Plot a specific caseId only
  python3 plot_results.py --test Test_OPP_forces_disks --case 8

  # Overlay all caseIds on one figure (e.g. energy for case 0, 8, 2006)
  python3 plot_results.py --test Test_OPP_forces_disks --quantity energy --overlay

  # Show plots interactively instead of saving
  python3 plot_results.py --test Test_OPP_forces_disks --show
"""

import os
import re
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path("../../res/2D_case/")

# quantity name → column layout
# "x"           : column index to use as x-axis
# "cols"         : { col_index: label } for all plottable columns
# "ylabel"       : y-axis label
# "default_col"  : column plotted by default (None = all cols)
#
# Energy file layout (8 columns):
#   0: outer iter (caseId)  1: inner iter  2: Total energy
#   3: Linear term          4: Exponential term
#   5: Fiber exp. term      6: Compressible term
#   7: First differential
QUANTITY_CFG = {
    "energy":       {"x": 0,
                     "cols": {1: "Total energy",
                              2: "Linear term (Neo-Hookean)",
                              3: "Exponential term",
                              4: "Fiber exp. term",
                              5: "Compressible term",
                              6: "First differential (dE)"},
                     "xlabel": "Outer iteration",
                     "ylabel": "Energy",
                     "default_col": 1},
    "L2Gradenergy": {"x": 0,
                     "cols": {1: "L2 Grad energy"},
                     "xlabel": "Iteration",
                     "ylabel": "L2 Grad energy",
                     "default_col": 1},
    "volume":       {"x": 0,
                     "cols": {1: "Volume"},
                     "xlabel": "Iteration",
                     "ylabel": "Volume",
                     "default_col": 1},
    "jacobian":     {"x": 0,
                     "cols": {1: "min(J)", 2: "max(J)"},
                     "xlabel": "Iteration",
                     "ylabel": "Jacobian",
                     "default_col": None},
}

# Map subfolder name → quantity key
SUBFOLDER_MAP = {
    "en":   "energy",
    "grad": "L2Gradenergy",
    "vol":  "volume",
    "jac":  "jacobian",
}


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def discover_tests(root: Path):
    """Return all Test_* directories."""
    if not root.exists():
        print(f"❌ Root path not found: {root}")
        sys.exit(1)
    return sorted([d for d in root.iterdir() if d.is_dir() and d.name.startswith("Test")])


def discover_files(test_dir: Path):
    """
    Return dict: { quantity: [ (caseId, Path), ... ] }
    by scanning en/, grad/, vol/, jac/ subfolders.
    """
    found = defaultdict(list)
    for subfolder, quantity in SUBFOLDER_MAP.items():
        folder = test_dir / subfolder
        if not folder.exists():
            continue
        for f in sorted(folder.iterdir(), key=lambda p: _sort_key(p.name)):
            if f.suffix == ".txt":
                case_id = extract_case_id(f.name)
                found[quantity].append((case_id, f))
    return found


def extract_case_id(filename: str) -> str:
    """Extract trailing number from filenames like energy8.txt → '8'."""
    m = re.search(r"(\d+)(?:\.txt)?$", filename)
    return m.group(1) if m else filename


def _sort_key(name: str):
    """Sort filenames numerically by trailing number."""
    m = re.search(r"(\d+)", name)
    return int(m.group(1)) if m else 0


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def load_data(path: Path):
    """Load a txt file, always return 2D array."""
    try:
        data = np.loadtxt(path, comments="#")
        if data.size == 0:
            print(f"  ⚠️  Skipping {path.name}: file is empty")
            return None
        return data.reshape(1, -1) if data.ndim == 1 else data
    except Exception as e:
        print(f"  ⚠️  Could not load {path.name}: {e}")
        return None


def plot_single(path: Path, quantity: str, case_id: str, out_dir: Path, show: bool, col: int = None):
    """Plot one file, save to out_dir/plots/."""
    cfg   = QUANTITY_CFG.get(quantity, {"cols": {1: "Value"}, "ylabel": "Value", "default_col": 1})
    data  = load_data(path)
    if data is None:
        return

    x_col = cfg.get("x", 0)
    it = data[:, x_col]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.grid(True, alpha=0.4)
    ax.set_xlabel(cfg.get("xlabel", "Iteration"))
    ax.set_ylabel(cfg["ylabel"])
    ax.set_title(f"{quantity}  |  case {case_id}")

    target_cols = cfg["cols"]
    if col is not None:
        target_cols = {col: cfg["cols"].get(col, f"col {col}")}
    elif cfg["default_col"] is not None:
        target_cols = {cfg["default_col"]: cfg["cols"].get(cfg["default_col"], "Value")}

    for c, label in target_cols.items():
        if c < data.shape[1]:
            ax.plot(it, data[:, c], marker="o", linewidth=1.5, markersize=3, label=label)

    if len(target_cols) > 1:
        ax.legend(fontsize=8)

    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{quantity}_{case_id}.png"
    plt.savefig(out_path, dpi=180)
    print(f"  💾  {out_path.relative_to(ROOT.parent.parent)}")

    if show:
        plt.show()
    plt.close()


def plot_overlay(files: list, quantity: str, test_name: str, out_dir: Path, show: bool, col: int = None):
    """Overlay all caseIds for a quantity on one figure."""
    cfg = QUANTITY_CFG.get(quantity, {"cols": {1: "Value"}, "ylabel": "Value", "default_col": 1})
    target_col = col if col is not None else (cfg["default_col"] or 1)
    label_str  = cfg["cols"].get(target_col, f"col {target_col}")

    x_col = cfg.get("x", 0)
    colors = cm.tab10(np.linspace(0, 1, max(len(files), 1)))

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.grid(True, alpha=0.4)
    ax.set_xlabel(cfg.get("xlabel", "Iteration"))
    ax.set_ylabel(cfg["ylabel"])
    ax.set_title(f"{test_name}  |  {quantity}  |  {label_str}  — all cases")

    for (case_id, path), color in zip(files, colors):
        data = load_data(path)
        if data is None or target_col >= data.shape[1]:
            continue
        ax.plot(data[:, x_col], data[:, target_col],
                marker="o", linewidth=1.5, markersize=3,
                label=f"case {case_id}", color=color)

    ax.legend(fontsize=8, ncol=2)
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{quantity}_all_cases_overlay.png"
    plt.savefig(out_path, dpi=180)
    print(f"  💾  {out_path.relative_to(ROOT.parent.parent)}")

    if show:
        plt.show()
    plt.close()


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def run_test(test_dir: Path, quantity_filter: str, case_filter: str,
             overlay: bool, show: bool, col: int):
    """Process one test directory."""
    print(f"\n📁 {test_dir.name}")
    out_dir = test_dir / "plots"
    files_by_qty = discover_files(test_dir)

    if not files_by_qty:
        print("  ⚠️  No data files found.")
        return

    quantities = [quantity_filter] if quantity_filter else list(files_by_qty.keys())

    for qty in quantities:
        if qty not in files_by_qty:
            print(f"  ⚠️  No files for quantity '{qty}'")
            continue

        files = files_by_qty[qty]

        # Filter by case if requested
        if case_filter:
            files = [(cid, p) for cid, p in files if cid == case_filter]
            if not files:
                print(f"  ⚠️  No files for case '{case_filter}' in {qty}")
                continue

        if overlay and len(files) > 1:
            plot_overlay(files, qty, test_dir.name, out_dir, show, col)
        else:
            for case_id, path in files:
                plot_single(path, qty, case_id, out_dir, show, col)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    global ROOT
    parser = argparse.ArgumentParser(
        description="Smart plotter for FreeFEM simulation results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--root",     type=str, default=str(ROOT),
                        help=f"Path to Saved_values folder (default: {ROOT})")
    parser.add_argument("--test",     type=str, default=None,
                        help="Test folder name, e.g. Test_OPP_forces_disks")
    parser.add_argument("--all",      action="store_true",
                        help="Process all Test_* folders")
    parser.add_argument("--quantity", type=str, default=None,
                        choices=list(QUANTITY_CFG.keys()),
                        help="Only plot this quantity (default: all)")
    parser.add_argument("--case",     type=str, default=None,
                        help="Only plot this caseId, e.g. 8 or 2006")
    parser.add_argument("--col",      type=int, default=None,
                        help="Column index to plot for energy (default: 1 = total)")
    parser.add_argument("--overlay",  action="store_true",
                        help="Overlay all cases on one figure per quantity")
    parser.add_argument("--show",     action="store_true",
                        help="Show interactive plot window (default: save only)")
    args = parser.parse_args()
    ROOT = Path(args.root)

    if not args.test and not args.all:
        parser.print_help()
        print("\n❌  Provide --test <name> or --all")
        sys.exit(1)

    tests = discover_tests(ROOT)

    if args.all:
        for td in tests:
            run_test(td, args.quantity, args.case, args.overlay, args.show, args.col)
    else:
        matches = [td for td in tests if td.name == args.test]
        if not matches:
            available = "\n  ".join(td.name for td in tests)
            print(f"❌  Test '{args.test}' not found. Available:\n  {available}")
            sys.exit(1)
        run_test(matches[0], args.quantity, args.case, args.overlay, args.show, args.col)

    print("\n✅  Done.\n")


if __name__ == "__main__":
    main()


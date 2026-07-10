"""
This script provides a plotting tool for FreeFEM simulation results.

Usage examples
--------------

python3 src/Python_scripts/plot_results.py --all
python3 src/Python_scripts/plot_results.py --all --debug
python3 src/Python_scripts/plot_results.py --test Test_horizontal_forces_disks_With_dirichlet --mode Direct
python3 src/Python_scripts/plot_results.py --test Test_horizontal_forces_disks_With_dirichlet --mode Direct --case 1
python3 src/Python_scripts/plot_results.py --test Test_horizontal_forces_disks_With_dirichlet --mode Direct --quantity energy
python3 src/Python_scripts/plot_results.py --test Test_horizontal_forces_disks_With_dirichlet --mode Direct --quantity L2Gradenergy --overlay
"""

import re
import sys
import argparse
import numpy as np
from pathlib import Path
from collections import defaultdict

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

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path("res/2D_case_MPI/").resolve()

QUANTITY_CFG = {
    "energy": {
        "x": 0,
        "cols": {
            1: r"$\mathrm{E}_{\mathrm{tot}}$",
            2: r"$\mathrm{E}_{\mathrm{NH}}$",
            3: r"$\mathrm{E}_{\mathrm{exp}}$",
            4: r"$\mathrm{E}_{\mathrm{fib}}$",
            5: r"$\mathrm{E}_{\mathrm{comp}}$",
            6: r"$\mathrm{dE}$",
        },
        "xlabel": r"iterations",
        "ylabel": r"Energy $\mathrm{E}$",
        "default_col": 1,
    },

    "L2Gradenergy": {
        "x": 0,
        "cols": {
            1: r"$\|\|\nabla \mathrm{E}\|\|_{L^2}$",
        },
        "xlabel": r"iterations",
        "ylabel": r"$\|\|\nabla \mathrm{E}\|\|_{L^2}$",
        "default_col": 1,
    },

    "volume": {
        "x": 0,
        "cols": {
            1: r"$\mathrm{Vol}$",
        },
        "xlabel": r"iterations",
        "ylabel": r"$\mathrm{Vol}$",
        "default_col": 1,
    },

    "jacobian": {
        "x": 0,
        "cols": {
            1: r"$\mathrm{\min(J)}$",
            2: r"$\mathrm{\max(J)}$",
        },
        "xlabel": r"iterations",
        "ylabel": r"$\mathrm{J}$",
        "default_col": None,
    },
}


QUANTITY_FILES = {
    "energy": {
        "subfolder": "en",
        "prefix": "energy",
        "exact": "energy.txt",
    },
    "L2Gradenergy": {
        "subfolder": "grad",
        "prefix": "L2Gradenergy",
        "exact": "L2Gradenergy.txt",
    },
    "volume": {
        "subfolder": "vol",
        "prefix": "volume",
        "exact": "volume.txt",
    },
    "jacobian": {
        "subfolder": "jac",
        "prefix": "jacobian",
        "exact": "jacobian.txt",
    },
}

VALID_MODES = ("Direct", "Inverse")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def normalize_case(case_name: str) -> str:
    """case_1 -> 1. Otherwise keep the input."""
    case_name = str(case_name)
    if case_name.startswith("case_"):
        return case_name[len("case_"):]
    return case_name


def extract_case_id(filename: str, prefix: str) -> str:
    """
        Extract a case id from a legacy filename.

        Examples:
          energy0.txt                 -> 0
          energy2006.txt              -> 2006
          L2Gradenergy0_bcF1.txt      -> 0_bcF1
          jacobian.txt                -> no_case
    """
    stem = Path(filename).stem

    if stem == prefix:
        return "no_case"

    if stem.startswith(prefix):
        case_id = stem[len(prefix):]
        return case_id if case_id else "no_case"

    return stem


def case_sort_key(case_id: str):
    """Sort by first number when possible."""
    m = re.search(r"\d+", str(case_id))
    return int(m.group(0)) if m else 0


def safe_relative(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def add_found(found, seen_paths, quantity, case_id, mode, path):
    """Append one file if it was not already registered."""
    path = path.resolve()

    if path in seen_paths:
        return

    seen_paths.add(path)
    found[quantity].append((case_id, mode, path))


def print_debug_tree(test_dir: Path, max_depth: int = 5):
    """
        Print a compact tree of directories and txt files.
        Useful when discovery finds no data.
    """
    print("  🔎 Debug tree:")

    base_depth = len(test_dir.parts)

    for p in sorted(test_dir.rglob("*")):
        depth = len(p.parts) - base_depth

        if depth > max_depth:
            continue

        if p.is_dir() or p.suffix == ".txt":
            indent = "    " + "  " * (depth - 1)
            suffix = "/" if p.is_dir() else ""
            print(f"{indent}{p.name}{suffix}")


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------

def discover_tests(root: Path):
    """Return all Test_* directories."""
    if not root.exists():
        print(f"❌ Root path not found: {root}")
        sys.exit(1)

    tests = sorted([
        d for d in root.iterdir()
        if d.is_dir() and d.name.startswith("Test")
    ])

    if not tests:
        print(f"❌ No Test_* folders found in: {root}")
        sys.exit(1)

    return tests


def discover_files(test_dir: Path, mode_filter: str = None, debug: bool = False):
    """
        Return:
          dict[quantity] = [(case_id, mode, path), ...]

        This function scans:
          1. New structure: Test_*/Direct/case_*/en/energy.txt
          2. New structure with suffixed files: Test_*/Direct/case_*/en/energy*.txt
          3. Mode but no case dir: Test_*/Direct/en/energy*.txt
          4. Old structure: Test_*/en/energy*.txt
    """
    found = defaultdict(list)
    seen_paths = set()

    # Candidate mode directories.
    # If --mode Direct is requested, only scan Test_*/Direct.
    mode_dirs = []

    if mode_filter:
        candidate = test_dir / mode_filter
        if candidate.exists() and candidate.is_dir():
            mode_dirs.append(candidate)
        elif debug:
            print(f"  🔎 Mode folder not found: {candidate}")
    else:
        for mode in VALID_MODES:
            candidate = test_dir / mode
            if candidate.exists() and candidate.is_dir():
                mode_dirs.append(candidate)

    # ------------------------------------------------------------------
    # 1 and 2. New structure: Direct/case_*/subfolder/file.txt
    # ------------------------------------------------------------------
    for mode_dir in mode_dirs:
        mode = mode_dir.name

        case_dirs = sorted([
            d for d in mode_dir.iterdir()
            if d.is_dir() and d.name.startswith("case_")
        ], key=lambda p: case_sort_key(normalize_case(p.name)))

        if debug:
            print(f"  🔎 Mode {mode}: {len(case_dirs)} case folder(s) found")

        for case_dir in case_dirs:
            case_id = normalize_case(case_dir.name)

            for quantity, spec in QUANTITY_FILES.items():
                folder = case_dir / spec["subfolder"]

                if not folder.exists():
                    continue

                # Exact file first, e.g. energy.txt
                exact_path = folder / spec["exact"]
                if exact_path.exists() and exact_path.is_file():
                    add_found(found, seen_paths, quantity, case_id, mode, exact_path)

                # Fallback: energy*.txt, L2Gradenergy*.txt, etc.
                for f in sorted(folder.glob(spec["prefix"] + "*.txt")):
                    add_found(found, seen_paths, quantity, case_id, mode, f)

    # ------------------------------------------------------------------
    # 3. Mode but no case dir: Direct/en/energy*.txt
    # ------------------------------------------------------------------
    for mode_dir in mode_dirs:
        mode = mode_dir.name

        for quantity, spec in QUANTITY_FILES.items():
            folder = mode_dir / spec["subfolder"]

            if not folder.exists():
                continue

            for f in sorted(folder.glob(spec["prefix"] + "*.txt")):
                case_id = extract_case_id(f.name, spec["prefix"])
                add_found(found, seen_paths, quantity, case_id, mode, f)

    # ------------------------------------------------------------------
    # 4. Old structure: Test_*/en/energy*.txt
    # Only scan old structure when no mode filter is requested.
    # ------------------------------------------------------------------
    if mode_filter is None:
        for quantity, spec in QUANTITY_FILES.items():
            folder = test_dir / spec["subfolder"]

            if not folder.exists():
                continue

            for f in sorted(folder.glob(spec["prefix"] + "*.txt")):
                case_id = extract_case_id(f.name, spec["prefix"])
                add_found(found, seen_paths, quantity, case_id, "Legacy", f)

    for quantity in found:
        found[quantity].sort(key=lambda item: (item[1], case_sort_key(item[0]), str(item[2])))

    if debug:
        total = sum(len(v) for v in found.values())
        print(f"  🔎 Total detected data files: {total}")
        for quantity, files in found.items():
            print(f"  🔎 {quantity}: {len(files)} file(s)")
            for case_id, mode, path in files:
                print(f"      - {mode}, case {case_id}: {safe_relative(path, test_dir)}")

        if total == 0:
            print_debug_tree(test_dir)

    return found


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(path: Path):
    """Load a txt file, always return a 2D array."""
    try:
        data = np.loadtxt(path, comments="#")

        if data.size == 0:
            print(f"  ⚠️  Skipping {path.name}: file is empty")
            return None

        if data.ndim == 1:
            data = data.reshape(1, -1)

        return data

    except Exception as e:
        print(f"  ⚠️  Could not load {path}: {e}")
        return None


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_single(path: Path, quantity: str, case_id: str, mode: str,
                out_dir: Path, show: bool, col: int = None):
    """Plot one file."""
    cfg = QUANTITY_CFG.get(
        quantity,
        {
            "x": 0,
            "cols": {1: "Value"},
            "xlabel": "Iteration",
            "ylabel": "Value",
            "default_col": 1,
        }
    )

    data = load_data(path)
    if data is None:
        return

    x_col = cfg.get("x", 0)

    if x_col >= data.shape[1]:
        print(f"  ⚠️  Skipping {path.name}: missing x column {x_col}")
        return

    x = data[:, x_col]

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.grid(True)
    ax.set_xlabel(cfg.get("xlabel", "Iteration"))
    ax.set_ylabel(cfg.get("ylabel", "Value"))

    target_cols = cfg["cols"]

    if col is not None:
        target_cols = {
            col: cfg["cols"].get(col, f"col {col}")
        }
    elif cfg["default_col"] is not None:
        target_cols = {
            cfg["default_col"]: cfg["cols"].get(
                cfg["default_col"],
                "Value"
            )
        }

    plotted = False

    for c, label in target_cols.items():
        if c >= data.shape[1]:
            print(f"  ⚠️  Skipping column {c} in {path.name}: not enough columns")
            continue

        y = data[:, c]

        if quantity == "L2Gradenergy":
            mask = (x > 0) & (y > 0)

            if not np.any(mask):
                print(f"  ⚠️  Skipping {path.name}: no positive values for semilogy")
                continue

            ax.semilogy(
                x[mask],
                y[mask],
                marker="o",
                linewidth=1.5,
                markersize=3,
                label=label,
            )
            ax.grid(True)

        else:
            ax.plot(
                x,
                y,
                marker="o",
                label=label,
            )

        plotted = True

    if not plotted:
        plt.close()
        return

    ax.legend()

    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{quantity}_{mode}_case_{case_id}.png"

    plt.savefig(out_path, dpi=180)
    print(f"  💾 {safe_relative(out_path, ROOT.parent)}")

    if show:
        plt.show()

    plt.close()


def plot_overlay(files: list, quantity: str, test_name: str,
                 out_dir: Path, show: bool, col: int = None):
    """
        Overlay several cases/modes on one figure.

        files contains:
          [(case_id, mode, path), ...]
    """
    cfg = QUANTITY_CFG.get(
        quantity,
        {
            "x": 0,
            "cols": {1: "Value"},
            "xlabel": "Iteration",
            "ylabel": "Value",
            "default_col": 1,
        }
    )

    target_col = col if col is not None else (cfg["default_col"] or 1)
    label_str = cfg["cols"].get(target_col, f"col {target_col}")

    x_col = cfg.get("x", 0)
    colors = cm.tab10(np.linspace(0, 1, max(len(files), 1)))

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.grid(True)
    ax.set_xlabel(cfg.get("xlabel", "Iteration"))
    ax.set_ylabel(cfg["ylabel"])

    plotted = False

    for (case_id, mode, path), color in zip(files, colors):
        data = load_data(path)

        if data is None:
            continue

        if x_col >= data.shape[1]:
            print(f"  ⚠️  Skipping {path.name}: missing x column {x_col}")
            continue

        if target_col >= data.shape[1]:
            print(f"  ⚠️  Skipping {path.name}: missing target column {target_col}")
            continue

        x = data[:, x_col]
        y = data[:, target_col]
        label = f"{mode} case {case_id}"

        if quantity == "L2Gradenergy":
            mask = (x > 0) & (y > 0)

            if not np.any(mask):
                print(f"  ⚠️  Skipping {label}: no positive values for semilogy")
                continue

            ax.semilogy(
                x[mask],
                y[mask],
                marker="o",
                linewidth=1.5,
                markersize=3,
                label=label,
                color=color,
            )
            ax.grid(True)

        else:
            ax.plot(
                x,
                y,
                marker="o",
                linewidth=1.5,
                markersize=3,
                label=label,
                color=color,
            )

        plotted = True

    if not plotted:
        plt.close()
        return

    ax.legend(fontsize=8, ncol=2)
    plt.tight_layout()

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{quantity}_overlay.png"

    plt.savefig(out_path, dpi=180)
    print(f"  💾 {safe_relative(out_path, ROOT.parent)}")

    if show:
        plt.show()

    plt.close()


# ---------------------------------------------------------------------------
# Runners
# ---------------------------------------------------------------------------

def run_test(test_dir: Path, quantity_filter: str, case_filter: str,
             mode_filter: str, overlay: bool, show: bool,
             col: int, order_start: int, debug: bool):
    """Process one Test_* directory."""
    print(f"\n📁 {test_dir.name}")

    files_by_qty = discover_files(
        test_dir,
        mode_filter=mode_filter,
        debug=debug,
    )

    if not files_by_qty:
        print("  ⚠️  No data files found.")
        print("  👉 Try:")
        print(f"     find {test_dir} -maxdepth 6 -type f | sort")
        print("     python3 src/Python_scripts/plot_results.py --all --debug")
        return

    quantities = [quantity_filter] if quantity_filter else list(files_by_qty.keys())

    for qty in quantities:
        if qty not in files_by_qty:
            print(f"  ⚠️  No files for quantity '{qty}'")
            continue

        files = files_by_qty[qty]

        # Filter by case if requested.
        # Accept both --case 1 and --case case_1.
        if case_filter:
            wanted_case = normalize_case(case_filter)
            files = [
                (cid, mode, path)
                for cid, mode, path in files
                if normalize_case(cid) == wanted_case
            ]

            if not files:
                print(f"  ⚠️  No files for case '{case_filter}' in {qty}")
                continue

        if mode_filter:
            out_dir = test_dir / mode_filter / "plots"
        else:
            out_dir = test_dir / "plots"

        if overlay and len(files) > 1:
            plot_overlay(files, qty, test_dir.name, out_dir, show, col)
        else:
            for case_id, mode, path in files:
                plot_single(path, qty, case_id, mode, out_dir, show, col)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    global ROOT

    parser = argparse.ArgumentParser(
        description="Plots for FreeFEM simulation results.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "--root",
        type=str,
        default=str(ROOT),
        help=f"Path to results root folder, e.g. res/2D_case_MPI/ (default: {ROOT})",
    )

    parser.add_argument(
        "--test",
        type=str,
        default=None,
        help="Test folder name, e.g. Test_horizontal_forces_disks_With_dirichlet",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all Test_* folders",
    )

    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        choices=list(VALID_MODES),
        help="Only process this mode: Direct or Inverse. Default: both plus legacy.",
    )

    parser.add_argument(
        "--quantity",
        type=str,
        default=None,
        choices=list(QUANTITY_CFG.keys()),
        help="Only plot this quantity: energy, L2Gradenergy, volume, jacobian.",
    )

    parser.add_argument(
        "--case",
        type=str,
        default=None,
        help="Only plot this case id, e.g. 1, 8, 2006, or case_1.",
    )

    parser.add_argument(
        "--col",
        type=int,
        default=None,
        help="Column index to plot, e.g. --col 1",
    )

    parser.add_argument(
        "--overlay",
        action="store_true",
        help="Overlay all selected cases/modes on one figure per quantity",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Show interactive plot window instead of only saving",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print discovered folders/files while scanning.",
    )

    parser.add_argument(
        "--order-start",
        type=int,
        default=None,
        help="Reserved for convergence-order fit. Currently not used.",
    )

    args = parser.parse_args()
    ROOT = Path(args.root).resolve()

    if not args.test and not args.all:
        parser.print_help()
        print("\n❌ Provide --test <name> or --all")
        sys.exit(1)

    tests = discover_tests(ROOT)

    if args.all:
        for td in tests:
            run_test(
                td,
                args.quantity,
                args.case,
                args.mode,
                args.overlay,
                args.show,
                args.col,
                args.order_start,
                args.debug,
            )
    else:
        matches = [td for td in tests if td.name == args.test]

        if not matches:
            available = "\n  ".join(td.name for td in tests)
            print(f"❌ Test '{args.test}' not found. Available:\n  {available}")
            sys.exit(1)

        run_test(
            matches[0],
            args.quantity,
            args.case,
            args.mode,
            args.overlay,
            args.show,
            args.col,
            args.order_start,
            args.debug,
        )

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()

"""
reorganize_res.py
=================
Reorganizes a `res/` simulation results folder by test case.

LOGIC:
  1. Scans for all Test_* directories under res/
  2. For each test, extracts a "case key" from the folder name
     e.g. Test_OPP_forces_disks → "OPP_forces_disks"
  3. Matches mesh files (Mesh/) and fiber files (fiber/) to their test
     by looking for the case key in the filename
  4. Moves matched mesh/fiber files INTO the test folder under mesh/ and fiber/
  5. Sorts loose files at the root of each test folder:
       .eps / .png / .pdf  → plots/
       .txt / .csv / .dat  → data/
       .msh / .mesh / .geo → mesh/
  6. Leaves LR3/LR4/LR5 subfolders completely untouched
  7. Skips old_2D_case/ entirely

Usage:
  python3 reorganize_res.py --root /path/to/res            # dry run (default)
  python3 reorganize_res.py --root /path/to/res --apply    # actually move files
  python3 reorganize_res.py --root /path/to/res --report   # also save report.txt
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from collections import defaultdict


# ---------------------------------------------------------------------------
# Configuration — edit to match your conventions
# ---------------------------------------------------------------------------

EXT_MAP = {
    ".eps":  "plots",
    ".png":  "plots",
    ".pdf":  "plots",
    ".svg":  "plots",
    ".txt":  "data",
    ".csv":  "data",
    ".dat":  "data",
    ".log":  "data",
    ".msh":  "mesh",
    ".mesh": "mesh",
    ".geo":  "mesh",
    ".vtu":  "fiber",
}

# Subfolders inside a Test dir that are NEVER touched
PROTECTED_SUBDIRS = {
    "LR3", "LR4", "LR5",
    "en", "grad", "jac", "vol", "info",
    "Plots", "plots", "data", "mesh", "fiber", "misc",
}

# Top-level folders to skip entirely
SKIP_FOLDERS = {"old_2D_case"}

TEST_PATTERN = re.compile(r"^Test_(.+)$", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_case_key(test_dir_name: str) -> str:
    m = TEST_PATTERN.match(test_dir_name)
    return m.group(1) if m else test_dir_name


def find_test_dirs(root: Path):
    test_dirs = []
    for dirpath, dirnames, _ in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_FOLDERS]
        for d in list(dirnames):
            if TEST_PATTERN.match(d):
                test_dirs.append(Path(dirpath) / d)
    return sorted(test_dirs)


def find_source_files(folder: Path):
    if not folder.exists():
        return []
    return [f for f in folder.iterdir() if f.is_file()]


def match_files_to_key(files, case_key: str):
    return [f for f in files if case_key.lower() in f.name.lower()]


def build_tree(root: Path, prefix="", max_depth=4, depth=0):
    if depth > max_depth:
        return ""
    lines = []
    try:
        entries = sorted(root.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        return ""
    for i, entry in enumerate(entries):
        last = i == len(entries) - 1
        lines.append(f"{prefix}{'└── ' if last else '├── '}{entry.name}")
        if entry.is_dir():
            ext = "    " if last else "│   "
            sub = build_tree(entry, prefix + ext, max_depth, depth + 1)
            if sub:
                lines.append(sub)
    return "\n".join(lines)


def fmt_move(src: Path, dst: Path, root: Path):
    try:
        return f"  MOVE  {src.relative_to(root)}\n    →   {dst.relative_to(root)}"
    except ValueError:
        return f"  MOVE  {src}\n    →   {dst}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(root_path: str, apply: bool = False, report: bool = False):
    root = Path(root_path).resolve()
    if not root.exists():
        print(f"❌  Path not found: {root}")
        return

    print(f"\n{'='*60}")
    print(f"  Root : {root}")
    print(f"  Mode : {'✅  APPLY — files will be moved' if apply else '🔍  DRY RUN — no changes made'}")
    print(f"{'='*60}\n")

    print("📂 CURRENT STRUCTURE")
    print(root.name)
    print(build_tree(root))
    print()

    # Build shared file pools from Mesh/ and fiber/ under each case folder
    case_folders = [p for p in root.iterdir()
                    if p.is_dir() and p.name not in SKIP_FOLDERS]
    mesh_pool, fiber_pool = [], []
    for cf in case_folders:
        mesh_pool  += find_source_files(cf / "Mesh")
        fiber_pool += find_source_files(cf / "fiber")

    test_dirs = find_test_dirs(root)
    if not test_dirs:
        print("⚠️  No Test_* directories found.")
        return

    all_moves   = []
    report_lines = [f"Reorganization plan for: {root}\n"]
    errors      = []

    print("📋 PLANNED MOVES")
    print("-" * 60)

    for td in test_dirs:
        case_key = get_case_key(td.name)
        moves = []

        # 1. Pull matching mesh files from shared Mesh/ pool
        for f in match_files_to_key(mesh_pool, case_key):
            moves.append((f, td / "mesh" / f.name))

        # 2. Pull matching fiber files from shared fiber/ pool
        for f in match_files_to_key(fiber_pool, case_key):
            moves.append((f, td / "fiber" / f.name))

        # 3. Sort loose files sitting directly in the test root
        for item in sorted(td.iterdir()):
            if item.is_file():
                # .mesh.gmsh has two suffixes — handle specially
                if item.name.endswith(".mesh.gmsh"):
                    subfolder = "mesh"
                else:
                    subfolder = EXT_MAP.get(item.suffix.lower(), "misc")
                moves.append((item, td / subfolder / item.name))

        if moves:
            section = f"\n📁 {td.name}  ({len(moves)} file(s))"
            print(section)
            report_lines.append(section)
            for src, dst in moves:
                line = fmt_move(src, dst, root)
                print(line)
                report_lines.append(line)
            all_moves.extend(moves)

    if not all_moves:
        print("\n✅  Nothing to reorganize — structure is already clean.")
        return

    print(f"\n{'='*60}")
    print(f"  Total files to move : {len(all_moves)}")
    print(f"{'='*60}\n")

    if apply:
        print("🚀 Applying moves...\n")
        for src, dst in all_moves:
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(dst))
                print(f"  ✓  {src.name}  →  .../{dst.parent.name}/")
            except Exception as e:
                msg = f"  ✗  {src.name}: {e}"
                print(msg)
                errors.append(msg)

        moved = len(all_moves) - len(errors)
        print(f"\n✅ Done.  {moved} moved,  {len(errors)} errors.")
        if errors:
            print("\n⚠️  Errors:")
            for e in errors:
                print(e)

        print("\n📂 NEW STRUCTURE")
        print(root.name)
        print(build_tree(root))

    else:
        print("👆 DRY RUN — no files were moved.")
        print("   Run with --apply to execute:\n")
        print(f"   python3 reorganize_res.py --root {root_path} --apply\n")

    if report:
        rp = Path("reorganization_report.txt")
        rp.write_text("\n".join(report_lines))
        print(f"📄 Report saved → {rp.resolve()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reorganize simulation results by test case."
    )
    parser.add_argument("--root",   type=str, default="./res",
                        help="Path to root results folder (default: ./res)")
    parser.add_argument("--apply",  action="store_true",
                        help="Actually move files (default is dry run)")
    parser.add_argument("--report", action="store_true",
                        help="Save plan to reorganization_report.txt")
    args = parser.parse_args()
    run(args.root, apply=args.apply, report=args.report)

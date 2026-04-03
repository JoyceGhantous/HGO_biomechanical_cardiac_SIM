"""
flip_mesh_y.py
--------------
Flips a Gmsh v2.2 mesh symmetrically w.r.t. the Y-axis (th.x = -th.x).
Fixes triangle orientation so FreeFem++ sees positive areas.

Zero dependency on meshio format strings — parses the .msh file directly.

Usage:
    python3 flip_mesh_y.py                      
    python3 flip_mesh_y.py input.msh output.msh
"""
import sys
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

input_file  = sys.argv[1] if len(sys.argv) > 1 else BASE_DIR / ".." / "LR_gmsh_6.msh"
output_file = sys.argv[2] if len(sys.argv) > 2 else BASE_DIR / ".." / "LR_flipped_6.msh"

# ── Gmsh v2.2 element types that have signed area (swap nodes 1&2 to fix CCW) ──
SURFACE_ELEM_TYPES = {
    2,   # 3-node triangle
    9,   # 6-node triangle (P2)
}

print(f"Reading mesh from : {input_file}")
with open(input_file, "r") as f:
    raw = f.read()

# ── Split into named sections ──────────────────────────────────────────────────
def get_section(text, name):
    import re
    m = re.search(rf"\${name}\n(.*?)\$End{name}", text, re.DOTALL)
    return m.group(1).strip() if m else ""

header_txt   = get_section(raw, "MeshFormat")
physname_txt = get_section(raw, "PhysicalNames")
nodes_txt    = get_section(raw, "Nodes")
elems_txt    = get_section(raw, "Elements")

# ── Nodes ──────────────────────────────────────────────────────────────────────
node_lines = nodes_txt.splitlines()
n_nodes    = int(node_lines[0])
node_ids, coords = [], []
for line in node_lines[1:]:
    parts = line.split()
    node_ids.append(int(parts[0]))
    coords.append([float(parts[1]), float(parts[2]), float(parts[3])])
coords = np.array(coords)

# ── Flip X ─────────────────────────────────────────────────────────────────────
coords_orig = coords[:, 0].copy()
coords[:, 0] = -coords[:, 0]

# ── Elements ───────────────────────────────────────────────────────────────────
elem_lines = elems_txt.splitlines()
n_elems    = int(elem_lines[0])
new_elem_lines = []
for line in elem_lines[1:]:
    parts = line.split()
    elem_type = int(parts[1])
    if elem_type in SURFACE_ELEM_TYPES:
        n_tags   = int(parts[2])
        conn_start = 3 + n_tags          # index of first connectivity node
        conn = parts[conn_start:]
        # swap nodes 1 & 2 (0-indexed in connectivity) to restore CCW winding
        conn[1], conn[2] = conn[2], conn[1]
        parts = parts[:conn_start] + conn
    new_elem_lines.append(" ".join(parts))

# ── Write ──────────────────────────────────────────────────────────────────────
print(f"Writing flipped mesh to : {output_file}")
with open(output_file, "w") as f:
    f.write("$MeshFormat\n")
    f.write(header_txt + "\n")
    f.write("$EndMeshFormat\n")

    if physname_txt:
        f.write("$PhysicalNames\n")
        f.write(physname_txt + "\n")
        f.write("$EndPhysicalNames\n")

    f.write("$Nodes\n")
    f.write(f"{n_nodes}\n")
    for nid, xyz in zip(node_ids, coords):
        f.write(f"{nid} {xyz[0]:.17g} {xyz[1]:.17g} {xyz[2]:.17g}\n")
    f.write("$EndNodes\n")

    f.write("$Elements\n")
    f.write(f"{n_elems}\n")
    for line in new_elem_lines:
        f.write(line + "\n")
    f.write("$EndElements\n")

# ── Verification ───────────────────────────────────────────────────────────────
assert np.allclose(coords[:, 0], -coords_orig),        "FAIL: X not negated"
assert np.isclose(coords[:, 0].min(), -coords_orig.max()), "FAIL: bbox min"
assert np.isclose(coords[:, 0].max(), -coords_orig.min()), "FAIL: bbox max"
print("✓ All verification checks passed")

print(f"\n--- Summary ---")
print(f"  Nodes    : {n_nodes}")
print(f"  Elements : {n_elems}")
print(f"  X range (original): [{coords_orig.min():.4g}, {coords_orig.max():.4g}]")
print(f"  X range (flipped) : [{coords[:,0].min():.4g}, {coords[:,0].max():.4g}]")
print("Done.")

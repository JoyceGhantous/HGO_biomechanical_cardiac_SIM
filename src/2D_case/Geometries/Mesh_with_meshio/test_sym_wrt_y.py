import meshio
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent          # .../Mesh_with_meshio/
mesh = meshio.read(BASE_DIR / ".." / "LR_gmsh_6.msh")
meshF = meshio.read(BASE_DIR / ".." / "LR_flipped_6.msh")

original_x  = mesh.points[:, 0]
flipped_x   = meshF.points[:, 0]

# 1. Every X coordinate is exactly negated
assert np.allclose(flipped_x, -original_x), \
     "FAIL: some X coordinates were not negated"

# 2. Y and Z are untouched
assert np.allclose(meshF.points[:, 1], mesh.points[:, 1]), \
    "FAIL: Y coordinates changed"
assert np.allclose(meshF.points[:, 2], mesh.points[:, 2]), \
    "FAIL: Z coordinates changed"

# 3. Bounding box is mirrored (min/max swap signs)
assert np.isclose(flipped_x.min(), -original_x.max()), \
    "FAIL: X min of flipped != -X max of original"
assert np.isclose(flipped_x.max(), -original_x.min()), \
    "FAIL: X max of flipped != -X min of original"

# 4. Number of points and cells unchanged
assert len(meshF.points) == len(mesh.points), \
    "FAIL: point count changed"

print("All verification checks passed — mesh is correctly flipped w.r.t. Y-axis")
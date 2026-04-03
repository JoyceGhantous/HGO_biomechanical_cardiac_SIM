"""
check_symmetry.py
-----------------
Vérifie la symétrie axiale (x -> -x) d'un maillage 2D généré par Gmsh.

Usage:
    python3 check_symmetry.py

Dépendances:
    pip install meshio numpy
"""

import meshio
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent
mesh = meshio.read(BASE_DIR / ".." / "lower_half_from_quarter.msh")
# Extraction des coordonnées 2D (x, y) uniquement
pts = mesh.points[:, :2]

# VÉRIFICATION : équilibre de nombre de noeuds gauche/droite

TOL = 1e-2
x_positive = pts[pts[:, 0] >  TOL]          # points dans le demi-plan x > 0 (droite)
x_negative = pts[pts[:, 0] < -TOL]          # points dans le demi-plan x < 0 (gauche)
x_axis     = pts[np.abs(pts[:, 0]) <= TOL]  # points sur l'axe de symétrie x = 0

print(f"Points x > 0  : {len(x_positive)}")
print(f"Points x < 0  : {len(x_negative)}")
print(f"Points x = 0  : {len(x_axis)}")

# Un maillage symétrique doit avoir autant de points à gauche qu'à droite
if len(x_positive) == len(x_negative):
    print("Nombre de points symétrique")
else:
    print(f"Erreur - Déséquilibre : {abs(len(x_positive) - len(x_negative))} points d'écart")


# VÉRIFICATION GÉOMÉTRIQUE : existence du symétrique
# Pour chaque point P = (x, y), on cherche si son image miroir
# S = (-x, y) existe bien dans le maillage à la tolérance tol près.


missing = []

for p in pts: # pts is an array of coordinates
    sym   = np.array([-p[0], p[1]])                    # image par symétrie x -> -x
    dists = np.linalg.norm(pts - sym, axis=1)          # distances à tous les points
    if dists.min() > TOL:
        missing.append(p)                              # aucun point assez proche du symétrique de p

if len(missing) == 0:
    print("Maillage parfaitement symétrique")
else:
    print(f"Erreur {len(missing)} points sans symétrique :")
    for p in missing[:20]:   # on affiche au maximum les 20 premiers pour ne pas surcharger
        print(f"   ({p[0]:.6f}, {p[1]:.6f})")

# On vérifie l'orientation des triangles du maillage en calculant leur aire signée.
n_neg = 0
for cell_block in mesh.cells:
    if cell_block.type == "triangle":
        for tri in cell_block.data:
            p0, p1, p2 = pts[tri[0]], pts[tri[1]], pts[tri[2]] # Récupération des coordonnées des 3 sommets
            # Aire signée via produit vectoriel
            area = 0.5 * ((p1[0]-p0[0])*(p2[1]-p0[1]) - (p2[0]-p0[0])*(p1[1]-p0[1]))
            if area < 0:
                n_neg += 1

print(f"Triangles aire négative : {n_neg}")
print(f"Triangles aire positive : {sum(len(b.data) for b in mesh.cells if b.type=='triangle') - n_neg}")
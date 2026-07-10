import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# =====================================================
# Gmsh geometry: cylindrical half-shell with holes
# =====================================================

R1 = 5.0      # Outer radius
R2 = 3.0      # Inner radius
H = 14.0      # Height along the z-axis
h = 0.25

rt = 0.3
y_pos = -0.7

eps = 0.20
z_bas = 0.5
z_haut = H - 0.5

# =====================================================
# Points to visualize: 5 points on the outer boundary
# =====================================================

X_pts = np.array([-5.0, -4.0, 0.0, 4.0, 5.0])
Y_pts = np.array([0.0, -3.0, -5.0, -3.0, 0.0])
Z_pts = np.linspace(1.0, H - 1.0, len(X_pts))

# =====================================================
# Display resolution
# =====================================================

n_theta = 180
n_z = 180
n_r = 80
n_phi = 80
n_x = 80

# =====================================================
# Hole positions, as defined in the .geo file
# =====================================================

x_outer_left = -np.sqrt(R1**2 - y_pos**2)
x_inner_left = -np.sqrt(R2**2 - y_pos**2)
x_start_left = x_outer_left - eps
dx_left = (x_inner_left - x_outer_left) + 2 * eps
x_end_left = x_start_left + dx_left

x_inner_right = np.sqrt(R2**2 - y_pos**2)
x_outer_right = np.sqrt(R1**2 - y_pos**2)
x_start_right = x_inner_right - eps
dx_right = (x_outer_right - x_inner_right) + 2 * eps
x_end_right = x_start_right + dx_right

holes = [
    (x_start_left, x_end_left, y_pos, z_haut, "201"),
    (x_start_left, x_end_left, y_pos, z_bas, "202"),
    (x_start_right, x_end_right, y_pos, z_haut, "203"),
    (x_start_right, x_end_right, y_pos, z_bas, "204"),
]

print(
    f"LEFT  : x_start={x_start_left:.6g}, "
    f"dx={dx_left:.6g}, x_end={x_end_left:.6g}"
)
print(
    f"RIGHT : x_start={x_start_right:.6g}, "
    f"dx={dx_right:.6g}, x_end={x_end_right:.6g}"
)

# =====================================================
# Utility functions
# =====================================================

def mask_holes_on_surface(X, Y, Z):
    mask = np.zeros_like(X, dtype=bool)

    for x0, x1, y0, z0, _ in holes:
        in_x_range = (X >= min(x0, x1)) & (X <= max(x0, x1))
        in_cyl = (Y - y0)**2 + (Z - z0)**2 <= rt**2
        mask |= in_x_range & in_cyl

    return mask


def plot_surface_with_holes(ax, X, Y, Z, color, alpha):
    mask = mask_holes_on_surface(X, Y, Z)

    Xp = np.where(mask, np.nan, X)
    Yp = np.where(mask, np.nan, Y)
    Zp = np.where(mask, np.nan, Z)

    ax.plot_surface(
        Xp,
        Yp,
        Zp,
        color=color,
        alpha=alpha,
        linewidth=0,
        antialiased=True,
        shade=True
    )


def plot_tunnel_wall(
    ax,
    x0,
    x1,
    y0,
    z0,
    radius,
    color="crimson",
    alpha=0.85
):
    x = np.linspace(x0, x1, n_x)
    phi = np.linspace(0, 2 * np.pi, n_phi)

    X, PHI = np.meshgrid(x, phi)
    Y = y0 + radius * np.cos(PHI)
    Z = z0 + radius * np.sin(PHI)

    ax.plot_surface(
        X,
        Y,
        Z,
        color=color,
        alpha=alpha,
        linewidth=0,
        antialiased=True,
        shade=True
    )


def plot_y0_plane(ax, x_min, x_max, color, alpha):
    x = np.linspace(x_min, x_max, 2)
    z = np.linspace(0, H, n_z)

    X, Z = np.meshgrid(x, z)
    Y = np.zeros_like(X)

    ax.plot_surface(
        X,
        Y,
        Z,
        color=color,
        alpha=alpha,
        linewidth=0,
        shade=True
    )


def point_in_shell(x, y, z):
    r = np.sqrt(x**2 + y**2)

    # Half-shell condition
    inside_main = (
        (R2 <= r <= R1)
        and (y <= 0.0)
        and (0.0 <= z <= H)
    )

    if not inside_main:
        return False

    # Exclude points located inside a hole
    for x0, x1, y0, z0, _ in holes:
        in_x_range = min(x0, x1) <= x <= max(x0, x1)
        in_cylinder = (y - y0)**2 + (z - z0)**2 <= rt**2

        if in_x_range and in_cylinder:
            return False

    return True


# =====================================================
# 3D figure
# =====================================================

fig = plt.figure(figsize=(13, 10))
ax = fig.add_subplot(111, projection="3d")

# =====================================================
# Outer and inner surfaces
# =====================================================

theta = np.linspace(np.pi, 2 * np.pi, n_theta)
z = np.linspace(0, H, n_z)

TH, ZZ = np.meshgrid(theta, z)

X_outer = R1 * np.cos(TH)
Y_outer = R1 * np.sin(TH)
Z_outer = ZZ

X_inner = R2 * np.cos(TH)
Y_inner = R2 * np.sin(TH)
Z_inner = ZZ

plot_surface_with_holes(
    ax,
    X_outer,
    Y_outer,
    Z_outer,
    color="lightsteelblue",
    alpha=0.40
)

plot_surface_with_holes(
    ax,
    X_inner,
    Y_inner,
    Z_inner,
    color="lightgreen",
    alpha=0.45
)

# =====================================================
# Top and bottom faces
# =====================================================

r = np.linspace(R2, R1, n_r)
theta_cap = np.linspace(np.pi, 2 * np.pi, n_theta)

RR, TH_CAP = np.meshgrid(r, theta_cap)

X_cap = RR * np.cos(TH_CAP)
Y_cap = RR * np.sin(TH_CAP)

Z_bottom = np.zeros_like(X_cap)
Z_top = H * np.ones_like(X_cap)

ax.plot_surface(
    X_cap,
    Y_cap,
    Z_bottom,
    color="silver",
    alpha=0.55,
    linewidth=0,
    shade=True
)

ax.plot_surface(
    X_cap,
    Y_cap,
    Z_top,
    color="gold",
    alpha=0.40,
    linewidth=0,
    shade=True
)

# =====================================================
# Left and right planar faces
# =====================================================

plot_y0_plane(ax, -R1, -R2, color="lightgray", alpha=0.55)
plot_y0_plane(ax, R2, R1, color="lightgray", alpha=0.55)

# =====================================================
# Holes
# =====================================================

for x0, x1, y0, z0, label in holes:
    plot_tunnel_wall(
        ax,
        x0,
        x1,
        y0,
        z0,
        rt,
        color="crimson",
        alpha=0.85
    )

    ax.plot(
        [x0, x1],
        [y0, y0],
        [z0, z0],
        color="black",
        linestyle="--",
        linewidth=1.0
    )

    ax.text(
        0.5 * (x0 + x1),
        y0 - 0.35,
        z0,
        label,
        fontsize=9
    )

# =====================================================
# Edges
# =====================================================

for zz in [0, H]:
    ax.plot(
        R1 * np.cos(theta),
        R1 * np.sin(theta),
        zz,
        color="navy",
        linewidth=1.3
    )

    ax.plot(
        R2 * np.cos(theta),
        R2 * np.sin(theta),
        zz,
        color="darkgreen",
        linewidth=1.3
    )

for zz in [0, H]:
    ax.plot(
        [-R1, -R2],
        [0, 0],
        [zz, zz],
        color="black",
        linewidth=1.2
    )

    ax.plot(
        [R2, R1],
        [0, 0],
        [zz, zz],
        color="black",
        linewidth=1.2
    )

for xx in [-R1, -R2, R2, R1]:
    ax.plot(
        [xx, xx],
        [0, 0],
        [0, H],
        color="black",
        linewidth=1.0
    )

# =====================================================
# Point display
# =====================================================

inside_x, inside_y, inside_z = [], [], []
outside_x, outside_y, outside_z = [], [], []

for i, (xp, yp, zp) in enumerate(zip(X_pts, Y_pts, Z_pts)):
    inside = point_in_shell(xp, yp, zp)

    if inside:
        inside_x.append(xp)
        inside_y.append(yp)
        inside_z.append(zp)
    else:
        outside_x.append(xp)
        outside_y.append(yp)
        outside_z.append(zp)

    ax.text(
        xp + 0.08,
        yp + 0.08,
        zp + 0.08,
        f"P{i}",
        fontsize=9
    )

# Points inside the shell
if inside_x:
    ax.scatter(
        inside_x,
        inside_y,
        inside_z,
        color="limegreen",
        s=55,
        depthshade=True
    )

# Points outside the shell
if outside_x:
    ax.scatter(
        outside_x,
        outside_y,
        outside_z,
        color="red",
        s=55,
        depthshade=True
    )

# =====================================================
# Console information
# =====================================================

print("\nPoint classification:")

for i, (xp, yp, zp) in enumerate(zip(X_pts, Y_pts, Z_pts)):
    rr = np.sqrt(xp**2 + yp**2)

    status = (
        "INSIDE the shell"
        if point_in_shell(xp, yp, zp)
        else "OUTSIDE the shell"
    )

    print(
        f"P{i}: (x={xp:.2f}, y={yp:.2f}, z={zp:.2f}), "
        f"r={rr:.3f} -> {status}"
    )

# =====================================================
# Figure formatting
# =====================================================

ax.set_title("Points selected in 3D", pad=18)

ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")

ax.set_xlim(-R1 - 0.8, R1 + 0.8)
ax.set_ylim(-R1 - 0.8, 1.0)
ax.set_zlim(-0.5, H + 0.5)

ax.set_box_aspect((2 * R1, R1 + 1, H))
ax.view_init(elev=20, azim=90)

legend_elements = [
    Patch(
        facecolor="lightsteelblue",
        alpha=0.40,
        label="External surface"
    ),
    Patch(
        facecolor="lightgreen",
        alpha=0.45,
        label="Internal surface"
    ),
    Patch(
        facecolor="silver",
        alpha=0.55,
        label="Face z = 0"
    ),
    Patch(
        facecolor="gold",
        alpha=0.40,
        label="Face z = H"
    ),
    Patch(
        facecolor="crimson",
        alpha=0.85,
        label="Holes"
    ),
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Points inside",
        markerfacecolor="limegreen",
        markersize=8
    ),
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Points outside",
        markerfacecolor="red",
        markersize=8
    ),
]

ax.legend(handles=legend_elements, loc="upper left")

plt.tight_layout()
plt.savefig(
    "visualisation_3D_points.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()
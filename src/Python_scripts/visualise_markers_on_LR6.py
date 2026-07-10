import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle

test_case = input("Enter the test case to visualize (LR6 or LR6_bigger): ").strip()

h = 0.01
r2 = 0.85
r1 = 1.0
rh = 0.02
yh = -0.10

angleA = -94.5 * np.pi / 180.0
angleB = -85.5 * np.pi / 180.0

X = np.array([-0.953, 0.89,  0.998])

Y = np.array([-0.3, -0.455, -0.05])

if test_case == "LR6_bigger":
    X = 5 * X
    Y = 5 * Y

    h = 0.075
    r2 = 3.5
    r1 = 5.0

    rh = 0.25
    yh = -1.0

    angleA = -91.8 * np.pi / 180.0
    angleB = -88.2 * np.pi / 180.0

    print(X)
    print(Y)

elif test_case != "LR6":
    raise ValueError("Invalid test case. Choose 'LR6' or 'LR6_bigger'.")

angleA2 = angleA % (2 * np.pi)
angleB2 = angleB % (2 * np.pi)

c1 = r2 + (r1 - r2) * 0.5
c2 = -c1

theta_outer = np.linspace(np.pi, 2 * np.pi, 400)

theta_inner_left = np.linspace(np.pi, angleA2, 150)
theta_inner_mid = np.linspace(angleA2, angleB2, 80)
theta_inner_right = np.linspace(angleB2, 2 * np.pi, 150)

x_outer = r1 * np.cos(theta_outer)
y_outer = r1 * np.sin(theta_outer)

x_inner_left = r2 * np.cos(theta_inner_left)
y_inner_left = r2 * np.sin(theta_inner_left)

x_inner_mid = r2 * np.cos(theta_inner_mid)
y_inner_mid = r2 * np.sin(theta_inner_mid)

x_inner_right = r2 * np.cos(theta_inner_right)
y_inner_right = r2 * np.sin(theta_inner_right)

right_outer = (r1, 0.0)
right_inner = (r2, 0.0)

left_inner = (-r2, 0.0)
left_outer = (-r1, 0.0)

fig, ax = plt.subplots(figsize=(9, 9))

domain_patch = Wedge(
    center=(0, 0),
    r=r1,
    theta1=180,
    theta2=360,
    width=(r1 - r2),
    alpha=0.20
)
ax.add_patch(domain_patch)

hole_right_fill = Circle((c1, yh), rh, facecolor="white", edgecolor="none", zorder=2)
hole_left_fill = Circle((c2, yh), rh, facecolor="white", edgecolor="none", zorder=2)

ax.add_patch(hole_right_fill)
ax.add_patch(hole_left_fill)

ax.plot(x_outer, y_outer, lw=2, zorder=3)

ax.plot([right_outer[0], right_inner[0]], [right_outer[1], right_inner[1]], lw=2, zorder=3)
ax.plot([left_inner[0], left_outer[0]], [left_inner[1], left_outer[1]], lw=2, zorder=3)

ax.plot(x_inner_left, y_inner_left, lw=2, zorder=3)
ax.plot(x_inner_right, y_inner_right, lw=2, zorder=3)

ax.plot(x_inner_mid, y_inner_mid, lw=4, zorder=4)

hole_right = Circle((c1, yh), rh, fill=False, lw=2, linestyle="--", zorder=4)
hole_left = Circle((c2, yh), rh, fill=False, lw=2, linestyle="--", zorder=4)

ax.add_patch(hole_right)
ax.add_patch(hole_left)

offset = 0.03 * r1

ax.scatter(X, Y, s=60, marker="o", zorder=5)

for i, (x, y) in enumerate(zip(X, Y)):
    ax.text(x + offset, y + offset, f"P{i}", fontsize=9, zorder=6)

ax.set_title(f"Points in the 2D domain {test_case}")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)
ax.set_aspect("equal")

margin = 0.1 * r1
ax.set_xlim(-r1 - margin, r1 + margin)
ax.set_ylim(-r1 - margin, 0.15 * r1)

plt.savefig(f"visualise_markers_{test_case}.png", dpi=300, bbox_inches="tight")
plt.show()
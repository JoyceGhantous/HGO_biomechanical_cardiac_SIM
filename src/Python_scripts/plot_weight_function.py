import numpy as np
import matplotlib.pyplot as plt

p = int(input("Enter exponent p for the discrete weighted L2 norm, p >= 0 : "))

if p < 0:
    raise ValueError("p doit être >= 0")

x = 5.0 * np.array([
    -0.925, -0.92, -0.788, -0.651, -0.465, -0.24,
     0.24,  0.465,  0.651,  0.788,  0.92,  0.925
])

denominateur = np.sum(np.abs(x)**p)

y = np.abs(x)**p / denominateur

idx = np.argsort(x)
x_sorted = x[idx]
y_sorted = y[idx]

plt.figure(figsize=(8, 5))
plt.scatter(x_sorted, y_sorted, label=r"$w_i=\frac{|x_i|^p}{\sum_j |x_j|^p}$")
plt.plot(x_sorted, y_sorted, linestyle="--", alpha=0.6)

plt.xlabel("x")
plt.ylabel("w_i")
plt.title(f"Plot of the weights for p = {p}")
plt.grid(True)
plt.legend()
plt.savefig(f"weight_function_plot_p_{p}.png", dpi=300, bbox_inches="tight")
plt.show()
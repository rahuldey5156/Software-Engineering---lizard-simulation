"""Generate a performance graph from experiment results."""
import matplotlib.pyplot as plt
import numpy as np

cells = [100, 400, 900, 1600, 2500, 3600, 4900, 6400, 8100, 10000]
means = [0.154, 0.148, 0.214, 0.286, 0.358, 0.430, 0.520, 0.610, 0.756, 0.888]
mins  = [0.118, 0.139, 0.195, 0.251, 0.334, 0.416, 0.496, 0.567, 0.733, 0.870]
maxs  = [0.221, 0.153, 0.246, 0.311, 0.386, 0.448, 0.554, 0.639, 0.781, 0.909]

lower_err = [m - mn for m, mn in zip(means, mins)]
upper_err = [mx - m for m, mx in zip(means, maxs)]

plt.figure(figsize=(9, 5))
plt.errorbar(cells, means, yerr=[lower_err, upper_err],
             fmt='o-', capsize=5, color='steelblue',
             label='Mean runtime (5 runs)')
plt.xlabel('Grid size (number of cells)')
plt.ylabel('Runtime (seconds)')
plt.title('Simulation Runtime vs Grid Size\n(100 timesteps, all-land landscape, default parameters)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('results/runtime_vs_gridsize.png', dpi=150)
print("Saved results/runtime_vs_gridsize.png")

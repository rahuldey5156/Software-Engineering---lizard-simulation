"""Generate a bar chart of coefficient of variation across grid sizes."""
import os
import numpy as np
import matplotlib.pyplot as plt

sizes = ['10×10', '20×20', '30×30', '40×40', '50×50',
         '60×60', '70×70', '80×80', '90×90', '100×100']
cells = [100, 400, 900, 1600, 2500, 3600, 4900, 6400, 8100, 10000]

runs = [
    [0.221, 0.136, 0.118, 0.144, 0.154],
    [0.153, 0.148, 0.139, 0.152, 0.148],
    [0.195, 0.246, 0.209, 0.224, 0.197],
    [0.289, 0.300, 0.251, 0.280, 0.311],
    [0.352, 0.346, 0.334, 0.386, 0.371],
    [0.416, 0.448, 0.418, 0.421, 0.445],
    [0.501, 0.544, 0.496, 0.505, 0.554],
    [0.609, 0.638, 0.639, 0.567, 0.596],
    [0.781, 0.757, 0.735, 0.775, 0.733],
    [0.876, 0.908, 0.909, 0.877, 0.870],
]

means = [np.mean(r) for r in runs]
stds = [np.std(r) for r in runs]
cvs = [std / mean * 100 for std, mean in zip(stds, means)]

colors = ['#e74c3c' if cv > 10 else '#2ecc71' for cv in cvs]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(sizes, cvs, color=colors, edgecolor='white', linewidth=0.5)
ax.axhline(y=10, color='red', linestyle='--', linewidth=1,
           label='10% threshold')
ax.axhline(y=5, color='orange', linestyle='--', linewidth=1,
           label='5% threshold')

ax.set_xlabel('Grid Size')
ax.set_ylabel('Coefficient of Variation (%)')
ax.set_title(
    'Measurement Reliability: Coefficient of Variation by Grid Size\n'
    '(5 runs per configuration, lower CV = more reliable)',
    fontsize=11
)
ax.legend()
ax.set_ylim(0, max(cvs) * 1.2)

for bar, cv in zip(bars, cvs):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
            f'{cv:.1f}%', ha='center', va='bottom', fontsize=8)

plt.xticks(rotation=30, ha='right')
plt.tight_layout()
os.makedirs('results', exist_ok=True)
plt.savefig('results/cv_by_gridsize.png', dpi=150)
print("Saved results/cv_by_gridsize.png")

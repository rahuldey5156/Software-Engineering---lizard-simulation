"""Generate a pie chart of profiling results by function."""
import os
import matplotlib.pyplot as plt

# Profiling data from cProfile run on 100x100 landscape, 100 timesteps
functions = [
    'find_nearest()',
    'move_insects()',
    'move_lizards()',
    'grow_berries()',
    'calculate_average_distance()',
    'write_ppm()',
    'other',
]
times = [0.914, 0.064, 0.067, 0.270, 0.142, 0.016, 0.156 + 0.039 + 0.036 + 0.032 + 0.028 + 0.024 + 0.004 + 0.005 + 0.004]

colors = [
    '#e74c3c', '#3498db', '#2ecc71', '#f39c12',
    '#9b59b6', '#1abc9c', '#95a5a6'
]

fig, ax = plt.subplots(figsize=(9, 6))
wedges, texts, autotexts = ax.pie(
    times,
    labels=functions,
    autopct='%1.1f%%',
    colors=colors,
    startangle=140,
    pctdistance=0.82
)
for text in texts:
    text.set_fontsize(10)
for autotext in autotexts:
    autotext.set_fontsize(9)

ax.set_title(
    'Simulation Runtime by Function\n'
    '(100×100 landscape, 100 timesteps, cProfile)',
    fontsize=12
)
plt.tight_layout()
os.makedirs('results', exist_ok=True)
plt.savefig('results/profiling_breakdown.png', dpi=150)
print("Saved results/profiling_breakdown.png")

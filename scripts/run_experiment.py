"""
Run the performance experiment: measure simulation runtime across grid sizes.
Each grid size is run 5 times with different seeds to assess reliability.
Results are printed as CSV to stdout.
"""
import subprocess
import time
import os

sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
runs_per_size = 5

print("Size,Cells,Run1,Run2,Run3,Run4,Run5,Mean,Min,Max")

for n in sizes:
    landscape = f"landscapes/experiment/{n}x{n}.dat"
    times = []
    for run in range(runs_per_size):
        start = time.perf_counter()
        subprocess.run(
            ["python3", "-m", "insect.simulate_insect",
             "-f", landscape,
             "-s", str(run + 1),
             "-x", "100",
             "-o", "9999"],
            capture_output=True
        )
        elapsed = time.perf_counter() - start
        times.append(elapsed)

    mean = sum(times) / len(times)
    print(f"{n}x{n},{n*n}," +
          ",".join(f"{t:.3f}" for t in times) +
          f",{mean:.3f},{min(times):.3f},{max(times):.3f}")

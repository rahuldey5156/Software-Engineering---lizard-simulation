"""Generate square all-land landscape files for the performance experiment."""
import os

sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
out_dir = "landscapes/experiment"
os.makedirs(out_dir, exist_ok=True)

for n in sizes:
    filename = os.path.join(out_dir, f"{n}x{n}.dat")
    with open(filename, "w") as f:
        f.write(f"{n} {n}\n")
        for row in range(n):
            f.write(" ".join(["1"] * n) + "\n")
    print(f"Created {filename}")

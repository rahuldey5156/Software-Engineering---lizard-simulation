# Performance Experiment: Effect of Grid Size on Simulation Runtime

## Introduction

This experiment investigates how the size of the landscape grid affects the
runtime of the lizard-insect-berry simulation. Understanding this relationship
is important for predicting how the simulation will scale to larger, more
realistic landscapes.

The simulation performs several operations each timestep whose cost is expected
to grow with grid size. Specifically:

- The main loop iterates over every cell in the grid to update entity states,
  giving an O(N) cost per timestep where N is the number of cells.
- The BFS used for insect and lizard movement explores cells outward from each
  animal. In the worst case, BFS explores the entire grid, giving O(N) cost
  per animal per timestep.
- The statistics and PPM output at each output interval also iterate over all
  cells.

**Hypothesis**: Total runtime will scale super-linearly with the number of
grid cells, because both the number of animals and the BFS search space grow
with grid size. Specifically, we expect runtime to grow approximately as
O(N^1.5) or O(N^2) where N is the number of cells.

## Method

### Environment

- **Hardware**: Apple MacBook (Apple Silicon)
- **OS**: macOS
- **Python version**: 3.11.14 (Anaconda distribution)
- **Key packages**: numpy, collections.deque

### Experimental Design

Square all-land landscape files were generated for sizes from 10×10 to
100×100 in steps of 10 (i.e. 100 to 10,000 cells). All-land landscapes
were used to eliminate the effect of water on BFS search paths and to
ensure that the number of land cells is exactly equal to the grid size.
This gives a clean, controlled variable.

All other simulation parameters were held fixed:

| Parameter | Value | Reason |
|-----------|-------|--------|
| Timesteps (`-x`) | 100 | Long enough to measure reliably |
| Output interval (`-o`) | 9999 | Suppresses file output overhead |
| Berry proportion (`-b`) | 0.05 (default) | Standard conditions |
| Insect proportion (`-i`) | 0.08 (default) | Standard conditions |
| Lizard proportion (`-l`) | 0.01 (default) | Standard conditions |
| Insect move interval (`-j`) | 5 (default) | Standard conditions |
| Lizard move interval (`-m`) | 2 (default) | Standard conditions |
| Lizard view radius (`-n`) | 3 (default) | Standard conditions |

Each configuration was run **5 times** with different random seeds (1–5) to
assess the reliability and variability of the measurements. The mean, minimum
and maximum runtime across the 5 runs are reported.

Landscape files were generated using `scripts/generate_landscapes.py` and
the experiment was run using `scripts/run_experiment.py`. To reproduce:

```console
$ python3 scripts/generate_landscapes.py
$ python3 scripts/run_experiment.py
```

## Results

| Size | Cells | Run 1 | Run 2 | Run 3 | Run 4 | Run 5 | Mean | Min | Max |
|------|-------|-------|-------|-------|-------|-------|------|-----|-----|
| 10×10 | 100 | 0.221 | 0.136 | 0.118 | 0.144 | 0.154 | 0.154 | 0.118 | 0.221 |
| 20×20 | 400 | 0.153 | 0.148 | 0.139 | 0.152 | 0.148 | 0.148 | 0.139 | 0.153 |
| 30×30 | 900 | 0.195 | 0.246 | 0.209 | 0.224 | 0.197 | 0.214 | 0.195 | 0.246 |
| 40×40 | 1600 | 0.289 | 0.300 | 0.251 | 0.280 | 0.311 | 0.286 | 0.251 | 0.311 |
| 50×50 | 2500 | 0.352 | 0.346 | 0.334 | 0.386 | 0.371 | 0.358 | 0.334 | 0.386 |
| 60×60 | 3600 | 0.416 | 0.448 | 0.418 | 0.421 | 0.445 | 0.430 | 0.416 | 0.448 |
| 70×70 | 4900 | 0.501 | 0.544 | 0.496 | 0.505 | 0.554 | 0.520 | 0.496 | 0.554 |
| 80×80 | 6400 | 0.609 | 0.638 | 0.639 | 0.567 | 0.596 | 0.610 | 0.567 | 0.639 |
| 90×90 | 8100 | 0.781 | 0.757 | 0.735 | 0.775 | 0.733 | 0.756 | 0.733 | 0.781 |
| 100×100 | 10000 | 0.876 | 0.908 | 0.909 | 0.877 | 0.870 | 0.888 | 0.870 | 0.909 |

All times are in seconds. The variability across runs (Max - Min) is small
relative to the mean for all grid sizes, confirming that 5 runs is sufficient
to obtain reliable measurements.

The relationship between grid size and mean runtime is shown below. Note that
the 10×10 result shows higher variability than larger grids, which is expected
at this scale where Python startup and import overhead dominate over simulation
computation.

![Runtime vs Grid Size](results/runtime_vs_gridsize.png)

## Discussion

The results clearly show that runtime increases with grid size, consistent
with the hypothesis. However, the relationship is sub-linear rather than
super-linear over this range. Specifically, going from 100 cells (10×10) to
10,000 cells (100×100) — a 100× increase in cells — produces only a roughly
6× increase in mean runtime (0.154s to 0.888s).

This can be explained by examining the specific code:

**Dominant cost: nested loops over all cells.** The main simulation loop in
`sim()` contains multiple nested `for row / for col` loops that iterate over
every cell each timestep. This gives O(N) cost per timestep where N is the
number of cells, which is consistent with the approximately linear growth
observed in the results.

**BFS cost is bounded in practice.** While BFS has a worst-case cost of O(N)
per animal, the lizard view radius parameter (`-n`, default 3) limits the
lizard BFS to at most a small diamond of cells regardless of grid size. Insect
BFS is unlimited but terminates as soon as the nearest berry is found, so in
practice it rarely explores the whole grid. This explains why the overall
scaling is closer to O(N) than the O(N^2) worst case.

**Python startup overhead dominates at small scales.** The 10×10 result has
higher relative variability (0.118s to 0.221s) because at this scale, Python
interpreter startup and module import time (numpy, argparse etc.) make up a
significant fraction of the total measured time. This effect diminishes as
grid size grows.

**The simulation is CPU-bound at large scales.** At 100×100, the mean and
minimum times are very close (0.888s vs 0.870s), and variability is low,
confirming that the simulation is dominated by computation rather than
system overhead at this scale.

## Next Steps

1. **Extend to larger grid sizes.** The experiment only goes up to 100×100
   (10,000 cells). Running up to 500×500 or 1000×1000 would reveal whether
   the scaling remains linear or becomes super-linear as BFS searches cover
   larger areas and animal populations grow.

2. **Isolate the cost of BFS.** Profiling the simulation with `cProfile` would
   confirm whether `find_nearest()` or the main cell loops dominate runtime.
   This could be done by comparing runs with movement disabled (`-j` and `-m`
   set very high) against standard runs.

3. **Investigate the effect of lizard view radius.** The view radius parameter
   `n` directly controls the maximum BFS depth for lizards. Increasing `n`
   should increase runtime super-linearly as the search diamond grows. An
   experiment varying `n` from 1 to 20 on a fixed large grid would quantify
   this effect.

4. **Replace Python loops with NumPy vectorisation.** The nested cell loops
   are the dominant cost and could potentially be replaced with NumPy array
   operations, which are implemented in C and would give a significant speedup.
   This is the most promising optimisation for this program.

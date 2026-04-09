# Performance Experiment: Effect of Grid Size on Simulation Runtime

## Introduction

This experiment investigates how the size of the landscape grid affects the
runtime of the lizard-insect-berry simulation. Understanding this relationship
is important for predicting how the simulation will scale to larger, more
realistic landscapes.

The simulation performs several operations each timestep whose cost is expected
to grow with grid size. Specifically:

- The main simulation loop iterates over every cell in the grid to update
  entity states, giving an O(N) cost per timestep where N is the number of
  cells.
- The breadth-first search (BFS) used for insect and lizard movement explores
  cells outward from each animal. In the worst case, BFS explores the entire
  grid, giving O(N) cost per animal per timestep.
- The statistics and PPM output at each output interval also iterate over all
  cells.

**Hypothesis**: Total runtime will grow super-linearly with the number of grid
cells, because both the number of animals and the BFS search space grow with
grid size. Specifically, we expect runtime to grow approximately as O(N^1.5)
or O(N^2) where N is the number of cells.

## Method

### Environment

- **Hardware**: Apple MacBook (Apple Silicon)
- **Operating System**: macOS
- **Python version**: 3.11.14 (Anaconda distribution)
- **Key packages**: numpy, collections.deque

### Experimental Design

Square all-land landscape files were generated for grid sizes from 10×10 to
100×100 in steps of 10, giving grids of 100 to 10,000 cells. All-land
landscapes were chosen deliberately to eliminate the confounding effect of
water on BFS search paths and to ensure that the number of land cells equals
exactly the grid area. This gives a single clean, controlled independent
variable: grid size.

All other simulation parameters were held fixed across all runs:

| Parameter | Value | Reason |
|-----------|-------|--------|
| Timesteps (`-x`) | 100 | Long enough to obtain stable measurements |
| Output interval (`-o`) | 9999 | Suppresses file I/O overhead during timing |
| Berry proportion (`-b`) | 0.05 (default) | Standard simulation conditions |
| Insect proportion (`-i`) | 0.08 (default) | Standard simulation conditions |
| Lizard proportion (`-l`) | 0.01 (default) | Standard simulation conditions |
| Insect move interval (`-j`) | 5 (default) | Standard simulation conditions |
| Lizard move interval (`-m`) | 2 (default) | Standard simulation conditions |
| Lizard view radius (`-n`) | 3 (default) | Standard simulation conditions |

Each configuration was run **5 times** with different random seeds (1 to 5)
to assess the reliability and variability of the measurements. Using different
seeds ensures that the results are not specific to one particular arrangement
of animals, and that the mean runtime is representative of typical behaviour.
The mean, minimum and maximum runtime across the 5 runs are reported.

Runtime was measured using Python's `time.perf_counter()`, which provides
high-resolution wall-clock timing. The timer started immediately before the
simulation subprocess was launched and stopped immediately after it returned.

Landscape files were generated using `scripts/generate_landscapes.py` and
the experiment was timed using `scripts/run_experiment.py`. To reproduce
the full experiment:

```console
$ python3 scripts/generate_landscapes.py
$ python3 scripts/run_experiment.py
$ python3 scripts/plot_results.py
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
to obtain reliable measurements. The largest absolute variability is seen at
10×10 (0.103s range), which is expected at this scale as discussed below.

The relationship between grid size and mean runtime is shown in the figure
below, with error bars showing the minimum and maximum observed runtimes.

![Runtime vs Grid Size](results/runtime_vs_gridsize.png)

## Discussion

The results clearly show that runtime increases with grid size, which is
consistent with the hypothesis. However, the relationship is sub-linear rather
than super-linear over this range of grid sizes. Specifically, going from 100
cells (10×10) to 10,000 cells (100×100) — a 100-fold increase in cells —
produces only a roughly 6-fold increase in mean runtime (0.154s to 0.888s).
This can be explained by examining the specific code in `simulate_insect.py`.

**Dominant cost: nested cell loops.** The main simulation loop in `sim()`
contains multiple nested `for row / for col` loops that iterate over every
cell in the grid each timestep. This contributes an O(N) cost per timestep,
where N is the number of cells. With 100 fixed timesteps, this gives O(100N)
total, which is consistent with the approximately linear growth seen in the
results. For example, going from 10×10 (100 cells) to 50×50 (2,500 cells) —
a 25-fold increase — produces approximately a 2.3-fold increase in runtime,
which is closer to O(N^0.6) empirically, suggesting that fixed overheads still
play a role at these scales.

**BFS cost is bounded in practice.** While BFS has a worst-case cost of O(N)
per animal, two factors limit its cost in practice. First, the lizard view
radius parameter (`-n`, default 3) limits each lizard BFS to a small diamond
of at most 12 cells regardless of grid size. Second, insect BFS terminates as
soon as the nearest berry is found, so in practice it rarely explores the
whole grid. This explains why the overall scaling is closer to O(N) than the
O(N^2) worst case that would result if BFS explored the full grid for every
animal every timestep.

**Python startup overhead dominates at small scales.** The 10×10 result shows
the highest relative variability (0.118s to 0.221s, a range of 0.103s). At
this scale, Python interpreter startup and module import time (numpy, argparse,
collections etc.) make up a significant fraction of the total measured time,
causing high run-to-run variability. This effect diminishes as grid size grows
and computation dominates over startup time.

**The simulation is CPU-bound at large scales.** At 100×100, the variability
across runs is very low (0.870s to 0.909s, a range of only 0.039s), and the
mean and minimum are close together. This confirms that at this scale the
simulation is dominated by computation rather than system overhead or I/O,
and that 5 runs gives a reliable estimate of typical runtime.

## Next Steps

1. **Extend to larger grid sizes.** This experiment only covers up to 100×100
   (10,000 cells). Running up to 500×500 or 1,000×1,000 would reveal whether
   the approximately linear scaling continues or becomes super-linear as BFS
   searches cover larger areas and animal populations grow proportionally.

2. **Profile to isolate the cost of BFS.** Using Python's `cProfile` module
   would confirm whether `find_nearest()` or the main cell loops dominate
   runtime at each grid size. A simple comparison could be made by running
   with movement disabled (setting `-j` and `-m` to a value larger than the
   cutoff) against standard runs to isolate the BFS contribution.

3. **Investigate the effect of lizard view radius.** The view radius parameter
   `-n` directly controls the maximum BFS depth for lizards. Increasing `-n`
   should increase runtime as the search diamond grows quadratically with
   radius. An experiment varying `-n` from 1 to 20 on a fixed large grid would
   quantify this effect and determine whether it becomes the dominant cost at
   large radii.

4. **Replace Python loops with NumPy vectorisation.** The nested cell loops
   are the dominant cost and could potentially be replaced with NumPy array
   operations, which are implemented in C and avoid Python interpreter overhead
   for each cell. This is the most promising optimisation for this program and
   could give a significant speedup without changing the simulation logic.

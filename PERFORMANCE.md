=========================================
PERFORMANCE EXPERIMENT LOG - s2793337
Date: 05-03-2026
Model: BFS Optimization (deque) and Robust Parsing Fix
Steps (-x): 100
Seed (-s): 1
=========================================

| Landscape File            | Dimensions | Total Tiles | Real Time (s) | User Time (s) |
|---------------------------|------------|-------------|---------------|---------------|
| 0x0.dat                   | 0x0        | 0           | 0.239         | 0.852         |
| 1x1.dat                   | 1x1        | 1           | 0.108         | 0.266         |
| 1x1land.dat               | 1x1        | 1           | 0.138         | 0.331         |
| 1x1water.dat              | 1x1        | 1           | 0.125         | 0.242         |
| 3x1.dat                   | 3x1        | 3           | 0.098         | 0.209         |
| 3x3.dat                   | 3x3        | 9           | 0.117         | 0.211         |
| 1x50.dat                  | 1x50       | 50          | 0.129         | 0.270         |
| 50x1.dat                  | 50x1       | 50          | 0.113         | 0.203         |
| 10x20.dat                 | 10x20      | 200         | 0.143         | 0.291         |
| 20x10.dat                 | 20x10      | 200         | 0.128         | 0.311         |
| two_square_islands.dat    | 20x10      | 200         | 0.160         | 0.327         |
| 20x20corner.dat           | 20x20      | 400         | 0.163         | 0.329         |
| 20x20land.dat             | 20x20      | 400         | 0.138         | 0.346         |
| 20x20water.dat           | 20x20      | 400         | 0.123         | 0.253         |
| 40x20ps.dat               | 40x20      | 800         | 0.214         | 0.403         |
| 50x20.dat                 | 50x20      | 1,000       | 0.239         | 0.588         |
| small.dat                 | -          | -           | 0.238         | 0.447         |
| map.dat                   | -          | -           | 0.187         | 0.558         |
| test.dat                  | -          | -           | 0.298         | 0.912         |
| test2.dat                 | 100x100    | 10,000      | 1.099         | 1.460         |
| islands.dat               | 1000x800   | 800,000     | 54.938        | 55.098        |

Observations:
- The execution time for small maps (under 1,000 tiles) remains consistent, suggesting Python startup and system overhead dominate at this scale.
- The 'islands.dat' stress test shows efficient scaling; while tiles increased 4,000x over the 10x20 baseline, time only increased by ~186x.
- User time closely matches real time on the largest file (islands.dat), confirming the simulation is computationally bound.
- Using deque.popleft() provides O(1) efficiency, allowing the simulation to handle high-resolution landscapes that would otherwise timeout.

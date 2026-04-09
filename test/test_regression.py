import subprocess
import os
import numpy as np
import pytest
from insect import simulate_insect

# ── Unit tests ──────────────────────────────────────────────────────────────

def test_get_version():
    assert simulate_insect.getVersion() == 1.0


def test_find_nearest_finds_berry():
    """BFS should find a berry directly to the right."""
    # 3x3 grid with halo = 5x5. Halo edges are water (0).
    lscape = np.ones((5, 5), int)
    lscape[0, :] = 0
    lscape[4, :] = 0
    lscape[:, 0] = 0
    lscape[:, 4] = 0
    grid = np.zeros((5, 5), int)
    # Place a berry at (2, 3) — one step to the right of (2, 2)
    grid[2, 3] = 1
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), 1)
    assert (dx, dy) == (0, 1)


def test_find_nearest_no_target():
    """BFS should return (0, 0) when no target exists."""
    lscape = np.ones((5, 5), int)
    lscape[0, :] = 0
    lscape[4, :] = 0
    lscape[:, 0] = 0
    lscape[:, 4] = 0
    grid = np.zeros((5, 5), int)
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), 1)
    assert (dx, dy) == (0, 0)


def test_find_nearest_respects_max_dist():
    """BFS should return (0, 0) when target is beyond max_dist."""
    # 5x5 grid with halo = 7x7
    lscape = np.ones((7, 7), int)
    lscape[0, :] = 0
    lscape[6, :] = 0
    lscape[:, 0] = 0
    lscape[:, 6] = 0
    grid = np.zeros((7, 7), int)
    # Place berry 4 steps away from (3, 1) at (3, 5)
    grid[3, 5] = 1
    dx, dy = simulate_insect.find_nearest(lscape, grid, (3, 1), 1, max_dist=2)
    assert (dx, dy) == (0, 0)


def test_find_nearest_respects_water():
    """BFS should not cross water cells."""
    lscape = np.ones((5, 5), int)
    lscape[0, :] = 0
    lscape[4, :] = 0
    lscape[:, 0] = 0
    lscape[:, 4] = 0
    # Block all paths to column 3 on row 2
    lscape[1, 3] = 0
    lscape[2, 3] = 0
    lscape[3, 3] = 0
    grid = np.zeros((5, 5), int)
    # Berry is unreachable due to water wall
    grid[2, 3] = 1
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), 1)
    assert (dx, dy) == (0, 0)


# ── End-to-end regression test ───────────────────────────────────────────────

EXPECTED_AVERAGES = [
    (0,  5, 17, 4.412, 3, 3.667),
    (10, 3, 14, 10.500, 3, 3.000),
    (20, 6, 10, 4.800, 3, 5.667),
    (30, 7,  9, 2.667, 3, 8.000),
    (40, 6,  9, 4.778, 3, 8.000),
]

def test_simulation_matches_baseline():
    """Run simulation and verify averages.csv matches known-good baseline."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "landscapes/10x20.dat",
        "-s", "1",
        "-x", "50"
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)

    assert os.path.exists("averages.csv"), "averages.csv was not created"

    with open("averages.csv", "r") as f:
        lines = [l.strip() for l in f.readlines() if l.strip()]

    assert lines[0] == "Timestep,# Fruit,# Insects,Avg distance to berry,# Lizards, Avg distance to insect"

    data_lines = lines[1:]
    assert len(data_lines) == len(EXPECTED_AVERAGES), "Unexpected number of output rows"

    for line, (exp_t, exp_b, exp_i, exp_ai, exp_l, exp_al) in zip(data_lines, EXPECTED_AVERAGES):
        parts = line.split(",")
        assert int(parts[0]) == exp_t
        assert int(parts[1]) == exp_b
        assert int(parts[2]) == exp_i
        assert abs(float(parts[3]) - exp_ai) < 0.001
        assert int(parts[4]) == exp_l
        assert abs(float(parts[5]) - exp_al) < 0.001


def test_simulation_stdout():
    """Verify console output matches expected format and values."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "landscapes/10x20.dat",
        "-s", "1",
        "-x", "50"
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")

    assert lines[0] == "Insect simulation 1.0"
    assert lines[1] == "Width: 10 Height: 20"
    assert "Timestep: 0 Berries: 5 Insects: 17(4.412) Lizards: 3(3.667)" in lines[2]


def test_ppm_files_created():
    """Verify PPM files are created at correct timesteps."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "landscapes/10x20.dat",
        "-s", "1",
        "-x", "50"
    ]
    subprocess.run(cmd, check=True)
    for t in [0, 10, 20, 30, 40]:
        assert os.path.exists(f"map_{t:04d}.ppm"), f"map_{t:04d}.ppm not created"

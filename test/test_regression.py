import subprocess
import os
import math
import numpy as np
import pytest
from insect import simulate_insect

# ── Version test ─────────────────────────────────────────────────────────────

def test_get_version():
    """Version number should remain 1.0."""
    assert simulate_insect.getVersion() == 1.0


# ── find_nearest tests ───────────────────────────────────────────────────────

def make_landscape(height, width):
    """Helper: create a landscape with halo, all land inside."""
    lscape = np.zeros((height + 2, width + 2), int)
    lscape[1:height + 1, 1:width + 1] = 1
    return lscape


def test_find_nearest_finds_berry():
    """BFS should find a berry directly to the right."""
    lscape = make_landscape(3, 3)
    grid = np.zeros((5, 5), int)
    grid[2, 3] = simulate_insect.BERRY
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), simulate_insect.BERRY)
    assert (dx, dy) == (0, 1)


def test_find_nearest_no_target():
    """BFS should return (0, 0) when no target exists."""
    lscape = make_landscape(3, 3)
    grid = np.zeros((5, 5), int)
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), simulate_insect.BERRY)
    assert (dx, dy) == (0, 0)


def test_find_nearest_respects_max_dist():
    """BFS should return (0, 0) when target is beyond max_dist."""
    lscape = make_landscape(5, 5)
    grid = np.zeros((7, 7), int)
    grid[3, 5] = simulate_insect.BERRY  # 4 steps away from (3, 1)
    dx, dy = simulate_insect.find_nearest(lscape, grid, (3, 1), simulate_insect.BERRY, max_dist=2)
    assert (dx, dy) == (0, 0)


def test_find_nearest_respects_water():
    """BFS should not cross water cells."""
    lscape = make_landscape(3, 3)
    # Wall of water blocking column 3
    lscape[1, 3] = 0
    lscape[2, 3] = 0
    lscape[3, 3] = 0
    grid = np.zeros((5, 5), int)
    grid[2, 3] = simulate_insect.BERRY
    dx, dy = simulate_insect.find_nearest(lscape, grid, (2, 2), simulate_insect.BERRY)
    assert (dx, dy) == (0, 0)


def test_find_nearest_finds_insect_for_lizard():
    """Lizard BFS should find an insect within view radius."""
    lscape = make_landscape(3, 3)
    grid = np.zeros((5, 5), int)
    grid[2, 3] = simulate_insect.INSECT
    dx, dy = simulate_insect.find_nearest(
        lscape, grid, (2, 2), simulate_insect.INSECT, max_dist=3)
    assert (dx, dy) == (0, 1)


# ── load_landscape tests ─────────────────────────────────────────────────────

def test_load_landscape_dimensions(tmp_path):
    """Landscape dimensions should be read correctly from file."""
    f = tmp_path / "test.dat"
    f.write_text("3 2\n1 1 1\n0 1 0\n")
    landscape, width, height = simulate_insect.load_landscape(str(f))
    assert width == 3
    assert height == 2


def test_load_landscape_halo(tmp_path):
    """Landscape array should have a border of zeros (halo)."""
    f = tmp_path / "test.dat"
    f.write_text("3 2\n1 1 1\n0 1 0\n")
    landscape, width, height = simulate_insect.load_landscape(str(f))
    # Check all four halo edges are zero
    assert all(landscape[0, :] == 0), "Top halo row should be zero"
    assert all(landscape[-1, :] == 0), "Bottom halo row should be zero"
    assert all(landscape[:, 0] == 0), "Left halo column should be zero"
    assert all(landscape[:, -1] == 0), "Right halo column should be zero"


def test_load_landscape_values(tmp_path):
    """Landscape interior values should match the file contents."""
    f = tmp_path / "test.dat"
    f.write_text("3 2\n1 1 1\n0 1 0\n")
    landscape, width, height = simulate_insect.load_landscape(str(f))
    assert landscape[1, 1] == 1
    assert landscape[1, 2] == 1
    assert landscape[1, 3] == 1
    assert landscape[2, 1] == 0
    assert landscape[2, 2] == 1
    assert landscape[2, 3] == 0


def test_load_landscape_missing_file():
    """Loading a nonexistent file should exit with a non-zero code."""
    with pytest.raises(SystemExit) as exc:
        simulate_insect.load_landscape("nonexistent.dat")
    assert exc.value.code != 0


def test_load_landscape_all_water(tmp_path):
    """An all-water landscape should load without error."""
    f = tmp_path / "water.dat"
    f.write_text("3 3\n0 0 0\n0 0 0\n0 0 0\n")
    landscape, width, height = simulate_insect.load_landscape(str(f))
    assert width == 3
    assert height == 3
    assert landscape[1:4, 1:4].sum() == 0


# ── initialise_grid tests ────────────────────────────────────────────────────

def test_initialise_grid_shape():
    """Grid should have the same shape as the landscape."""
    lscape = make_landscape(5, 5)
    grid = simulate_insect.initialise_grid(lscape, 5, 5, 0.5, 0.5, 0.5, seed=1)
    assert grid.shape == lscape.shape


def test_initialise_grid_no_entities_on_water():
    """No entities should be placed on water cells."""
    lscape = make_landscape(5, 5)
    lscape[2, 2] = 0  # Make one cell water
    grid = simulate_insect.initialise_grid(lscape, 5, 5, 1.0, 1.0, 1.0, seed=1)
    assert grid[2, 2] == simulate_insect.EMPTY


def test_initialise_grid_zero_props():
    """With zero proportions, grid should remain empty."""
    lscape = make_landscape(5, 5)
    grid = simulate_insect.initialise_grid(lscape, 5, 5, 0.0, 0.0, 0.0, seed=1)
    assert grid.sum() == 0


def test_initialise_grid_reproducible():
    """Same seed should produce the same grid."""
    lscape = make_landscape(5, 5)
    grid1 = simulate_insect.initialise_grid(lscape, 5, 5, 0.3, 0.2, 0.1, seed=42)
    grid2 = simulate_insect.initialise_grid(lscape, 5, 5, 0.3, 0.2, 0.1, seed=42)
    assert np.array_equal(grid1, grid2)


def test_initialise_grid_halo_empty():
    """Halo border cells should always be empty after initialisation."""
    lscape = make_landscape(5, 5)
    grid = simulate_insect.initialise_grid(lscape, 5, 5, 1.0, 1.0, 1.0, seed=1)
    assert all(grid[0, :] == 0)
    assert all(grid[-1, :] == 0)
    assert all(grid[:, 0] == 0)
    assert all(grid[:, -1] == 0)


# ── collect_positions tests ──────────────────────────────────────────────────

def test_collect_positions_empty_grid():
    """Empty grid should return no positions."""
    lscape = make_landscape(3, 3)
    grid = np.zeros((5, 5), int)
    berries, insects, lizards = simulate_insect.collect_positions(grid, lscape, 3, 3)
    assert berries == []
    assert insects == []
    assert lizards == []


def test_collect_positions_counts():
    """collect_positions should find the correct number of each entity."""
    lscape = make_landscape(3, 3)
    grid = np.zeros((5, 5), int)
    grid[1, 1] = simulate_insect.BERRY
    grid[2, 2] = simulate_insect.INSECT
    grid[3, 3] = simulate_insect.LIZARD
    grid[1, 2] = simulate_insect.BERRY
    berries, insects, lizards = simulate_insect.collect_positions(grid, lscape, 3, 3)
    assert len(berries) == 2
    assert len(insects) == 1
    assert len(lizards) == 1


def test_collect_positions_ignores_water():
    """Entities on water cells should not be collected."""
    lscape = make_landscape(3, 3)
    lscape[2, 2] = 0  # Make cell water
    grid = np.zeros((5, 5), int)
    grid[2, 2] = simulate_insect.BERRY  # Place berry on water
    berries, insects, lizards = simulate_insect.collect_positions(grid, lscape, 3, 3)
    assert len(berries) == 0


# ── calculate_average_distance tests ─────────────────────────────────────────

def test_calculate_average_distance_simple():
    """Average distance should be correct for a simple case."""
    searchers = [(1, 1)]
    targets = [(1, 3)]
    avg = simulate_insect.calculate_average_distance(searchers, targets)
    assert abs(avg - 2.0) < 0.001


def test_calculate_average_distance_no_searchers():
    """Should return inf when there are no searchers."""
    avg = simulate_insect.calculate_average_distance([], [(1, 1)])
    assert avg == math.inf


def test_calculate_average_distance_no_targets():
    """Should return inf when there are no targets."""
    avg = simulate_insect.calculate_average_distance([(1, 1)], [])
    assert avg == math.inf


def test_calculate_average_distance_multiple():
    """Should correctly average distances across multiple searchers."""
    searchers = [(1, 1), (1, 2)]
    targets = [(1, 4)]
    # Distances: 3 and 2, average = 2.5
    avg = simulate_insect.calculate_average_distance(searchers, targets)
    assert abs(avg - 2.5) < 0.001


# ── End-to-end regression tests ──────────────────────────────────────────────

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


def test_all_water_landscape():
    """Simulation on all-water landscape should run without error."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "landscapes/20x20water.dat",
        "-s", "1",
        "-x", "10"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0


def test_invalid_landscape_file():
    """Simulation with missing landscape file should exit with error."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "nonexistent.dat",
        "-s", "1",
        "-x", "10"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Error" in result.stderr


def test_invalid_berry_prop():
    """Out-of-range berry proportion should exit with error."""
    cmd = [
        "python3", "-m", "insect.simulate_insect",
        "-f", "landscapes/10x20.dat",
        "-b", "1.5"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode != 0
    assert "Error" in result.stderr

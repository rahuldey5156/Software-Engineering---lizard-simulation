'''Lizard-insect-berry simulation.

Version 1.0, last updated in Feb 2026.
'''
import math
import random
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import deque
from dataclasses import dataclass

import numpy as np

# Entity type constants used in the grid state array
EMPTY = 0
BERRY = 1
INSECT = 2
LIZARD = 3

# Landscape cell constants
WATER = 0
LAND = 1

# Cardinal movement directions (row_delta, col_delta)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


@dataclass
class SimulationConfig:
    """
    Configuration parameters for the lizard-insect-berry simulation.

    Attributes:
        berry_prop (float): Initial probability of a berry in each land cell.
        berry_growth (float): Probability of a berry growing in an empty cell each timestep.
        insect_prop (float): Initial probability of an insect in each land cell.
        insect_move_ts (int): Number of timesteps between insect movements.
        lizard_prop (float): Initial probability of a lizard in each land cell.
        lizard_move_ts (int): Number of timesteps between lizard movements.
        lizard_view_radius (int): Maximum BFS search radius for lizards hunting insects.
        output_ts (int): Interval in timesteps between file and console outputs.
        cutoff (int): Total number of timesteps to simulate.
        landscape_file (str): Path to the input landscape file.
        seed (int): Random seed for reproducibility.
    """
    berry_prop: float = 0.05
    berry_growth: float = 0.001
    insect_prop: float = 0.08
    insect_move_ts: int = 5
    lizard_prop: float = 0.01
    lizard_move_ts: int = 2
    lizard_view_radius: int = 3
    output_ts: int = 10
    cutoff: int = 500
    landscape_file: str = ""
    seed: int = 1


def get_version():
    """Return the current version of the simulation."""
    return 1.0


# Keep original name as alias so existing tests pass
getVersion = get_version  # pylint: disable=invalid-name


def sim_comm_line_intf():
    """Parse command-line arguments and run the simulation."""
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-b", "--berry-prop", type=float, default=0.05,
                        help="Approximate proportion of landscape filled with berries")
    parser.add_argument("-c", "--berry-growth", type=float, default=0.001,
                        help="Approximate proportion of berries that appears each timestep")
    parser.add_argument("-i", "--insect-prop", type=float, default=0.08,
                        help="Approximate proportion of landscape filled with insects")
    parser.add_argument("-j", "--insect-move-ts", type=int, default=5,
                        help="Timesteps for insect movements")
    parser.add_argument("-l", "--lizard-prop", type=float, default=0.01,
                        help="Approximate proportion of landscape filled with lizards")
    parser.add_argument("-m", "--lizard-move-ts", type=int, default=2,
                        help="Timesteps for lizard movements")
    parser.add_argument("-n", "--lizard-view-radius", type=int, default=3,
                        help="Maximum number of cells lizards watch for insects")
    parser.add_argument("-o", "--output-ts", type=int, default=10,
                        help="Number of time steps at which to output files")
    parser.add_argument("-x", "--cutoff", type=int, default=500,
                        help="Maximum time to run the simulation (in timesteps)")
    parser.add_argument("-f", "--landscape-file", type=str, required=True,
                        help="Input landscape file")
    parser.add_argument("-s", "--seed", type=int, default=1,
                        help="Random seed for initialising locations and movement")
    args = parser.parse_args()

    # Validate probability parameters are in range [0, 1]
    for name, value in [("berry-prop", args.berry_prop),
                         ("berry-growth", args.berry_growth),
                         ("insect-prop", args.insect_prop),
                         ("lizard-prop", args.lizard_prop)]:
        if not 0.0 <= value <= 1.0:
            print(f"Error: --{name} must be between 0.0 and 1.0, got {value}",
                  file=sys.stderr)
            sys.exit(1)

    # Validate integer parameters are positive
    for name, value in [("insect-move-ts", args.insect_move_ts),
                         ("lizard-move-ts", args.lizard_move_ts),
                         ("lizard-view-radius", args.lizard_view_radius),
                         ("output-ts", args.output_ts),
                         ("cutoff", args.cutoff)]:
        if value <= 0:
            print(f"Error: --{name} must be a positive integer, got {value}",
                  file=sys.stderr)
            sys.exit(1)

    config = SimulationConfig(
        berry_prop=args.berry_prop,
        berry_growth=args.berry_growth,
        insect_prop=args.insect_prop,
        insect_move_ts=args.insect_move_ts,
        lizard_prop=args.lizard_prop,
        lizard_move_ts=args.lizard_move_ts,
        lizard_view_radius=args.lizard_view_radius,
        output_ts=args.output_ts,
        cutoff=args.cutoff,
        landscape_file=args.landscape_file,
        seed=args.seed
    )
    sim(config)


# Keep original name as alias so the program entry point still works
simCommLineIntf = sim_comm_line_intf  # pylint: disable=invalid-name


def load_landscape(landscape_file):
    """
    Load a landscape from a file into a 2D NumPy array with a halo border of water.

    The halo is a one-cell border of water (0) around all edges, used to avoid
    boundary checks during simulation updates.

    Args:
        landscape_file (str): Path to the landscape input file.

    Returns:
        tuple: (landscape, width, height) where landscape is a 2D NumPy array
               of shape (height+2, width+2), and width and height are the
               dimensions of the landscape excluding the halo.

    Raises:
        SystemExit: If the file is not found, cannot be read, or is malformed.
    """
    if not landscape_file:
        print("Error: no landscape file specified.", file=sys.stderr)
        sys.exit(1)

    try:
        with open(landscape_file, "r", encoding="utf-8") as f:
            header = f.readline().split()
            if len(header) != 2:
                print(
                    "Error: landscape file header must contain exactly "
                    "two integers (width height).",
                    file=sys.stderr)
                sys.exit(1)

            try:
                width, height = int(header[0]), int(header[1])
            except ValueError:
                print(
                    f"Error: landscape file header must contain integers, "
                    f"got: {header}",
                    file=sys.stderr)
                sys.exit(1)

            if width < 0 or height < 0:
                print(
                    f"Error: landscape dimensions must be non-negative, "
                    f"got width={width} height={height}.",
                    file=sys.stderr)
                sys.exit(1)

            print(f"Width: {width} Height: {height}")

            width_with_halo = width + 2
            height_with_halo = height + 2

            landscape = np.zeros((height_with_halo, width_with_halo), int)
            row = 1
            for line in f:
                values = line.split()
                if values:
                    if len(values) != width:
                        print(
                            f"Error: expected {width} values per row, "
                            f"got {len(values)} in row {row}.",
                            file=sys.stderr)
                        sys.exit(1)
                    try:
                        parsed = [int(v) for v in values]
                    except ValueError:
                        print(
                            "Error: landscape file must contain only 0s and 1s.",
                            file=sys.stderr)
                        sys.exit(1)
                    if any(v not in (0, 1) for v in parsed):
                        print(
                            f"Error: landscape values must be 0 (water) or "
                            f"1 (land), got: {parsed}",
                            file=sys.stderr)
                        sys.exit(1)
                    landscape[row] = [0] + parsed + [0]
                    row += 1

    except FileNotFoundError:
        print(
            f"Error: landscape file '{landscape_file}' not found.",
            file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(
            f"Error: could not read landscape file '{landscape_file}': {e}",
            file=sys.stderr)
        sys.exit(1)

    return landscape, width, height


def initialise_grid(landscape, width, height, berry_prop, insect_prop,
                    lizard_prop, seed):
    """
    Randomly initialise the entity grid with berries, insects and lizards on land cells.

    For each land cell, entities are placed independently with the given probabilities.
    If multiple entities are placed in the same cell, the last one wins
    (lizard > insect > berry).

    Args:
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water) including halo.
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.
        berry_prop (float): Probability of a berry in each land cell.
        insect_prop (float): Probability of an insect in each land cell.
        lizard_prop (float): Probability of a lizard in each land cell.
        seed (int): Random seed for reproducibility.

    Returns:
        np.ndarray: 2D grid of entity states with same shape as landscape.
    """
    grid = np.zeros((height + 2, width + 2), int)
    random.seed(seed)
    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if landscape[row, col]:
                if random.random() < berry_prop:
                    grid[row, col] = BERRY
                if random.random() < insect_prop:
                    grid[row, col] = INSECT
                if random.random() < lizard_prop:
                    grid[row, col] = LIZARD
    return grid


def collect_positions(grid, landscape, width, height):
    """
    Collect the positions of all berries, insects and lizards on land cells.

    Args:
        grid (np.ndarray): 2D grid of entity states.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.

    Returns:
        tuple: (berry_positions, insect_positions, lizard_positions) each a
               list of (row, col) tuples.
    """
    berry_positions = []
    insect_positions = []
    lizard_positions = []

    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if landscape[row, col]:
                if grid[row, col] == BERRY:
                    berry_positions.append((row, col))
                elif grid[row, col] == INSECT:
                    insect_positions.append((row, col))
                elif grid[row, col] == LIZARD:
                    lizard_positions.append((row, col))

    return berry_positions, insect_positions, lizard_positions


def calculate_average_distance(searcher_positions, target_positions):
    """
    Calculate the average Manhattan distance from each searcher to its nearest target.

    Manhattan distance is used as a simple straight-line approximation and does
    not account for water cells.

    Args:
        searcher_positions (list): List of (row, col) positions of searching entities.
        target_positions (list): List of (row, col) positions of target entities.

    Returns:
        float: Average distance to nearest target, or math.inf if no searchers
               or targets exist.
    """
    if not searcher_positions or not target_positions:
        return math.inf

    distances = []
    for searcher in searcher_positions:
        min_dist = math.inf
        for target in target_positions:
            dist = abs(searcher[0] - target[0]) + abs(searcher[1] - target[1])
            min_dist = min(min_dist, dist)
        distances.append(min_dist)

    return sum(distances) / len(distances)


def write_averages(timestep, num_berries, num_insects, avg_insect_dist,
                   num_lizards, avg_lizard_dist):
    """
    Append a row of statistics to the averages CSV file.

    Args:
        timestep (int): Current simulation timestep.
        num_berries (int): Total number of berries on the landscape.
        num_insects (int): Total number of insects on the landscape.
        avg_insect_dist (float): Average distance from each insect to nearest berry.
        num_lizards (int): Total number of lizards on the landscape.
        avg_lizard_dist (float): Average distance from each lizard to nearest insect.
    """
    with open("averages.csv", "a", encoding="utf-8") as f:
        f.write(
            f"{timestep},{num_berries},{num_insects},{avg_insect_dist:.3f},"
            f"{num_lizards},{avg_lizard_dist:.3f}\n"
        )


def write_ppm(timestep, grid, landscape, width, height, lizard_view_radius):
    """
    Write a Plain PPM image file visualising the current simulation state.

    Colour encoding per cell:
        - Water:  RGB(0, 200, 255) bright blue-green
        - Berry:  red channel = 150
        - Insect: blue channel = 150
        - Lizard: green channel = 200, with a dimming green diamond showing
                  its view radius

    Args:
        timestep (int): Current simulation timestep, used to name the output file.
        grid (np.ndarray): 2D grid of entity states.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.
        lizard_view_radius (int): Maximum BFS search radius for lizard vision diamond.
    """
    berry_cols = np.zeros((height, width), int)
    insect_cols = np.zeros((height, width), int)
    lizard_cols = np.zeros((height, width), int)

    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if landscape[row, col]:
                if grid[row, col] == BERRY:
                    berry_cols[row - 1, col - 1] = 150
                elif grid[row, col] == INSECT:
                    insect_cols[row - 1, col - 1] = 150
                elif grid[row, col] == LIZARD:
                    _render_lizard(
                        row, col, lizard_cols, landscape,
                        lizard_view_radius)

    with open(f"map_{timestep:04d}.ppm", "w", encoding="utf-8") as f:
        f.write(f"P3\n{width} {height}\n255\n")
        for row in range(0, height):
            for col in range(0, width):
                if landscape[row + 1, col + 1]:
                    f.write(
                        f"{berry_cols[row, col]} "
                        f"{lizard_cols[row, col]} "
                        f"{insect_cols[row, col]}\n")
                else:
                    f.write("0 200 255\n")


def _render_lizard(row, col, lizard_cols, landscape, lizard_view_radius):
    """
    Render a lizard and its dimming green view-radius diamond into lizard_cols.

    Uses BFS outward from the lizard position to illuminate surrounding cells,
    with brightness decreasing with distance.

    Args:
        row (int): Row index of the lizard (including halo offset).
        col (int): Column index of the lizard (including halo offset).
        lizard_cols (np.ndarray): 2D array of green channel values to update.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        lizard_view_radius (int): Maximum BFS search radius.
    """
    lizard_cols[row - 1, col - 1] = 200

    search_dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    search_queue = [
        (row + row_delta, col + col_delta, row_delta, col_delta, 1)
        for row_delta, col_delta in search_dirs
        if landscape[row + row_delta, col + col_delta]
    ]
    visited = {(row, col)}

    while search_queue:
        curr_row, curr_col, orig_row_delta, orig_col_delta, dist = \
            search_queue.pop(0)

        if (curr_row, curr_col) in visited or dist > lizard_view_radius:
            continue
        visited.add((curr_row, curr_col))

        lizard_cols[curr_row - 1, curr_col - 1] = max(
            lizard_cols[curr_row - 1, curr_col - 1],
            100 / dist
        )

        for row_delta, col_delta in search_dirs:
            next_row = curr_row + row_delta
            next_col = curr_col + col_delta
            if landscape[next_row, next_col] and \
                    (next_row, next_col) not in visited:
                search_queue.append(
                    (next_row, next_col,
                     orig_row_delta, orig_col_delta, dist + 1)
                )


def grow_berries(grid, grid_next, landscape, width, height, berry_growth):
    """
    Randomly grow new berries on empty land cells.

    Each empty land cell has a berry_growth probability of growing a berry
    on the next timestep.

    Args:
        grid (np.ndarray): Current 2D grid of entity states.
        grid_next (np.ndarray): Next 2D grid to be updated in place.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.
        berry_growth (float): Probability of a berry growing in an empty cell.
    """
    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if landscape[row, col] and not grid[row, col]:
                if random.random() < berry_growth:
                    grid_next[row, col] = BERRY


def move_insects(grid, grid_next, landscape, width, height):
    """
    Move each insect one step toward the nearest berry using BFS.

    Insects stay in place if no berry is found or if the destination cell
    is already occupied by another insect or a lizard.

    Args:
        grid (np.ndarray): Current 2D grid of entity states.
        grid_next (np.ndarray): Next 2D grid to be updated in place.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.
    """
    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if grid[row, col] == INSECT:
                row_step, col_step = find_nearest(
                    landscape, grid, (row, col), BERRY)
                next_row = row + row_step
                next_col = col + col_step

                if (row_step == 0 and col_step == 0) \
                        or grid[next_row, next_col] in (INSECT, LIZARD) \
                        or grid_next[next_row, next_col] in (INSECT, LIZARD):
                    next_row, next_col = row, col

                grid_next[row, col] = EMPTY
                grid_next[next_row, next_col] = INSECT


def move_lizards(grid, grid_next, landscape, width, height, lizard_view_radius):
    """
    Move each lizard one step toward the nearest insect within its view radius
    using BFS.

    Lizards stay in place if no insect is found within lizard_view_radius cells,
    or if the destination cell is already occupied by a berry or another lizard.

    Args:
        grid (np.ndarray): Current 2D grid of entity states.
        grid_next (np.ndarray): Next 2D grid to be updated in place.
        landscape (np.ndarray): 2D landscape grid (1=land, 0=water).
        width (int): Width of the landscape excluding halo.
        height (int): Height of the landscape excluding halo.
        lizard_view_radius (int): Maximum BFS search radius for lizards hunting insects.
    """
    for row in range(1, height + 1):
        for col in range(1, width + 1):
            if grid[row, col] == LIZARD:
                row_step, col_step = find_nearest(
                    landscape, grid, (row, col), INSECT,
                    max_dist=lizard_view_radius)
                next_row = row + row_step
                next_col = col + col_step

                if (row_step == 0 and col_step == 0) \
                        or grid[next_row, next_col] in (BERRY, LIZARD) \
                        or grid_next[next_row, next_col] in (BERRY, LIZARD):
                    next_row, next_col = row, col

                grid_next[row, col] = EMPTY
                grid_next[next_row, next_col] = LIZARD


def find_nearest(landscape, grid_state, start_pos, target_val,
                 max_dist=math.inf):
    """
    Find the nearest cell containing target_val using breadth-first search (BFS).

    Directions are randomly shuffled before each search to spread animals out,
    matching the behaviour of the original simulation.

    Args:
        landscape (np.ndarray): 2D grid where 1=land and 0=water (including halo).
        grid_state (np.ndarray): 2D grid of entity states
                                 (EMPTY, BERRY, INSECT, LIZARD).
        start_pos (tuple): (row, col) position of the searching animal.
        target_val (int): Entity value to search for (e.g. BERRY=1, INSECT=2).
        max_dist (int): Maximum BFS search depth in steps. Defaults to math.inf.

    Returns:
        tuple: (row_delta, col_delta) of the first step toward the nearest target,
               or (0, 0) if no target is found within max_dist.
    """
    start_row, start_col = start_pos

    # Randomly shuffle directions to encourage animals to spread out
    remaining_dirs = list(DIRECTIONS)
    shuffled_dirs = []
    while remaining_dirs:
        idx = math.floor(random.random() * len(remaining_dirs))
        shuffled_dirs.append(remaining_dirs.pop(idx))

    # Initialise BFS queue with valid adjacent land cells
    # Each entry: (row, col, first_row_step, first_col_step, distance)
    queue = deque()
    for row_delta, col_delta in shuffled_dirs:
        neighbour_row = start_row + row_delta
        neighbour_col = start_col + col_delta
        if landscape[neighbour_row, neighbour_col]:
            queue.append((neighbour_row, neighbour_col,
                          row_delta, col_delta, 1))

    visited = {(start_row, start_col)}

    while queue:
        curr_row, curr_col, first_row_step, first_col_step, dist = \
            queue.popleft()

        if (curr_row, curr_col) in visited or dist > max_dist:
            continue
        visited.add((curr_row, curr_col))

        if grid_state[curr_row, curr_col] == target_val:
            return first_row_step, first_col_step

        for row_delta, col_delta in shuffled_dirs:
            next_row = curr_row + row_delta
            next_col = curr_col + col_delta
            if landscape[next_row, next_col] and \
                    (next_row, next_col) not in visited:
                queue.append((next_row, next_col,
                              first_row_step, first_col_step, dist + 1))

    return 0, 0


def sim(config):
    """
    Run the lizard-insect-berry simulation.

    Args:
        config (SimulationConfig): Dataclass containing all simulation parameters.
    """
    print(f"Insect simulation {get_version()}")

    landscape, width, height = load_landscape(config.landscape_file)
    grid = initialise_grid(
        landscape, width, height,
        config.berry_prop, config.insect_prop, config.lizard_prop, config.seed
    )

    # Reuse this array each timestep to avoid repeated memory allocation
    grid_next = grid.copy()

    # Write CSV header
    with open("averages.csv", "w", encoding="utf-8") as f:
        f.write(
            "Timestep,# Fruit,# Insects,Avg distance to berry,"
            "# Lizards, Avg distance to insect\n"
        )

    for timestep in range(0, config.cutoff):

        # Output statistics and PPM image at regular intervals
        if timestep % config.output_ts == 0:
            berry_positions, insect_positions, lizard_positions = \
                collect_positions(grid, landscape, width, height)

            num_berries = len(berry_positions)
            num_insects = len(insect_positions)
            num_lizards = len(lizard_positions)

            avg_insect_dist = calculate_average_distance(
                insect_positions, berry_positions)
            avg_lizard_dist = calculate_average_distance(
                lizard_positions, insect_positions)

            print(
                f"Averages. Timestep: {timestep} "
                f"Berries: {num_berries} "
                f"Insects: {num_insects}({avg_insect_dist:.3f}) "
                f"Lizards: {num_lizards}({avg_lizard_dist:.3f})"
            )

            write_averages(timestep, num_berries, num_insects,
                           avg_insect_dist, num_lizards, avg_lizard_dist)
            write_ppm(timestep, grid, landscape, width, height,
                      config.lizard_view_radius)

        # Copy current grid state into next grid using NumPy for efficiency
        np.copyto(grid_next, grid)

        grow_berries(grid, grid_next, landscape, width, height,
                     config.berry_growth)

        if timestep % config.insect_move_ts == 0:
            move_insects(grid, grid_next, landscape, width, height)

        if timestep % config.lizard_move_ts == 0:
            move_lizards(grid, grid_next, landscape, width, height,
                         config.lizard_view_radius)

        # Swap grids for next iteration
        grid, grid_next = grid_next, grid


if __name__ == "__main__":
    sim_comm_line_intf()

'''Lizard-insect-berry simulation.

Version 1.0, last updated in Feb 2026.
'''
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from collections import deque
import math
import numpy as np
import random

# Entity type constants used in the grid state array
EMPTY = 0
BERRY = 1
INSECT = 2
LIZARD = 3

# Halo border value (water)
WATER = 0
LAND = 1

# Cardinal movement directions (row_delta, col_delta)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def getVersion():
    """Return the current version of the simulation."""
    return 1.0


def simCommLineIntf():
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
    sim(
        args.berry_prop,
        args.berry_growth,
        args.insect_prop,
        args.insect_move_ts,
        args.lizard_prop,
        args.lizard_move_ts,
        args.lizard_view_radius,
        args.output_ts,
        args.cutoff,
        args.landscape_file,
        args.seed
    )


def find_nearest(landscape, grid_state, start_pos, target_val, max_dist=math.inf):
    """
    Find the nearest cell containing target_val using breadth-first search (BFS).

    Directions are randomly shuffled before each search to spread animals out,
    matching the behaviour of the original simulation.

    Args:
        landscape (np.ndarray): 2D grid where 1=land and 0=water (including halo).
        grid_state (np.ndarray): 2D grid of entity states (EMPTY, BERRY, INSECT, LIZARD).
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
            queue.append((neighbour_row, neighbour_col, row_delta, col_delta, 1))

    visited = {(start_row, start_col)}

    while queue:
        curr_row, curr_col, first_row_step, first_col_step, dist = queue.popleft()

        if (curr_row, curr_col) in visited or dist > max_dist:
            continue
        visited.add((curr_row, curr_col))

        if grid_state[curr_row, curr_col] == target_val:
            return first_row_step, first_col_step

        for row_delta, col_delta in shuffled_dirs:
            next_row = curr_row + row_delta
            next_col = curr_col + col_delta
            if landscape[next_row, next_col] and (next_row, next_col) not in visited:
                queue.append((next_row, next_col, first_row_step, first_col_step, dist + 1))

    return 0, 0


def sim(berry_prop, berry_growth, insect_prop, insect_move_ts, lizard_prop,
        lizard_move_ts, lizard_view_radius, output_ts, cutoff, landscape_file, seed):
    """
    Run the lizard-insect-berry simulation.

    Args:
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
    print("Insect simulation", getVersion())

    # Load landscape from file into a 2D array with a halo border of water
    with open(landscape_file, "r") as f:
        width, height = [int(v) for v in f.readline().split(" ")]
        print("Width: {} Height: {}".format(width, height))

        width_with_halo = width + 2
        height_with_halo = height + 2

        landscape = np.zeros((height_with_halo, width_with_halo), int)
        row = 1
        for line in f:
            values = line.split()
            if values:
                landscape[row] = [0] + [int(v) for v in values] + [0]
                row += 1

    # Initialise entity grid: randomly place berries, insects and lizards on land cells
    grid = np.zeros((height_with_halo, width_with_halo), int)
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

    # Reuse this array each timestep to avoid repeated memory allocation
    grid_next = grid.copy()

    # Write CSV header
    with open("averages.csv", "w") as f:
        f.write("Timestep,# Fruit,# Insects,Avg distance to berry,# Lizards, Avg distance to insect\n")

    for timestep in range(0, cutoff):

        # Output statistics and PPM image at regular intervals
        if timestep % output_ts == 0:
            berry_positions = []
            insect_positions = []
            lizard_positions = []

            for row in range(1, height + 1):
                for col in range(1, width + 1):
                    if landscape[row, col]:
                        if grid[row, col] == BERRY:
                            berry_positions.append((row, col))
                        if grid[row, col] == INSECT:
                            insect_positions.append((row, col))
                        if grid[row, col] == LIZARD:
                            lizard_positions.append((row, col))

            num_berries = len(berry_positions)
            num_insects = len(insect_positions)
            num_lizards = len(lizard_positions)

            # Calculate average Manhattan distance from each insect to nearest berry
            insect_distances = []
            for insect_pos in insect_positions:
                min_dist = math.inf
                for berry_pos in berry_positions:
                    dist = abs(insect_pos[0] - berry_pos[0]) + abs(insect_pos[1] - berry_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                insect_distances.append(min_dist)

            # Calculate average Manhattan distance from each lizard to nearest insect
            lizard_distances = []
            for lizard_pos in lizard_positions:
                min_dist = math.inf
                for insect_pos in insect_positions:
                    dist = abs(lizard_pos[0] - insect_pos[0]) + abs(lizard_pos[1] - insect_pos[1])
                    if dist < min_dist:
                        min_dist = dist
                lizard_distances.append(min_dist)

            avg_insect_dist = sum(insect_distances) / len(insect_distances) if insect_distances else math.inf
            avg_lizard_dist = sum(lizard_distances) / len(lizard_distances) if lizard_distances else math.inf

            print("Averages. Timestep: {} Berries: {} Insects: {}({:.3f}) Lizards: {}({:.3f})".format(
                timestep, num_berries, num_insects, avg_insect_dist, num_lizards, avg_lizard_dist))

            with open("averages.csv", "a") as f:
                f.write("{},{},{},{:.3f},{},{:.3f}\n".format(
                    timestep, num_berries, num_insects, avg_insect_dist,
                    num_lizards, avg_lizard_dist))

            # Build PPM colour channels for berries (red), lizards (green), insects (blue)
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
                            lizard_cols[row - 1, col - 1] = 200
                            # Illuminate cells within lizard's view radius as a green diamond
                            dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                            q = []
                            vis = set()
                            vis.add((row, col))
                            for dx, dy in dirs:
                                cx = row + dx
                                cy = col + dy
                                if landscape[cx, cy]:
                                    q += [(cx, cy, dx, dy, 1)]
                            while q:
                                cx, cy, odx, ody, d = q.pop(0)
                                if (cx, cy) in vis:
                                    continue
                                if d > lizard_view_radius:
                                    continue
                                vis.add((cx, cy))
                                lizard_cols[cx - 1, cy - 1] = max(lizard_cols[cx - 1, cy - 1], 100 / d)
                                for dx, dy in dirs:
                                    nx, ny = cx + dx, cy + dy
                                    if landscape[nx, ny] and (nx, ny) not in vis:
                                        q.append((nx, ny, odx, ody, d + 1))

            # Write PPM image file for this timestep
            with open("map_{:04d}.ppm".format(timestep), "w") as f:
                f.write("P3\n{} {}\n{}\n".format(width, height, 255))
                for row in range(0, height):
                    for col in range(0, width):
                        if landscape[row + 1, col + 1]:
                            f.write("{} {} {}\n".format(
                                berry_cols[row, col],
                                lizard_cols[row, col],
                                insect_cols[row, col]))
                        else:
                            f.write("{} {} {}\n".format(0, 200, 255))

        # Copy current grid to next grid for this timestep's updates
        for row in range(1, height + 1):
            for col in range(1, width + 1):
                grid_next[row, col] = grid[row, col]

        # Grow new berries randomly on empty land cells
        for row in range(1, height + 1):
            for col in range(1, width + 1):
                if landscape[row, col] and not grid[row, col]:
                    if random.random() < berry_growth:
                        grid_next[row, col] = BERRY

        # Move insects toward nearest berry every insect_move_ts timesteps
        if timestep % insect_move_ts == 0:
            for row in range(1, height + 1):
                for col in range(1, width + 1):
                    if grid[row, col] == INSECT:
                        row_step, col_step = find_nearest(landscape, grid, (row, col), BERRY)
                        next_row = row + row_step
                        next_col = col + col_step

                        # Stay put if no berry found or destination is occupied
                        if (row_step == 0 and col_step == 0) \
                                or grid[next_row, next_col] in (INSECT, LIZARD) \
                                or grid_next[next_row, next_col] in (INSECT, LIZARD):
                            next_row, next_col = row, col

                        grid_next[row, col] = EMPTY
                        grid_next[next_row, next_col] = INSECT

        # Move lizards toward nearest insect every lizard_move_ts timesteps
        if timestep % lizard_move_ts == 0:
            for row in range(1, height + 1):
                for col in range(1, width + 1):
                    if grid[row, col] == LIZARD:
                        row_step, col_step = find_nearest(
                            landscape, grid, (row, col), INSECT,
                            max_dist=lizard_view_radius)
                        next_row = row + row_step
                        next_col = col + col_step

                        # Stay put if no insect found within radius or destination is occupied
                        if (row_step == 0 and col_step == 0) \
                                or grid[next_row, next_col] in (BERRY, LIZARD) \
                                or grid_next[next_row, next_col] in (BERRY, LIZARD):
                            next_row, next_col = row, col

                        grid_next[row, col] = EMPTY
                        grid_next[next_row, next_col] = LIZARD

        # Swap grids for next iteration
        grid, grid_next = grid_next, grid


if __name__ == "__main__":
    simCommLineIntf()

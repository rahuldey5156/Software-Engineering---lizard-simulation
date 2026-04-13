# MSc Programming Skills Python lizard-insect-berry simulation

## Requirements

* Python 3.x
* [numpy](https://numpy.org/)
* [pytest](https://pytest.org/)
* [pytest-cov](https://pytest-cov.readthedocs.io/) (for test coverage reports)
* [matplotlib](https://matplotlib.org/) (for reproducing the performance experiment graph only)
* [pylint](https://pylint.org/) (for static code analysis only)
* [ImageMagick](https://imagemagick.org/) (optional, for generating animated GIFs)

Install all dependencies with:

```console
$ pip install -r requirements.txt
```

To get Python 3 on Cirrus, run:

```console
$ module load anaconda/python3
```

The Anaconda Python distribution includes numpy and matplotlib.

---

## Usage

To run the simulation using the map [10x20.dat](landscapes/10x20.dat) with
default values for all other parameters:

```console
$ python -m insect.simulate_insect -f landscapes/10x20.dat
```

For an explanation of all command-line parameters and their default values:

```console
$ python -m insect.simulate_insect -h
```

### Command-line parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-f`, `--landscape-file` | (required) | Input landscape file |
| `-b`, `--berry-prop` | 0.05 | Initial proportion of land cells with berries |
| `-c`, `--berry-growth` | 0.001 | Proportion of empty cells that grow a berry per timestep |
| `-i`, `--insect-prop` | 0.08 | Initial proportion of land cells with insects |
| `-j`, `--insect-move-ts` | 5 | Timesteps between insect movements |
| `-l`, `--lizard-prop` | 0.01 | Initial proportion of land cells with lizards |
| `-m`, `--lizard-move-ts` | 2 | Timesteps between lizard movements |
| `-n`, `--lizard-view-radius` | 3 | Maximum BFS search radius for lizards hunting insects |
| `-o`, `--output-ts` | 10 | Interval in timesteps between outputs |
| `-x`, `--cutoff` | 500 | Total number of timesteps to simulate |
| `-s`, `--seed` | 1 | Random seed for reproducibility |

### Input files

Map files are expected to be plain-text files of the form:

* One header line giving the width (Nx) and height (Ny) separated by a space
* Ny lines, each containing Nx space-separated values of 1 (land) or 0 (water)

For example:

```
7 7
1 1 1 1 1 1 1
1 1 1 1 1 1 1
1 1 1 1 0 1 1
1 1 1 1 0 0 1
1 1 1 0 0 0 0
1 1 1 0 0 0 0
1 0 0 0 0 0 0
```

A selection of landscape files are provided in the [landscapes/](landscapes/)
directory, ranging from simple 1x1 grids to complex 1000x800 island maps.

### Invalid input handling

The program will print an error message to stderr and exit with a non-zero
exit code if:

* The landscape file does not exist or cannot be read
* The landscape file header is malformed or missing
* Landscape cell values contain anything other than 0 or 1
* Probability parameters (`-b`, `-c`, `-i`, `-l`) are outside [0.0, 1.0]
* Integer parameters (`-j`, `-m`, `-n`, `-o`, `-x`) are not positive integers

### PPM output files

Plain PPM image files are output every `output-ts` timesteps, named
`map_<NNNN>.ppm`. These visualise the positions of berries, insects, lizards
and water at that point in time.

Colour encoding:

* **Water**: bright blue-green RGB(0, 200, 255)
* **Berry**: red channel = 150
* **Insect**: blue channel = 150
* **Lizard**: green channel = 200, surrounded by a dimming green diamond
  showing its view radius. Cells within the view radius appear progressively
  dimmer the further they are from the lizard.

### CSV averages output file

A plain-text CSV file `averages.csv` is written with statistics at every
`output-ts` timesteps:

```csv
Timestep,# Berries,# Insects,Avg distance to berry,# Lizards,Avg distance to insect
```

where:

* `Timestep`: current timestep
* `# Berries`: total number of berries on the landscape
* `# Insects`: total number of insects on the landscape
* `Avg distance to berry`: average Manhattan distance from each insect to its nearest berry
* `# Lizards`: total number of lizards on the landscape
* `Avg distance to insect`: average Manhattan distance from each lizard to its nearest insect

---

## Visualising the simulation

PPM files can be viewed individually using ImageMagick. Cirrus users should
first run `module load ImageMagick`.

To view a single PPM file:

```console
$ display -resize 400 map_0000.ppm
```

To animate all PPM files:

```console
$ animate -resize 400 map*.ppm
```

To generate an animated GIF from the PPM files:

```console
$ python -m insect.simulate_insect -f landscapes/map.dat -s 1 -x 100 -o 5
$ magick $(ls map_*.ppm | sort) -resize 400x400 -delay 20 results/simulation.gif
```

A sample animated GIF showing 100 timesteps on the `map.dat` landscape is
shown below. The full file is available at [results/simulation.gif](results/simulation.gif).

![Simulation Animation](results/simulation.gif)

For more information on the PPM file format, run `man ppm` or see
[ppm](http://netpbm.sourceforge.net/doc/ppm.html).

---

## Running automated tests

All tests are in `test/test_regression.py` and cover:

* Unit tests for `find_nearest`, `load_landscape`, `initialise_grid`,
  `collect_positions`, `calculate_average_distance`, `grow_berries`,
  `move_insects`, `move_lizards`, `write_averages` and `write_ppm`
* End-to-end regression tests verifying console output, CSV values and PPM
  file creation on multiple landscape files
* Edge case tests covering 0x0, 1x1, all-water, all-land, wide, tall,
  island and corner landscapes
* Boundary tests for all probability and integer parameters
* Reproducibility tests verifying same seed gives identical output
* Invalid input handling tests

Run all tests from the repository root:

```console
$ pytest test/test_regression.py -v
```

Expected output:

```
73 passed in ~5s
```

To run tests with coverage report:

```console
$ pytest test/test_regression.py --cov=insect --cov-report=term-missing
```

To run static analysis:

```console
$ pylint insect/simulate_insect.py
```

Expected pylint score: 10.00/10.

---

## Performance experiment

The performance experiment investigates how grid size affects simulation
runtime. Full details, including profiling results and analysis, are in
[PERFORMANCE.md](PERFORMANCE.md).

To reproduce the full experiment:

```console
$ python3 scripts/generate_landscapes.py
$ python3 scripts/run_experiment.py
$ python3 scripts/plot_results.py
```

To reproduce the profiling results:

```console
$ python3 scripts/profile_simulation.py
```

Results are saved to `results/runtime_vs_gridsize.png`.

---

## Repository structure

```
s2793337/
  insect/
    __init__.py
    simulate_insect.py      # Main simulation code
  test/
    __init__.py
    test_example.py         # Original minimal test provided with coursework
    test_regression.py      # All automated tests (73 tests)
    baselines/
      expected_averages_10x20.csv  # Baseline CSV for regression testing
  landscapes/
    *.dat                   # Provided landscape files
    experiment/             # Generated landscape files for performance experiment
  scripts/
    generate_landscapes.py  # Generates landscape files for the experiment
    run_experiment.py       # Times the simulation across grid sizes
    plot_results.py         # Plots the results graph
    profile_simulation.py   # Profiles the simulation using cProfile
  results/
    runtime_vs_gridsize.png # Performance experiment graph
    simulation.gif          # Animated GIF of the simulation
  .pylintrc                 # Pylint configuration
  requirements.txt          # Python dependencies
  README.md                 # This file
  PERFORMANCE.md            # Performance experiment report
```

---

## Running the simulation within PyCharm

If you know how to use the [PyCharm](https://www.jetbrains.com/pycharm/)
integrated development environment, here is one way to configure it:

Create a configuration to run the program:

* Select Run menu → Run... → Edit Configurations... → + → Python
* Click the dropdown next to 'Script path' and select 'Module name'
* Enter Module name: `insect.simulate_insect`
* Enter Parameters: `-f landscapes/10x20.dat`
* Click Run

Create a configuration to run the tests using pytest:

* Select Run menu → Run... → Edit Configurations... → + → pytest
* Click Run

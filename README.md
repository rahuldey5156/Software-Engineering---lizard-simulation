# MSc Programming Skills Python lizard-insect-berry simulation

## Requirements

* Python 3.x
* [numpy](https://numpy.org/)
* [pytest](https://pytest.org/)

To get Python 3 on Cirrus, run:

```console
$ module load anaconda/python3
```

The Anaconda Python distribution includes numpy and many other useful Python packages.

---

## Usage

To run the simulation using the map, [10x20.dat](../landscapes/10x20.dat), with default values for the other parameters:

```console
$ python -m insect.simulate_insect -f ../landscapes/10x20.dat
```

For an explanation of the other command-line parameters and their values, run:

```console
$ python -m insect.simulate_insect -h
```

### Input files

Map files are expected to be plain-text files of form:

* One line giving Nx, the number of columns, and Ny, the number of rows
* Ny lines, each consisting of a sequence of Nx space-separated ones and zeros (land=1, water=0).

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

### PPM output files

"Plain PPM" image files are output every `OUTPUT_TS` timesteps.  These files are named `map_<NNNN>.ppm` and are a visualisation of the position of berries, insects, lizards and water-only squares.

These files do not include the halo as the use of a halo is an implementation detail.

These files are plain-text so you can view them as you would any plain-text file e.g.:

```console
$ cat map<NNNN>.ppm
```
PPM files can be viewed graphically using ImageMagick commands as follows.

Cirrus users will need first need to run:

```console
$ module load ImageMagick
```

To view a PPM file, run:

```console
$ display -resize 400 map<NNNN>.ppm
```

To animate a series of PPM files:

```console
$ animate -resize 400 map*.ppm
```

For more information on the PPM file format, run `man ppm` or see [ppm](http://netpbm.sourceforge.net/doc/ppm.html).

### CSV averages output file

A plain-text comma-separated values file, `averages.csv`, has the average density of mice and foxes (across the land-only squares) calculated every `OUTPUT_TS` timesteps. The file has four columns and a header row:

```csv
Timestep,# Berries,# Insects,Avg distance to berry,# Lizards,Avg distance to insect
```

where:

* `Timestep`: timestep from 0 .. `LENGTH`
* `# Berries`: total number of berries
* `# Insects`: total number of mice
* `Avg distance to berry`: average distance from each insect to nearest berry
* `# Lizards`: total number of cats
* `Avg distance to insect`: average distance from each lizard to nearest insect

This file is plain-text so you can view it as you would any plain-text file e.g.:

```console
$ cat averages.csv
```

---

## Running automated tests

`test/test_example.py` is a module with a unit test for the `getVersion` function in `insect/simulate_insect.py`.

`pytest` can find and run any tests in the current directory or its subdirectories:

```console
$ pytest
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.20s ========================================
```

`pytest` can be told to find and run the tests in a specific module:

```console
$ pytest test/test_example.py
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.21s ========================================
```

`pytest` can be told to run a specific test within a specific module:

```console
$ pytest test/test_example.py::testGetVersion
======================================= test session starts =======================================
...
test/test_example.py .                                                                      [100%]

======================================== 1 passed in 0.35s ========================================
```

For more information on `pytest`, see the [pytest](https://docs.pytest.org/) documentation.

---

## Running the simulation within Pycharm

If you know how to use the [Pycharm](https://www.jetbrains.com/pycharm/) integrated development environment, then here is *one way* you can configure this to run the program and tests as follows (for example, for Pycharm 2020.02).

Start Pycharm.

Open the source code directory:

* Click Open
* Select the directory with the code, the directory with ``, `test`, and `README.md`.

Create a configuration to run the program:

* Select Run menu, Run...
* Click Edit Configurations...
* Click +
* Click Python.
* Click V on right of 'Script path' and select 'Module name'.
* Enter Module name: `insect.simulate_insect`
* Enter Parameters: Enter `-f <path from your home directory to landscapes/10x20.dat>`. The current directory is assumed to be wherever you started Pycharm. If you started this in your home directory then your path to `landscapes/10x20.dat` might be `assessment/landscapes/10x20.dat`.
* Click Run.
* The 'Run' window should show the output from the run.

Rerun the program:

* Select Run menu, Run...
* Click `insect.simulate_insect`.
* The 'Run' window should show the output from the run.

Create a configuration to run the tests using `pytest`:

* Select Run menu, Run...
* Click Edit Configurations...
* Click +
* Click pytest.
* Click Run.
* The 'Run' window should show the output from the test run.

Rerun the tests:

* Select Run menu, Run...
* Click `insect.simulate_insect`.
* Click pytest.
* The 'Run' window should show the output from the test run.

To edit a run configuration:

* Select Run menu, Edit Configurations...
* Click the configuration you want to edit.
* For running `insect.simulate_insect` with different command-line parameters, you can add these to, and edit them within, the Parameters field in the Configuration form. Alternatively, you can create run configurations with different names for different parameter sets.

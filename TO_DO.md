# Refactoring & Development Plan

## Step 1: Modularization
    - **Break down `main_simulation_loop` (God Function):**
    - Extract **Landscape Parsing** into a dedicated `MapLoader` class.
    - Move **Insect Movement Logic** to a `MovementEngine` function.
    - Move **Resource Consumption/Growth** to a `BioLogic` module.
    - Isolate **Output/Logging** to a `ReportGenerator`.

## Step 2: Testing & Validation
    - Create unit tests for individual modules extracted in Step 1.
    - Implement regression tests using the 21-file dataset to ensure performance      stays consistent.

## Step 3: Final Optimization
    - Review coordinate system storage to see if a dictionary or NumPy array is       faster than the current BFS implementation.

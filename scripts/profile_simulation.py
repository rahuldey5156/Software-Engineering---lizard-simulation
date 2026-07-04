"""
Profile the simulation using cProfile to identify the most costly functions.
Runs on a large landscape to ensure meaningful profiling data.
"""
import cProfile
import pstats
import io
import sys
import os

# Add parent directory to path so we can import the module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from insect.simulate_insect import sim

# Profile on 100x100 landscape for 100 timesteps
profiler = cProfile.Profile()
profiler.enable()
sim(
    berry_prop=0.05,
    berry_growth=0.001,
    insect_prop=0.08,
    insect_move_ts=5,
    lizard_prop=0.01,
    lizard_move_ts=2,
    lizard_view_radius=3,
    output_ts=9999,
    cutoff=100,
    landscape_file="landscapes/experiment/100x100.dat",
    seed=1
)
profiler.disable()

stream = io.StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats("cumulative")
stats.print_stats(15)
print(stream.getvalue())

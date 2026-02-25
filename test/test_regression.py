import subprocess
import os
import pandas as pd
from insect import simulate_insect

def test_simulation_output_consistency():
    # Run simulation with a fixed seed for reproducibility 
    cmd = ["python3", "-m", "insect.simulate_insect", "-f", "landscapes/10x20.dat", "-s", "1", "-x", "50"]
    subprocess.run(cmd, check=True)

    # Check if output exists [cite: 4]
    assert os.path.exists("averages.csv")

    # Load data to ensure it's valid CSV [cite: 4]
    df = pd.read_csv("averages.csv")
    assert not df.empty
    assert "Timestep" in df.columns

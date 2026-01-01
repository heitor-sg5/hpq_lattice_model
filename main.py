import argparse
import os
import json
import random
import time
from collections import Counter

from model.chain import PeptideChain
from model.lattice import Lattice
from folding.energy import EnergyModel
from folding.relax import relax_chain
from utils.io import save_structure, save_log, plot_3d, plot_energy_vs_steps

# Directories for output
structure_dir = "output/structures"
log_dir = "output/logs"
data_dir = "data"

# CL argument parser
parser = argparse.ArgumentParser(description="Toy protein folding model")
parser.add_argument("--sequence", type=str, required=True,
                    help="Peptide sequence OR name of file")
parser.add_argument("--steps", type=int, default=1000) # number of simulation steps
parser.add_argument("--seed", type=int, default=42) # random seed
args = parser.parse_args()

# Seed the rng for reproducibility
random.seed(args.seed)

# Load residue properties from json
with open(os.path.join(data_dir, "residues.json")) as f:
    residue_props = json.load(f)

# Check if sequence is an example file
seq_input = args.sequence
if seq_input.startswith("example_"):
    file_path = os.path.join(data_dir, seq_input)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Example file {file_path} not found")
    with open(file_path) as f:
        sequence = f.read().strip()
else:
    sequence = seq_input

start = time.time()

# Initialize lattice and peptide chain
lattice = Lattice()
chain = PeptideChain(residue_props=residue_props, lattice=lattice)
chain.initialize_linear(sequence) # place residues on a zigzag along the x-axis

# Define the energy model with parameters
energy_model = EnergyModel(alpha=0.2, eps_HH=1.0, eps_HP=0.3, eps_PP=0.1, eps_Q=1.0)

# Ensure output directories exist
os.makedirs(structure_dir, exist_ok=True)
os.makedirs(log_dir, exist_ok=True)

# Relax chain (folding simulation)
trajectory = relax_chain(
    chain, lattice, energy_model, n_steps=args.steps, T_start=2.0, T_end=0.5
)

# Save stepwise simulation log
save_log({"sequence": sequence, "seed": args.seed, "trajectory": trajectory}, log_dir)

# Save final structure to csv
structure = chain.get_structure()
csv_filename = save_structure(structure, structure_dir, sequence=sequence)

end = time.time() - start

# Plot final 3d structure with local energies
plot_3d(os.path.join(structure_dir, csv_filename), local_energies=trajectory[-1]["local_energies"])
plot_energy_vs_steps(trajectory)

# Get move counts
move_types = [step["move_type"] for step in trajectory if "move_type" in step]
move_counts = Counter(move_types)

# Compute and print final total energy
total_energy = trajectory[-1]["total_energy"]
print(f"Sequence: {sequence}")
print(f"Length: {len(sequence)}")
print(f"Final Energy: {total_energy:.2f}")
print(f"Move counts: {dict(move_counts)}")
print(f"Structure saved to {structure_dir}")
print(f"Logs saved to {log_dir}")
print(f"Runtime: {end:.2f} seconds")
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

from utils.save import save_structure, save_log
from utils.viewer import plot_3d
from utils.analytics import plot_energy_vs_steps

structure_dir = "output/structures"
log_dir = "output/logs"
data_dir = "data"

def run_simulation(sequence, residue_props, steps, seed, run_id=None, plot=False,):
    if run_id is not None:
        random.seed(seed + run_id)
        run_tag = f"run_{run_id}"
    else:
        random.seed(seed)
        run_tag = None

    start_time = time.time()

    lattice = Lattice()
    chain = PeptideChain(residue_props=residue_props, lattice=lattice)
    chain.initialize_linear(sequence)

    energy_model = EnergyModel( alpha=0.2, eps_HH=1.0, eps_HP=0.3, eps_PP=0.1, eps_Q=1.0,)
    trajectory = relax_chain( chain, lattice, energy_model, n_steps=steps, T_start=2.0, T_end=0.5,)

    log_data = {"sequence": sequence, "seed": seed, "trajectory": trajectory, "run_id": run_tag,}
    save_log(log_data, log_dir, prefix=run_tag)

    structure = chain.get_structure()
    csv_filename = save_structure( structure, structure_dir, sequence=sequence, prefix=run_tag,)

    runtime = time.time() - start_time

    if plot:
        plot_3d(os.path.join(structure_dir, csv_filename), local_energies=trajectory[-1]["local_energies"],)
        plot_energy_vs_steps(trajectory)

    move_types = [step["move_type"] for step in trajectory if "move_type" in step]
    move_counts = Counter(move_types)

    total_energy = trajectory[-1]["total_energy"]
    min_energy = min(step["total_energy"] for step in trajectory)

    return {
        "run_tag": run_tag,
        "final_energy": total_energy,
        "min_energy": min_energy,
        "move_counts": dict(move_counts),
        "runtime": runtime,
    }

def main():
    parser = argparse.ArgumentParser(description="Toy protein folding model")
    parser.add_argument("--sequence", type=str, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--steps", type=int, default=1000)
    parser.add_argument("--runs", type=int, default=1)
    args = parser.parse_args()

    os.makedirs(structure_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    with open(os.path.join(data_dir, "residues.json")) as f:
        residue_props = json.load(f)

    if args.sequence.startswith("example_"):
        file_path = os.path.join(data_dir, args.sequence)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Example file {file_path} not found")
        with open(file_path) as f:
            sequence = f.read().strip()
    else:
        sequence = args.sequence

    if args.runs == 1:
        result = run_simulation(
            sequence=sequence, 
            residue_props=residue_props, 
            steps=args.steps, 
            seed=args.seed, 
            plot=True,
        )

        print(f"Sequence: {sequence}")
        print(f"Length: {len(sequence)}")
        print(f"Final Energy: {result['final_energy']:.2f}")
        print(f"Lowest Energy: {result['min_energy']:.2f}")
        print(f"Move counts: {result['move_counts']}")
        print(f"Runtime: {result['runtime']:.2f} seconds")
        print(f"Structures saved to {structure_dir}")
        print(f"Logs saved to {log_dir}")

    else:
        total_runtime = 0
        for i in range(1, args.runs + 1):
            result = run_simulation(
                sequence=sequence,
                residue_props=residue_props,
                steps=args.steps,
                seed=args.seed,
                run_id=i,
                plot=False,
            )

            print(f"Run {i}")
            print(f"Final Energy: {result['final_energy']:.2f}")
            print(f"Lowest Energy: {result['min_energy']:.2f}")
            print(f"Move counts: {result['move_counts']}")
            print(f"Runtime: {result['runtime']:.2f} seconds\n")
            total_runtime += result['runtime']
        print(f"Runtime: {total_runtime:.2f} seconds\n")

if __name__ == "__main__":
    main()
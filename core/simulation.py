import random
import time
from collections import Counter

from model.chain import PeptideChain
from model.lattice import Lattice
from folding.energy import EnergyModel
from folding.relax import relax_chain
from folding.moves import set_pivot_probability, PIVOT_P

def run_simulation(
    sequence,
    residue_props,
    steps,
    seed,
    run_id=None,
    # Temperature / annealing
    T_start=2.0,
    T_end=0.5,
    # Energy model parameters
    alpha=0.2,
    eps_HH=1.0,
    eps_HP=0.3,
    eps_PP=0.1,
    eps_Q=1.0,
    # Monte Carlo move settings
    pivot_p=None,
):
    """
    Run a single Monte Carlo simulation.
    Returns a dictionary with simulation results including:
    - final_energy, min_energy
    - move_counts
    - runtime
    - structure
    - trajectory
    - contact_graph
    """
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

    # Allow runtime control of pivot move probability
    if pivot_p is not None:
        set_pivot_probability(pivot_p)
    else:
        set_pivot_probability(PIVOT_P)

    energy_model = EnergyModel(
        alpha=alpha,
        eps_HH=eps_HH,
        eps_HP=eps_HP,
        eps_PP=eps_PP,
        eps_Q=eps_Q,
    )
    trajectory, best_chain = relax_chain(
        chain,
        lattice,
        energy_model,
        n_steps=steps,
        T_start=T_start,
        T_end=T_end,
    )

    structure = best_chain.get_structure()
    runtime = time.time() - start_time

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
        "structure": structure,
        "trajectory": trajectory
    }
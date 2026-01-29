import math
import random
import copy
from folding.moves import get_possible_moves, apply_move

def relax_chain(chain, lattice, energy_model, n_steps=1000, T_start=2.0, T_end=0.5):
    """Metropolis Monte Carlo iteration, returning the complete trajectory"""
    trajectory = []

    min_energy = float("inf")
    best_structure = None

    for step in range(n_steps):
        # Exponential annealing
        temperature = T_start * (T_end / T_start) ** (step / (n_steps - 1))

        # Compute energies before move
        old_energies = energy_model.compute_local_energies(chain)
        old_energy = energy_model.compute_total_energy(old_energies)

        # Generate all valid moves
        moves = get_possible_moves(chain)
        if not moves:
            trajectory.append({
                "step": step,
                "temperature": temperature,
                "delta_E": 0,
                "accepted": False,
                "move_type": None,
                "total_energy": old_energy,
                "local_energies": old_energies,
                "total_moves": 0,
                "positions": [
                    {
                        "index": c.index,
                        "x": c.position[0],
                        "y": c.position[1],
                        "z": c.position[2],
                    }
                    for c in chain.residues
                ],
            })
            continue
        num_moves = len(moves)

        # Pick a random move
        move = random.choice(moves)
        affected = move["cube_indices"]

        # Save old positions for rollback
        old_positions = {i: chain.residues[i].position for i in affected}

        # Apply move
        apply_move(chain, move)

        # Compute energies after move
        new_energies = energy_model.compute_local_energies(chain)
        new_energy = energy_model.compute_total_energy(new_energies)

        delta_E = new_energy - old_energy

        accepted = True
        if delta_E > 0:
            if random.random() >= math.exp(-delta_E / temperature):
                accepted = False
                # Roll back
                for idx, pos in old_positions.items():
                    lattice.remove_cube(chain.residues[idx])
                    chain.residues[idx].set_position(pos)
                    lattice.add_cube(chain.residues[idx])

                total_energy = old_energy
                local_energies = old_energies
        else:
            total_energy = new_energy
            local_energies = new_energies

        # Track lowest-energy structure
        if total_energy < min_energy:
            min_energy = total_energy
            best_structure = copy.deepcopy(chain)

        # Log step info
        trajectory.append({
            "step": step,
            "temperature": temperature,
            "delta_E": delta_E,
            "accepted": accepted,
            "move_type": move["type"],
            "total_energy": total_energy,
            "local_energies": local_energies,
            "total_moves": num_moves,
            "positions": [
                {
                    "index": c.index,
                    "x": c.position[0],
                    "y": c.position[1],
                    "z": c.position[2],
                }
                for c in chain.residues
            ],
        })

    return trajectory, best_structure
import math
import random
from folding.moves import get_possible_moves, apply_move

def relax_chain(chain, lattice, energy_model, n_steps=1000, T_start=2.0, T_end=0.5):
    trajectory = []

    for step in range(n_steps):
        # Linear annealing (decrease temperature from T_start to T_end)
        temperature = T_start - (T_start - T_end) * (step / n_steps)

        # Generate all valid moves
        moves = get_possible_moves(chain)
        if not moves:
            continue # skip if no moves possible

        # Pick a random move
        move = random.choice(moves)
        affected = move["cube_indices"]

        # Save old positions for rollback if move rejected
        old_positions = {i: chain.residues[i].position for i in affected}

        # Compute energies before move
        old_energy = energy_model.compute_total_energy(chain)

        # Apply move
        apply_move(chain, move)

        # Compute energies after move
        new_energy = energy_model.compute_total_energy(chain)

        # Change in energy for affected residues
        delta_E = new_energy - old_energy

        accepted = True
        # Metropolis acceptance criterion (using Boltzmann probability)
        if delta_E > 0 and random.random() >= math.exp(-delta_E / temperature):
            accepted = False
            # Undo move if rejected
            for idx, pos in old_positions.items():
                lattice.remove_cube(chain.residues[idx])
                chain.residues[idx].set_position(pos)
                lattice.add_cube(chain.residues[idx])

        # Log step info including move type
        trajectory.append({
            "step": step,
            "temperature": temperature,
            "delta_E": delta_E,
            "accepted": accepted,
            "move_type": move["type"],
            "total_energy": energy_model.compute_total_energy(chain),
            "local_energies": energy_model.compute_local_energies(chain),
            "positions": [
                {"index": c.index, "x": c.position[0], "y": c.position[1], "z": c.position[2]}
                for c in chain.residues
            ]
        })

    return trajectory
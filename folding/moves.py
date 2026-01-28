import random

PIVOT_P = 0.25  # Probability of attempting a pivot move
CRANKSHAFT_P = 0.5 # Probability of attempting a crankshaft move

def set_probabilities(p, c):
    """Set the global probability of attempting pivot and crankshaft moves."""
    global PIVOT_P
    PIVOT_P = float(p)
    global CRANKSHAFT_P
    CRANKSHAFT_P = float(c)

def are_adjacent(pos1, pos2):
    """Check if two lattice positions are adjacent."""
    dx = abs(pos1[0] - pos2[0])
    dy = abs(pos1[1] - pos2[1])
    dz = abs(pos1[2] - pos2[2])
    return dx + dy + dz == 1 # only face-adjacent positions

def get_possible_moves(chain):
    """Get all valid moves for the chain at current conformation."""
    moves = []
    residues = chain.residues
    lattice = chain.lattice
    n = len(residues)

    # End moves: move the first or last residue
    if n >= 2:
        for end_index in [0, n - 1]:
            cube = residues[end_index]
            neighbor_index = 1 if end_index == 0 else n - 2
            bonded_neighbor = residues[neighbor_index]

            for pos in lattice.get_neighbours(cube.position):
                if lattice.is_occupied(pos):
                    continue
                # only require adjacency to bonded neighbour
                if are_adjacent(pos, bonded_neighbor.position):
                    moves.append({
                        "type": "end",
                        "cube_indices": [cube.index],
                        "new_positions": [pos]
                    })

    # Corner moves: move interior residue diagonally if adjacent to previous and next
    for cube in residues[1:-1]:
        prev_cube = residues[cube.index - 1]
        next_cube = residues[cube.index + 1]

        for pos in lattice.get_neighbours(cube.position):
            if lattice.is_occupied(pos):
                continue
            # allow move if adjacent to at least one neighbour
            if are_adjacent(prev_cube.position, pos) and are_adjacent(next_cube.position, pos):
                moves.append({
                    "type": "corner",
                    "cube_indices": [cube.index],
                    "new_positions": [pos]
                })

    # Pivot moves: rotate a subchain around a pivot point
    if random.random() < PIVOT_P:
        for pivot_index in range(1, n - 1):
            downstream = residues[pivot_index + 1:]
            if not downstream:
                continue

            rotated_positions = rotate_subchain(
                residues[pivot_index],
                downstream,
                lattice
            )

            if rotated_positions:
                moves.append({
                    "type": "pivot",
                    "cube_indices": [c.index for c in downstream],
                    "new_positions": rotated_positions
                })
    
    # Crankshaft moves: rotate two consecutive interior residues
    if random.random() < PIVOT_P:
        for i in range(1, n - 2):
            new_positions = crankshaft_positions(chain, i, lattice)
            if new_positions:
                moves.append({
                    "type": "crankshaft",
                    "cube_indices": [i, i + 1],
                    "new_positions": new_positions
                })

    return moves

def apply_move(chain, move):
    """Apply a move to the chain and update lattice occupancy."""
    lattice = chain.lattice
    indices = move["cube_indices"]

    # Remove old positions from lattice
    for idx in indices:
        lattice.remove_cube(chain.residues[idx])

    # Set new positions and update lattice
    for idx, pos in zip(indices, move["new_positions"]):
        chain.residues[idx].set_position(pos)
        lattice.add_cube(chain.residues[idx])

def rotate(v, axis):
    """Rotate a vector around a given axis (0=x,1=y,2=z)."""
    x, y, z = v
    if axis == 0:
        return (x, -z, y)
    elif axis == 1:
        return (z, y, -x)
    else:
        return (-y, x, z)

def rotate_subchain(pivot_cube, subchain, lattice):
    """Rotate a subchain around pivot_cube."""
    vectors = []
    prev = pivot_cube.position
    # Compute relative vectors from pivot
    for cube in subchain:
        vectors.append((
            cube.position[0] - prev[0],
            cube.position[1] - prev[1],
            cube.position[2] - prev[2]
        ))
        prev = cube.position

    axis = random.choice([0, 1, 2]) # choose random rotation axis
    rotated_vectors = [rotate(v, axis) for v in vectors]

    # Compute new absolute positions
    positions = []
    current = pivot_cube.position
    for v in rotated_vectors:
        next_pos = (
            current[0] + v[0],
            current[1] + v[1],
            current[2] + v[2]
        )
        if lattice.is_occupied(next_pos):
            return None # invalid move due to overlap
        positions.append(next_pos)
        current = next_pos

    return positions

def crankshaft_positions(chain, i, lattice):
    """Attempt a crankshaft move on residues i and i+1."""
    residues = chain.residues

    a = residues[i - 1].position
    b = residues[i].position
    c = residues[i + 1].position
    d = residues[i + 2].position

    # Endpoints must be adjacent (axis length = 2)
    if not are_adjacent(a, d):
        return None

    # Vector directions
    vb = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    vc = (c[0] - d[0], c[1] - d[1], c[2] - d[2])

    axis = random.choice([0, 1, 2])

    vb_rot = rotate(vb, axis)
    vc_rot = rotate(vc, axis)

    new_b = (a[0] + vb_rot[0], a[1] + vb_rot[1], a[2] + vb_rot[2])
    new_c = (d[0] + vc_rot[0], d[1] + vc_rot[1], d[2] + vc_rot[2])

    # Must preserve chain connectivity
    if not (are_adjacent(new_b, new_c)):
        return None

    # Must not overlap lattice
    for pos in (new_b, new_c):
        if lattice.is_occupied(pos):
            return None

    return [new_b, new_c]
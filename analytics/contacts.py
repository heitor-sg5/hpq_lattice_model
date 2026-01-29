import itertools
from collections import defaultdict
import numpy as np

def build_contact_graph(structure, lattice):
    """
    Build a contact graph from a final folded structure.
    Nodes are residue indexes, edges are non-bonded nearest neighbours.
    """
    residues = structure["residues"]
    positions = {r["index"]: (r["x"], r["y"], r["z"]) for r in residues}
    graph = {}

    # Check all unordered residue pairs
    for i, j in itertools.combinations(positions.keys(), 2):
        if abs(i - j) <= 1:
            continue  # skip covalently bonded neighbours
        # Add edge if residues occupy neighbouring lattice sites
        if positions[j] in lattice.get_neighbours(positions[i]):
            graph[(i, j)] = 1.0  # binary contact
    return graph

def consensus_contact_graph(graphs):
    """Compute a consensus contact graph across multiple independent runs."""
    consensus = defaultdict(float)
    # Count contact occurrences across runs
    for g in graphs:
        for edge in g:
            consensus[edge] += 1.0
    # Normalize by number of runs to obtain frequencies
    n = len(graphs)
    for edge in consensus:
        consensus[edge] /= n
    return dict(consensus)

def contact_frequency_matrix(consensus, n_residues):
    """Convert a contact graph into a symmetric contact-frequency matrix."""
    M = np.zeros((n_residues, n_residues))
    # Matrix entry (i, j) = probability that residues i and j are in contact
    for (i, j), w in consensus.items():
        M[i, j] = w
        M[j, i] = w  # enforce symmetry
    return M

def get_native(structure):
    """Computes native contacts from a chain structure dict."""
    native_contacts = set()
    residues = structure["residues"]
    N = len(residues)
    for i, j in itertools.combinations(range(N), 2):
        # skip covalent neighbors
        if abs(i - j) == 1:
            continue
        # extract positions from the dict
        pos_i = (residues[i]["x"], residues[i]["y"], residues[i]["z"])
        pos_j = (residues[j]["x"], residues[j]["y"], residues[j]["z"])
        # nearest neighbor check (Manhattan distance == 1)
        if sum(abs(a - b) for a, b in zip(pos_i, pos_j)) == 1:
            native_contacts.add((i, j))
    return native_contacts

def total_neighbours(positions):
    """Computes the total number of contacts."""
    total = 0
    indices = [p["index"] for p in positions]
    for i, j in itertools.combinations(indices, 2):
        # skip covalent neighbors
        if abs(i - j) == 1:
            continue
        pos_i = (positions[i]["x"], positions[i]["y"], positions[i]["z"])
        pos_j = (positions[j]["x"], positions[j]["y"], positions[j]["z"])
        if sum(abs(a - b) for a, b in zip(pos_i, pos_j)) == 1:
            total += 1
    return total

def get_native_frequency(native_contacts, positions):
    """Computes the fraction of native contacts present in current structure."""
    if not native_contacts:
        return 0.0
    count = 0
    for i, j in native_contacts:
        pos_i = (positions[i]["x"], positions[i]["y"], positions[i]["z"])
        pos_j = (positions[j]["x"], positions[j]["y"], positions[j]["z"])
        if sum(abs(a - b) for a, b in zip(pos_i, pos_j)) == 1:
            count += 1

    return count / len(native_contacts)
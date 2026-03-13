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
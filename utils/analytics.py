import itertools
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist

# Build a contact graph from a final folded structure, where nodes are 
# residue indexes and edges are non-bonded nearest neighbours
def build_contact_graph(structure, lattice):
    # Extract residue list from structure dictionary
    residues = structure["residues"]

    # Map residue index (i.e. lattice coordinates)
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

# Compute a consensus contact graph across multiple independent runs
def consensus_contact_graph(graphs):
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

# Convert a contact graph into a symmetric contact-frequency matrix
def contact_frequency_matrix(consensus, n_residues):
    M = np.zeros((n_residues, n_residues))

    # Matrix entry (i, j) = probability that residues i and j are in contact
    for (i, j), w in consensus.items():
        M[i, j] = w
        M[j, i] = w # enforce symmetry
    return M

# Plot the contact-frequency matrix as a 2D heatmap
def plot_contact_matrix(graphs, sequence):
    n_residues = len(sequence)

    # Build consensus contact graph across runs
    consensus = consensus_contact_graph(graphs)
    matrix = contact_frequency_matrix(consensus, n_residues)

    # Hierarchical clustering using scipy
    dist = pdist(matrix, metric="correlation")
    Z = linkage(dist, method="average")

    # Labels
    labels = [f"{aa}{i}" for i, aa in enumerate(sequence)]
    fig, (ax_heat, ax_dendro) = plt.subplots(1, 2, figsize=(12, 6), gridspec_kw={"width_ratios": [3, 2]})

    # Heatmap (sequence-ordered)
    im = ax_heat.imshow(matrix, origin="lower", cmap="viridis")
    ax_heat.set_title("Contact frequency matrix")
    ax_heat.set_xlabel("Residue index")
    ax_heat.set_ylabel("Residue index")
    plt.colorbar(im, ax=ax_heat, label="Contact frequency")

    # Cladogram
    dendrogram(Z, orientation="left", labels=labels, ax=ax_dendro, leaf_font_size=8)
    ax_dendro.set_xlabel("Distance")
    ax_dendro.set_title("Contact-profile hierarchy")

    plt.tight_layout()
    plt.show()

# Plot total energy over simulation steps
def plot_energy_vs_steps(trajectory=None, trajectories=None):
    if trajectories is not None:
        min_len = min(len(traj) for traj in trajectories)
        steps = np.array([traj[i]["step"] for i in range(min_len) for traj in trajectories[:1]])
        energies = np.array([[traj[i]["total_energy"] for i in range(min_len)] for traj in trajectories])
        mean_energy = energies.mean(axis=0)
        std_energy = energies.std(axis=0)
        plt.figure(figsize=(8, 5))
        plt.plot(steps, mean_energy, linewidth=2, label="Mean energy")
        plt.fill_between(steps, mean_energy - std_energy, mean_energy + std_energy, alpha=0.3, label="±1 std")
    else:
        steps = [step["step"] for step in trajectory]
        energies = [step["total_energy"] for step in trajectory]
        plt.figure(figsize=(8, 5))
        plt.plot(steps, energies, linewidth=2)
    plt.xlabel("Step")
    plt.ylabel("Energy")
    plt.title("Metropolis MC Progression")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
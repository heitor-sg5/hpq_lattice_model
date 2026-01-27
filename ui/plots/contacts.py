import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist
import plotly.graph_objects as go

from model.lattice import Lattice
from analytics.contacts import (
    build_contact_graph,
    consensus_contact_graph,
    contact_frequency_matrix,
)

def contact_heatmap_from_runs(results, sequence):
    """Create contact frequency heatmap from multiple runs."""
    if not results:
        return None

    lattice = Lattice()
    graphs = []
    for r in results:
        structure = r["structure"]
        graphs.append(build_contact_graph(structure, lattice))

    consensus = consensus_contact_graph(graphs)
    matrix = contact_frequency_matrix(consensus, len(sequence))

    fig = go.Figure(
        data=go.Heatmap(
            z=matrix,
            colorscale="Viridis",
            colorbar=dict(title="Contact frequency"),
        )
    )
    fig.update_layout(
        xaxis_title="Residue index",
        yaxis_title="Residue index",
        height=400,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig

def cladogram_from_runs(results, sequence):
    """Create cladogram (dendrogram) from contact patterns."""
    if not results:
        return None

    # Need at least two residues for a meaningful dendrogram
    if len(sequence) < 2:
        return None

    lattice = Lattice()
    graphs = []
    for r in results:
        structure = r["structure"]
        graphs.append(build_contact_graph(structure, lattice))

    consensus = consensus_contact_graph(graphs)
    matrix = contact_frequency_matrix(consensus, len(sequence))

    # Hierarchical clustering
    try:
        dist = pdist(matrix, metric="correlation")
        if dist.size == 0:
            return None
        Z = linkage(dist, method="average")
    except Exception:
        # If clustering fails due to degenerate distances, skip plotting
        return None

    labels = [f"{aa}{i}" for i, aa in enumerate(sequence)]
    fig, ax = plt.subplots(figsize=(4, 5))
    dendrogram(Z, orientation="right", labels=labels, ax=ax, leaf_font_size=8)
    ax.set_xlabel("Distance")
    plt.tight_layout()
    return fig
import numpy as np
import plotly.graph_objects as go

def plot_moves_histogram_single(result):
    """Plot move counts histogram for a single run."""
    move_counts = result.get("move_counts", {})
    if not move_counts:
        move_counts = {}
    types = list(move_counts.keys())
    counts = [move_counts[t] for t in types]

    fig = go.Figure(
        data=go.Bar(
            x=types,
            y=counts,
            name="Move count",
        )
    )
    fig.update_layout(
        xaxis_title="Move type",
        yaxis_title="Count",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig

def plot_moves_histogram_multi(results):
    """Plot move counts histogram for multiple runs with error bars."""
    # Collect all move types observed across runs
    all_types = set()
    for r in results:
        all_types.update(r.get("move_counts", {}).keys())
    types = sorted(all_types)
    if not types:
        types = []

    n_runs = len(results)
    counts_matrix = np.zeros((n_runs, len(types)), dtype=float)
    for i, r in enumerate(results):
        mc = r.get("move_counts", {})
        for j, t in enumerate(types):
            counts_matrix[i, j] = mc.get(t, 0.0)

    mean_counts = counts_matrix.mean(axis=0)
    std_counts = counts_matrix.std(axis=0)

    fig = go.Figure(
        data=go.Bar(
            x=types,
            y=mean_counts,
            error_y=dict(type="data", array=std_counts),
            name="Mean count per run",
        )
    )
    fig.update_layout(
        xaxis_title="Move type",
        yaxis_title="Count",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig
import numpy as np
import plotly.graph_objects as go

def plot_moves_histogram_single(result, eps=1.0):
    """Plot move counts histogram for a single run."""
    move_counts = result.get("move_counts", {})
    if not move_counts:
        move_counts = {}
    types = list(move_counts.keys())
    counts = np.array([move_counts[t] for t in types], dtype=float)
    log_counts = np.log10(counts + eps)

    fig = go.Figure(
        data=go.Bar(
            x=types,
            y=log_counts,
            name="Move count",
        )
    )
    fig.update_layout(
        xaxis_title="Move type",
        yaxis_title="Log count",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig

def plot_moves_histogram_multi(results, eps=1.0):
    """Plot move counts histogram for multiple runs with error bars."""
    # Collect all move types observed across runs
    all_types = set()
    for r in results:
        all_types.update(r.get("move_counts", {}).keys())
    types = sorted(all_types)

    n_runs = len(results)
    n_types = len(types)

    # Build counts matrix
    counts_matrix = np.zeros((n_runs, n_types), dtype=float)
    for i, r in enumerate(results):
        mc = r.get("move_counts", {})
        for j, t in enumerate(types):
            counts_matrix[i, j] = mc.get(t, 0.0)

    # Log-transform (add eps to avoid log(0))
    log_counts = np.log10(counts_matrix + eps)

    mean_log_counts = log_counts.mean(axis=0)
    std_log_counts = log_counts.std(axis=0)

    fig = go.Figure(
        data=go.Bar(
            x=types,
            y=mean_log_counts,
            error_y=dict(type="data", array=std_log_counts),
            name="Mean log10 count per run",
        )
    )
    fig.update_layout(
        xaxis_title="Move type",
        yaxis_title="Log count",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig
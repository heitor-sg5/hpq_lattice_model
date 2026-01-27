import numpy as np
import plotly.graph_objects as go

from analytics.trajectories import energy_trace_from_trajectory

def plot_energy_vs_step_interactive(trajectory):
    """Plot energy vs step for a single trajectory."""
    df = energy_trace_from_trajectory(trajectory)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["step"],
            y=df["energy"],
            mode="lines",
            name="Energy",
        )
    )
    fig.update_layout(
        xaxis_title="Step",
        yaxis_title="Total energy",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig

def plot_energy_multi_runs(trajectories):
    """Plot energy vs step for multiple runs with mean and std."""
    min_len = min(len(t) for t in trajectories)
    energies = np.array(
        [[traj[i]["total_energy"] for i in range(min_len)] for traj in trajectories]
    )
    steps = np.array([trajectories[0][i]["step"] for i in range(min_len)])
    mean_energy = energies.mean(axis=0)
    std_energy = energies.std(axis=0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=mean_energy,
            mode="lines",
            name="Mean energy",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([steps, steps[::-1]]),
            y=np.concatenate(
                [mean_energy - std_energy, (mean_energy + std_energy)[::-1]]
            ),
            fill="toself",
            fillcolor="rgba(0, 0, 255, 0.1)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=True,
            name="±1 std",
        )
    )
    fig.update_layout(
        xaxis_title="Step",
        yaxis_title="Total energy",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig
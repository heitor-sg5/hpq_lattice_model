import numpy as np
import plotly.graph_objects as go

def plot_temperature_vs_step_interactive(trajectory):
    """Plot temperature vs step for a single trajectory."""
    steps = [s["step"] for s in trajectory]
    temps = [s["temperature"] for s in trajectory]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=temps,
            mode="lines",
            name="Temperature",
        )
    )
    fig.update_layout(
        xaxis_title="Step",
        yaxis_title="Temperature",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig

def plot_temperature_multi_runs(trajectories):
    """Plot temperature vs step for multiple runs with mean and std."""
    min_len = min(len(t) for t in trajectories)
    temps = np.array(
        [[traj[i]["temperature"] for i in range(min_len)] for traj in trajectories]
    )
    steps = np.array([trajectories[0][i]["step"] for i in range(min_len)])
    mean_temp = temps.mean(axis=0)
    std_temp = temps.std(axis=0)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=steps,
            y=mean_temp,
            mode="lines",
            name="Mean temperature",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=np.concatenate([steps, steps[::-1]]),
            y=np.concatenate(
                [mean_temp - std_temp, (mean_temp + std_temp)[::-1]]
            ),
            fill="toself",
            fillcolor="rgba(255, 0, 0, 0.1)",
            line=dict(color="rgba(0,0,0,0)"),
            showlegend=True,
            name="±1 std",
        )
    )
    fig.update_layout(
        xaxis_title="Step",
        yaxis_title="Temperature",
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
    )
    return fig
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def build_positions_from_step(step):
    """Extract positions from trajectory step."""
    positions = step["positions"]
    df = pd.DataFrame(positions)
    df = df.sort_values("index")
    return df

def build_color_values(df_positions, residue_props, local_energies, sequence, mode):
    """Build color values array based on selected mode."""
    if mode == "Hydrophobicity":
        vals = np.array(
            [residue_props[aa]["hydrophobicity"] for aa in sequence], dtype=float
        )
    elif mode == "Charge":
        vals = np.array([residue_props[aa]["charge"] for aa in sequence], dtype=float)
    elif mode == "Local energy":
        vals = np.array(
            [local_energies.get(int(idx), 0.0) for idx in df_positions["index"]],
            dtype=float,
        )
    else:
        vals = np.zeros(len(df_positions), dtype=float)
    return vals

def plot_lattice_3d(step, residue_props, sequence, color_mode,):
    """Create 3D Plotly figure of lattice structure."""
    df_pos = build_positions_from_step(step)
    local_energies = step.get("local_energies", {})

    x = df_pos["x"].to_numpy()
    y = df_pos["y"].to_numpy()
    z = df_pos["z"].to_numpy()

    colors = build_color_values(df_pos, residue_props, local_energies, sequence, color_mode)

    # Normalize colors for a symmetric colorscale
    if np.any(colors):
        vmax = max(abs(colors.min()), abs(colors.max()))
        if vmax == 0:
            vmax = 1.0
    else:
        vmax = 1.0

    fig = go.Figure()

    # Bonds as a polyline
    fig.add_trace(
        go.Scatter3d(
            x=x,
            y=y,
            z=z,
            mode="lines+markers",
            marker=dict(
                size=6,
                color=colors,
                colorscale="RdBu",
                cmin=-vmax,
                cmax=vmax,
                colorbar=dict(title=color_mode),
            ),
            line=dict(color="black", width=2),
        )
    )

    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis_title="X",
            yaxis_title="Y",
            zaxis_title="Z",
            aspectmode="data",
        ),
    )
    return fig
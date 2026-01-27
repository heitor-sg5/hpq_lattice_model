import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analytics.contacts import get_native, total_neighbours, get_native_frequency

def plot_landscapes(results, smooth_sigma=2):
    """
    Smooth funnel surface landscape plots using linear interpolation and Gaussian smoothing.
    - Left: Energy (E) vs Native contacts (Q) vs log10(total moves) (P)
    - Right: Energy (E) vs Native contacts (Q) vs total neighbours (N)
    """
    single_run = len(results) == 1

    # Determine native contacts and trajectories
    if single_run:
        traj = results[0]["trajectory"]
        step_interval = 10
        native_contacts = get_native(results[0]["structure"])
        trajectories_to_use = [traj]
    else:
        step_interval = 100
        best_run = min(results, key=lambda r: r["min_energy"])
        native_contacts = get_native(best_run["structure"])
        trajectories_to_use = [r["trajectory"] for r in results]

    E_list, Q_list, N_list, P_list = [], [], [], []

    for traj in trajectories_to_use:
        for step in traj[::step_interval]:
            positions = step["positions"]
            E = step["total_energy"]
            Q = get_native_frequency(native_contacts, positions)
            N = total_neighbours(positions)
            P = np.log10(step.get("total_moves", 1))

            E_list.append(E)
            Q_list.append(Q)
            N_list.append(N)
            P_list.append(P)

    E_arr = np.array(E_list)
    Q_arr = np.array(Q_list)
    N_arr = np.array(N_list)
    P_arr = np.array(P_list)

    P_grid = np.linspace(P_arr.min(), P_arr.max(), 150)
    Q_grid = np.linspace(Q_arr.min(), Q_arr.max(), 150)
    P_mesh, Q_mesh = np.meshgrid(P_grid, Q_grid)

    # Linear interpolation
    E_mesh_left = griddata((P_arr, Q_arr), E_arr, (P_mesh, Q_mesh), method='linear')
    E_mesh_left = gaussian_filter(E_mesh_left, sigma=smooth_sigma)
    E_mesh_left = np.clip(E_mesh_left, E_arr.min(), E_arr.max())

    N_grid = np.linspace(N_arr.min(), N_arr.max(), 150)
    Q_grid2 = np.linspace(Q_arr.min(), Q_arr.max(), 150)
    N_mesh, Q_mesh2 = np.meshgrid(N_grid, Q_grid2)

    E_mesh_right = griddata((N_arr, Q_arr), E_arr, (N_mesh, Q_mesh2), method='linear')
    E_mesh_right = gaussian_filter(E_mesh_right, sigma=smooth_sigma)
    E_mesh_right = np.clip(E_mesh_right, E_arr.min(), E_arr.max())

    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{'type':'surface'}, {'type':'surface'}]],
        subplot_titles=["Entropy Landscape", "Fold Landscape"]
    )

    fig.add_trace(
        go.Surface(
            x=P_mesh,
            y=Q_mesh,
            z=E_mesh_left,
            colorscale='Viridis',
            showscale=False,
            opacity=0.9,
            name='E-Q-P Surface'
        ),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter3d(
            x=P_arr, y=Q_arr, z=E_arr,
            mode='markers',
            marker=dict(size=2, color='black'),
            name='Data Points'
        ),
        row=1, col=1
    )
    fig.update_scenes(
        dict(
            xaxis_title='Total moves, P',
            yaxis_title='Native contacts, Q',
            zaxis_title='Energy, E'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Surface(
            x=N_mesh,
            y=Q_mesh2,
            z=E_mesh_right,
            colorscale='Plasma',
            showscale=False,
            opacity=0.9,
            name='E-Q-N Surface'
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter3d(
            x=N_arr, y=Q_arr, z=E_arr,
            mode='markers',
            marker=dict(size=2, color='black'),
            name='Data Points'
        ),
        row=1, col=2
    )
    fig.update_scenes(
        dict(
            xaxis_title='Total neighbours, N',
            yaxis_title='Native contacts, Q',
            zaxis_title='Energy, E'
        ),
        row=1, col=2
    )

    fig.update_layout(
        height=600,
        width=1200,
        showlegend=False,
    )

    return fig
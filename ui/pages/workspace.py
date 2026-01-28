import streamlit as st

from ui.panels.toolbar import toolbar, run_simulations
from ui.panels.playback import playback_controls, sidebar_runs
from ui.panels.analytics import analytics_panel
from ui.panels.export import export_tools
from ui.plots.lattice import plot_lattice_3d
from utils.io import load_residue_props

def workspace():
    """Render main workspace with simulation controls and visualization."""
    if not st.session_state.get("results"):
        # First entry into workspace (run an initial simulation)
        residue_props = load_residue_props()
        run_simulations(residue_props)

    residue_props = load_residue_props()

    st.markdown(
        """
        <div style="position: sticky; top: 0; z-index: 100; background-color: white;">
        """,
        unsafe_allow_html=True,
    )
    toolbar(residue_props)
    st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns([1.2, 3, 1.5])

    with cols[0]:
        sidebar_runs()
        export_tools()

    results = st.session_state.get("results", [])
    if not results:
        return

    current_run_idx = st.session_state["current_run_index"]
    current_result = results[current_run_idx]
    trajectory = current_result["trajectory"]

    with cols[1]:
        color_mode = st.segmented_control(
            "Coloring",
            options=["Hydrophobicity", "Local energy", "Charge"],
            default=st.session_state.get("color_mode", "Hydrophobicity"),
        )
        st.session_state["color_mode"] = color_mode

        if trajectory:
            current_step_idx = st.session_state.get("current_step_index", 0)
            current_step = trajectory[current_step_idx]
            fig = plot_lattice_3d(
                current_step,
                residue_props=residue_props,
                sequence=st.session_state.get("sequence", ""),
                color_mode=color_mode,
            )
            st.plotly_chart(fig, use_container_width=True)
            playback_controls(trajectory)
        else:
            st.info("No trajectory recorded for this run.")

    with cols[2]:
        analytics_panel()

    # Allow returning to the landing page to enter a new peptide
    st.markdown("---")
    if st.button("Return to start page"):
        st.session_state["view"] = "landing"
        st.session_state["results"] = []
        st.session_state["sequence"] = ""
        st.rerun()
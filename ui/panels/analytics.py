import streamlit as st

from analytics.statistics import compute_statistics_table
from ui.plots.energy import plot_energy_vs_step_interactive, plot_energy_multi_runs
from ui.plots.temperature import plot_temperature_vs_step_interactive, plot_temperature_multi_runs
from ui.plots.landscape import plot_landscapes
from ui.plots.moves import plot_moves_histogram_single, plot_moves_histogram_multi
from ui.plots.contacts import contact_heatmap_from_runs, cladogram_from_runs

def analytics_panel():
    """Render analytics panel with tabs for different visualizations."""
    results = st.session_state.get("results", [])
    if not results:
        return

    tabs = st.tabs(["Energy", "Temperature", "Landscape", "Moves", "Contacts", "Cladogram"])

    with tabs[0]:
        if len(results) == 1:
            traj = results[0]["trajectory"]
            fig = plot_energy_vs_step_interactive(traj)
        else:
            trajectories = [r["trajectory"] for r in results]
            fig = plot_energy_multi_runs(trajectories)
        st.plotly_chart(fig, use_container_width=True)

    with tabs[1]:
        if len(results) == 1:
            traj = results[0]["trajectory"]
            fig = plot_temperature_vs_step_interactive(traj)
        else:
            trajectories = [r["trajectory"] for r in results]
            fig = plot_temperature_multi_runs(trajectories)
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        fig = plot_landscapes(results)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
    
    with tabs[3]:
        if len(results) == 1:
            fig = plot_moves_histogram_single(results[0])
        else:
            fig = plot_moves_histogram_multi(results)
        st.plotly_chart(fig, use_container_width=True)

    with tabs[4]:
        seq = st.session_state.get("sequence", "")
        fig = contact_heatmap_from_runs(results, seq)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)

    with tabs[5]:
        seq = st.session_state.get("sequence", "")
        fig = cladogram_from_runs(results, seq)
        if fig is not None:
            st.pyplot(fig, clear_figure=True)
        else:
            st.info(
                "Cladogram is only shown when there are at least two residues "
                "and a non-trivial contact pattern to cluster."
            )
    
    # Statistics table below all charts
    st.markdown("---")
    st.markdown("**Simulation Statistics**")
    seq = st.session_state.get("sequence", "")
    stats_df = compute_statistics_table(results, seq)
    st.dataframe(stats_df, use_container_width=True, hide_index=True)
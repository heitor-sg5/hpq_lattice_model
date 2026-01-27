import streamlit as st

def playback_controls(current_trajectory):
    """Render playback controls for trajectory navigation."""
    n_steps = len(current_trajectory)
    if n_steps == 0:
        st.info("No trajectory steps recorded.")
        return

    idx = st.session_state.get("current_step_index", 0)
    idx = max(0, min(idx, n_steps - 1))

    # Find step with lowest energy
    min_energy_idx = 0
    min_energy = current_trajectory[0]["total_energy"]
    for i, step in enumerate(current_trajectory):
        if step["total_energy"] < min_energy:
            min_energy = step["total_energy"]
            min_energy_idx = i

    col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 3, 1, 1])

    with col1:
        if st.button("⏮", key="playback_first", help="Jump to first step"):
            idx = 0
            st.session_state["current_step_index"] = idx
            st.rerun()
    with col2:
        if st.button("⏪", key="playback_prev", help="Previous step"):
            idx = max(0, idx - 1)
            st.session_state["current_step_index"] = idx
            st.rerun()
    with col3:
        if st.button("📍", help="Jump to lowest energy step", key="playback_min_energy"):
            idx = min_energy_idx
            st.session_state["current_step_index"] = idx
            st.rerun()
    with col5:
        if st.button("⏩", key="playback_next", help="Next step"):
            idx = min(n_steps - 1, idx + 1)
            st.session_state["current_step_index"] = idx
            st.rerun()
    with col6:
        if st.button("⏭", key="playback_last", help="Jump to last step"):
            idx = n_steps - 1
            st.session_state["current_step_index"] = idx
            st.rerun()

    with col4:
        new_idx = st.slider(
            "Step",
            min_value=0,
            max_value=n_steps - 1,
            value=idx,
            label_visibility="collapsed",
            key="playback_slider",
        )
        if new_idx != idx:
            idx = new_idx
            st.session_state["current_step_index"] = idx
            st.rerun()

    st.session_state["current_step_index"] = idx
    st.caption(f"Current step: {current_trajectory[idx]['step']} / {current_trajectory[-1]['step']}")

def sidebar_runs():
    """Render run selector in sidebar."""
    results = st.session_state.get("results", [])
    if not results:
        st.info("Run a simulation to populate runs.")
        return

    labels = [f"Run {i+1}" for i in range(len(results))]
    selected = st.radio("Runs", labels, index=st.session_state["current_run_index"])
    st.session_state["current_run_index"] = labels.index(selected)
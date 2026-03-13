import streamlit as st

def sidebar_runs():
    """Render run selector in sidebar as a dropdown."""
    results = st.session_state.get("results", [])
    if not results:
        st.info("Run a simulation to populate runs.")
        return

    # Create labels for each run
    labels = [f"Run {i+1}" for i in range(len(results))]

    # Get current index from session state, default to 0
    current_index = st.session_state.get("current_run_index", 0)
    current_index = min(current_index, len(labels) - 1)
    selected_label = st.selectbox("Select run", labels, index=current_index)

    # Update session state to reflect the selected run
    st.session_state["current_run_index"] = labels.index(selected_label)
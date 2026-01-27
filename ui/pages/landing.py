import streamlit as st

from core.validation import validate_sequence
from utils.io import load_residue_props


def landing_page():
    """Render landing page with sequence input."""
    residue_props = load_residue_props()
    
    st.markdown(
        """
        <div style="text-align:center; margin-top: 10vh;">
            <h1>HPQ Lattice Protein Folding</h1>
            <p style="color: #666; font-size: 1.1rem;">
                Explore Metropolis Monte Carlo folding trajectories on a cubic lattice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col = st.container()
    with col:
        sequence = st.text_input(
            "Peptide sequence",
            key="landing_sequence",
            placeholder="Enter sequence (e.g. MVTYP...)",
            label_visibility="collapsed",
        )

        with st.expander("Advanced options", expanded=False):
            params = st.session_state["params"]
            seed = st.number_input("Random seed", value=int(params["seed"]), step=1)
            runs = st.number_input(
                "Number of independent runs",
                min_value=1,
                max_value=32,
                value=int(params["runs"]),
                step=1,
            )
            steps = st.number_input(
                "Total MC steps", min_value=100, max_value=100000, value=int(params["steps"]), step=100
            )

        error = None
        if st.button("Start folding", type="primary"):
            sequence_upper = sequence.strip().upper()
            error = validate_sequence(sequence_upper, residue_props)
            if error is None:
                st.session_state["sequence"] = sequence_upper

            if error is None and sequence:
                # Persist parameters and move to workspace
                st.session_state["params"].update(
                    {"seed": int(seed), "runs": int(runs), "steps": int(steps)}
                )
                st.session_state["view"] = "workspace"
                st.rerun()

        if error:
            st.error(error)
import streamlit as st

from core.simulation import run_simulation

def run_simulations(residue_props):
    """Run simulations for all runs."""
    seq = st.session_state.get("sequence", "")
    params = st.session_state["params"]

    results = []
    for i in range(1, int(params["runs"]) + 1):
        r = run_simulation(
            sequence=seq,
            residue_props=residue_props,
            steps=int(params["steps"]),
            seed=int(params["seed"]),
            run_id=i if params["runs"] > 1 else None,
            T_start=float(params["T_start"]),
            T_end=float(params["T_end"]),
            alpha=float(params["alpha"]),
            eps_HH=float(params["eps_HH"]),
            eps_HP=float(params["eps_HP"]),
            eps_PP=float(params["eps_PP"]),
            eps_Q=float(params["eps_Q"]),
            pivot_p=float(params["pivot_p"]),
        )
        results.append(r)

    st.session_state["results"] = results
    st.session_state["current_run_index"] = 0
    st.session_state["current_step_index"] = 0

def toolbar(residue_props):
    """Render parameter toolbar."""
    params = st.session_state["params"]

    with st.container():
        cols = st.columns([2, 3, 3, 2])

        with cols[0]:
            st.markdown("**Temperature & Annealing**")
            params["T_start"] = st.number_input(
                "Initial T", value=float(params["T_start"]), key="T_start"
            )
            params["T_end"] = st.number_input(
                "Final T", value=float(params["T_end"]), key="T_end"
            )

        with cols[1]:
            st.markdown("**Energy scores**")
            params["alpha"] = st.number_input(
                "Solvent exposure (α)", value=float(params["alpha"]), key="alpha"
            )
            params["eps_HH"] = st.number_input(
                "Hydrophobic-hydrophobic (εHH)", value=float(params["eps_HH"]), key="eps_HH"
            )
            params["eps_HP"] = st.number_input(
                "Hydrophobic-polar (εHP)", value=float(params["eps_HP"]), key="eps_HP"
            )

        with cols[2]:
            st.markdown("**MC moves**")
            params["eps_PP"] = st.number_input(
                "Polar-polar (εPP)", value=float(params["eps_PP"]), key="eps_PP"
            )
            params["eps_Q"] = st.number_input(
                "Charge-charge (εQQ)", value=float(params["eps_Q"]), key="eps_Q"
            )
            params["pivot_p"] = st.slider(
                "Pivot move probability",
                min_value=0.0,
                max_value=1.0,
                value=float(params["pivot_p"]),
            )

        with cols[3]:
            st.markdown("**Randomness & steps**")
            params["steps"] = st.number_input(
                "MC steps",
                min_value=100,
                max_value=100000,
                value=int(params["steps"]),
                step=100,
            )
            params["seed"] = st.number_input(
                "Seed", value=int(params["seed"]), step=1
            )
            params["runs"] = st.number_input(
                "Runs", min_value=1, max_value=32, value=int(params["runs"]), step=1
            )

        st.session_state["params"] = params

        rerun = st.button("Re-run simulation", type="primary")
        if rerun:
            run_simulations(residue_props)
            st.rerun()
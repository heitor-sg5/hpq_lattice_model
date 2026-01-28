import numpy as np
import pandas as pd

def compute_statistics_table(results, sequence):
    """Compute useful statistics for display."""
    stats_data = []
    
    if len(results) == 1:
        r = results[0]
        traj = r["trajectory"]
        initial_energy = traj[0]["total_energy"] if traj else 0.0
        final_energy = r["final_energy"]
        min_energy = r["min_energy"]
        min_step = None
        if traj:
            min_entry = min(traj, key=lambda s: s["total_energy"])
            min_step = min_entry["step"]
        acceptance_rate = sum(1 for s in traj if s.get("accepted", False)) / len(traj) if traj else 0.0
        
        stats_data.append({
            "Metric": "Sequence length",
            "Value": f"{len(sequence)}",
        })
        stats_data.append({
            "Metric": "Total MC steps",
            "Value": f"{len(traj)}",
        })
        stats_data.append({
            "Metric": "Runtime (seconds)",
            "Value": f"{r['runtime']:.2f}",
        })
        stats_data.append({
            "Metric": "Initial energy",
            "Value": f"{initial_energy:.3f}",
        })
        stats_data.append({
            "Metric": "Final energy",
            "Value": f"{final_energy:.3f}",
        })
        stats_data.append({
            "Metric": "Minimum energy",
            "Value": f"{min_energy:.3f} (Step: {min_step})",
        })
        stats_data.append({
            "Metric": "Energy change",
            "Value": f"{final_energy - initial_energy:.3f}",
        })
        stats_data.append({
            "Metric": "Acceptance rate",
            "Value": f"{acceptance_rate:.1%}",
        })
        
        # Move counts
        move_counts = r.get("move_counts", {})
        for move_type, count in sorted(move_counts.items()):
            stats_data.append({
                "Metric": f"{move_type.capitalize()} moves",
                "Value": f"{count}",
            })
    else:
        # Multiple runs (aggregate statistics)
        trajectories = [r["trajectory"] for r in results]
        runtimes = [r["runtime"] for r in results]

        final_energies = [r["final_energy"] for r in results]
        best_final_idx = int(np.argmin(final_energies))
        best_final_run = best_final_idx + 1
        best_final_traj = trajectories[best_final_idx]
        best_final_step = best_final_traj[-1]["step"] if best_final_traj else None

        min_energies = [r["min_energy"] for r in results]
        best_min_energy = np.inf
        best_min_run = None
        best_min_step = None
        for run_idx, traj in enumerate(trajectories):
            if not traj:
                continue
            min_entry = min(traj, key=lambda s: s["total_energy"])
            if min_entry["total_energy"] < best_min_energy:
                best_min_energy = min_entry["total_energy"]
                best_min_run = run_idx + 1
                best_min_step = min_entry["step"]

        initial_energies = [t[0]["total_energy"] if t else 0.0 for t in trajectories]
        energy_changes = [fe - ie for fe, ie in zip(final_energies, initial_energies)]
        
        acceptance_rates = []
        for traj in trajectories:
            if traj:
                acc_rate = sum(1 for s in traj if s.get("accepted", False)) / len(traj)
                acceptance_rates.append(acc_rate)
        
        stats_data.append({
            "Metric": "Sequence length",
            "Value": f"{len(sequence)}",
        })
        stats_data.append({
            "Metric": "Number of runs",
            "Value": f"{len(results)}",
        })
        stats_data.append({
            "Metric": "Total MC steps",
            "Value": f"{len(trajectories[0]) if trajectories else 0}",
        })
        stats_data.append({
            "Metric": "Mean runtime (s)",
            "Value": f"{np.mean(runtimes):.2f}",
        })
        stats_data.append({
            "Metric": "Total runtime (s)",
            "Value": f"{sum(runtimes):.2f}",
        })
        stats_data.append({
            "Metric": "Mean final energy",
            "Value": f"{np.mean(final_energies):.3f} ± {np.std(final_energies):.3f}",
        })
        stats_data.append({
            "Metric": "Best final energy",
            "Value": f"{np.min(final_energies):.3f} (Run: {best_final_run}, Step: {best_final_step})",
        })
        stats_data.append({
            "Metric": "Mean minimum energy",
            "Value": f"{np.mean(min_energies):.3f} ± {np.std(min_energies):.3f}",
        })
        stats_data.append({
            "Metric": "Best minimum energy",
            "Value": f"{np.min(min_energies):.3f} (Run: {best_min_run}, Step: {best_min_step})",
        })
        stats_data.append({
            "Metric": "Mean energy change",
            "Value": f"{np.mean(energy_changes):.3f} ± {np.std(energy_changes):.3f}",
        })
        if acceptance_rates:
            stats_data.append({
                "Metric": "Mean acceptance rate",
                "Value": f"{np.mean(acceptance_rates):.1%} ± {np.std(acceptance_rates):.1%}",
            })
        
        # Aggregate move counts
        all_move_types = set()
        for r in results:
            all_move_types.update(r.get("move_counts", {}).keys())
        for move_type in sorted(all_move_types):
            counts = [r.get("move_counts", {}).get(move_type, 0) for r in results]
            stats_data.append({
                "Metric": f"Mean {move_type} moves",
                "Value": f"{np.mean(counts):.1f} ± {np.std(counts):.1f}",
            })
    
    return pd.DataFrame(stats_data)
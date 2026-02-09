#!/usr/bin/env python3
"""
Generate publication-quality figures for NeurIPS paper.

Figures:
- Figure 3: Rate-Time Compensation (DOE-027)
- Figure 4: Movement Effect (DOE-029)
- Figure 5: L2 RAG Falsification Forest Plot
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Publication style settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 9,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'lines.linewidth': 1.0,
    'patch.linewidth': 0.5,
    'grid.linewidth': 0.5,
    'legend.frameon': False,
    'legend.fontsize': 8,
})

OUTPUT_DIR = Path("/Users/sangyi/workspace/research/clau-doom/research/paper/figures")


def save_figure(fig, name: str):
    """Save figure as both PDF and PNG."""
    pdf_path = OUTPUT_DIR / f"{name}.pdf"
    png_path = OUTPUT_DIR / f"{name}.png"

    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    fig.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

    print(f"Saved {name}.pdf and {name}.png")


def figure_3_rate_time_compensation():
    """
    Figure 3: Rate-Time Compensation (DOE-027)
    Three-panel figure showing attack ratio effects.
    """
    # Data from DOE-027
    attack_ratios = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])

    # Kills (flat, not significant)
    kills_mean = np.array([16.00, 17.40, 15.43, 16.13, 15.40, 15.43, 14.70])
    kills_sd = np.array([6.09, 5.97, 5.84, 7.38, 5.71, 5.27, 5.00])

    # Survival time (decreasing)
    survival_mean = np.array([26.22, 25.66, 24.70, 24.49, 23.08, 22.99, 21.29])
    survival_sd = np.array([9.24, 9.52, 9.68, 11.49, 8.82, 8.65, 8.12])

    # Kill rate (increasing, significant)
    kr_mean = np.array([36.47, 41.51, 38.18, 40.03, 40.49, 41.12, 41.99])
    kr_sd = np.array([5.12, 6.24, 5.14, 5.32, 5.85, 6.85, 4.36])

    n = 30
    sem_kills = kills_sd / np.sqrt(n)
    sem_survival = survival_sd / np.sqrt(n)
    sem_kr = kr_sd / np.sqrt(n)

    # Create figure
    fig, axes = plt.subplots(1, 3, figsize=(7.0, 2.2))

    # Panel A: Kill Rate (upward trend, significant)
    ax = axes[0]
    ax.errorbar(attack_ratios, kr_mean, yerr=sem_kr,
                marker='o', markersize=4, capsize=3, capthick=0.5,
                color='#1f77b4', linewidth=1.0)
    ax.set_xlabel('Attack Ratio')
    ax.set_ylabel('Kill Rate (kills/min)')
    ax.set_ylim(30, 48)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8])
    ax.text(0.05, 0.95, '(A)', transform=ax.transAxes,
            fontweight='bold', va='top', fontsize=10)
    ax.text(0.5, 0.95, 'F=3.736, p=0.0015', transform=ax.transAxes,
            ha='center', va='top', fontsize=7, style='italic')

    # Panel B: Survival Time (downward trend)
    ax = axes[1]
    ax.errorbar(attack_ratios, survival_mean, yerr=sem_survival,
                marker='o', markersize=4, capsize=3, capthick=0.5,
                color='#ff7f0e', linewidth=1.0)
    ax.set_xlabel('Attack Ratio')
    ax.set_ylabel('Survival Time (sec)')
    ax.set_ylim(18, 32)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8])
    ax.text(0.05, 0.95, '(B)', transform=ax.transAxes,
            fontweight='bold', va='top', fontsize=10)
    ax.text(0.5, 0.95, 'p=0.016', transform=ax.transAxes,
            ha='center', va='top', fontsize=7, style='italic')

    # Panel C: Total Kills (flat, not significant)
    ax = axes[2]
    ax.errorbar(attack_ratios, kills_mean, yerr=sem_kills,
                marker='o', markersize=4, capsize=3, capthick=0.5,
                color='#2ca02c', linewidth=1.0)
    ax.set_xlabel('Attack Ratio')
    ax.set_ylabel('Total Kills')
    ax.set_ylim(10, 22)
    ax.set_xticks([0.2, 0.4, 0.6, 0.8])
    ax.text(0.05, 0.95, '(C)', transform=ax.transAxes,
            fontweight='bold', va='top', fontsize=10)
    ax.text(0.5, 0.95, 'F=0.617, p=0.717, n.s.', transform=ax.transAxes,
            ha='center', va='top', fontsize=7, style='italic')

    plt.tight_layout()
    save_figure(fig, "figure3_rate_time_compensation")
    plt.close(fig)


def figure_4_movement_effect():
    """
    Figure 4: Movement Effect (DOE-029)
    Two-panel figure comparing movers vs non-movers.
    """
    # Data from DOE-029
    conditions = ['attack\noverride', 'attack\nraw', 'rand50\noverride', 'rand50\nraw']
    kills_mean = np.array([10.00, 9.90, 16.13, 17.87])
    kills_sd = np.array([3.10, 2.51, 6.08, 7.02])
    kr_mean = np.array([37.59, 44.03, 41.11, 43.29])
    kr_sd = np.array([6.20, 4.00, 5.01, 5.17])

    n = 30
    sem_kills = kills_sd / np.sqrt(n)
    sem_kr = kr_sd / np.sqrt(n)

    # Group by movement
    non_movers_kills = kills_mean[:2]
    movers_kills = kills_mean[2:]
    non_movers_kr = kr_mean[:2]
    movers_kr = kr_mean[2:]

    non_movers_sem_kills = sem_kills[:2]
    movers_sem_kills = sem_kills[2:]
    non_movers_sem_kr = sem_kr[:2]
    movers_sem_kr = sem_kr[2:]

    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(5.5, 2.5))

    # Panel A: Kills (significant difference)
    ax = axes[0]
    x = np.arange(2)
    width = 0.35

    # Non-movers (orange/red)
    ax.bar(x - width/2, non_movers_kills, width,
           yerr=non_movers_sem_kills, capsize=3,
           color='#d62728', alpha=0.8, label='Non-movers')

    # Movers (blue/teal)
    ax.bar(x + width/2, movers_kills, width,
           yerr=movers_sem_kills, capsize=3,
           color='#17becf', alpha=0.8, label='Movers')

    ax.set_ylabel('Total Kills')
    ax.set_xticks(x)
    ax.set_xticklabels(['Override', 'Raw'])
    ax.set_ylim(0, 25)
    ax.legend(loc='upper left', fontsize=7)
    ax.text(0.05, 0.95, '(A)', transform=ax.transAxes,
            fontweight='bold', va='top', fontsize=10)

    # Add significance bracket
    y_max = 25
    y_bracket = 23
    ax.plot([0, 1], [y_bracket, y_bracket], 'k-', linewidth=0.5)
    ax.text(0.5, y_bracket + 0.5, 'p<0.001, d=1.408',
            ha='center', fontsize=7, style='italic')

    # Panel B: Kill Rate (NOT different)
    ax = axes[1]

    # Non-movers
    ax.bar(x - width/2, non_movers_kr, width,
           yerr=non_movers_sem_kr, capsize=3,
           color='#d62728', alpha=0.8, label='Non-movers')

    # Movers
    ax.bar(x + width/2, movers_kr, width,
           yerr=movers_sem_kr, capsize=3,
           color='#17becf', alpha=0.8, label='Movers')

    ax.set_ylabel('Kill Rate (kills/min)')
    ax.set_xticks(x)
    ax.set_xticklabels(['Override', 'Raw'])
    ax.set_ylim(0, 50)
    ax.text(0.05, 0.95, '(B)', transform=ax.transAxes,
            fontweight='bold', va='top', fontsize=10)
    ax.text(0.5, 0.95, 'p=0.180, n.s.', transform=ax.transAxes,
            ha='center', va='top', fontsize=7, style='italic')

    plt.tight_layout()
    save_figure(fig, "figure4_movement_effect")
    plt.close(fig)


def figure_5_l2_rag_forest_plot():
    """
    Figure 5: L2 RAG Falsification Forest Plot
    Effect sizes (Cohen's d) with 95% CIs for three L2 tests.
    """
    # Test labels
    tests = [
        'DOE-022 (3-action, n=120)',
        'DOE-024 (3-action, n=360)',
        'DOE-026 (5-action, n=150)',
    ]

    # Effect sizes (Cohen's d) and sample sizes
    d_values = np.array([0.189, 0.118, -0.10])
    n_per_group = np.array([30, 90, 30])

    # Calculate 95% CIs using SE(d) ≈ sqrt(2/n + d²/(2*n))
    def calculate_ci(d, n):
        se_d = np.sqrt(2/n + d**2/(2*n))
        ci_lower = d - 1.96 * se_d
        ci_upper = d + 1.96 * se_d
        return ci_lower, ci_upper

    ci_lower = []
    ci_upper = []
    for d, n in zip(d_values, n_per_group):
        lower, upper = calculate_ci(d, n)
        ci_lower.append(lower)
        ci_upper.append(upper)

    ci_lower = np.array(ci_lower)
    ci_upper = np.array(ci_upper)

    # Create figure
    fig, ax = plt.subplots(figsize=(5.5, 3.0))

    # Y positions
    y_positions = np.arange(len(tests))

    # Plot CIs
    for i, (test, d, lower, upper) in enumerate(zip(tests, d_values, ci_lower, ci_upper)):
        # Horizontal CI line
        ax.plot([lower, upper], [i, i], 'k-', linewidth=1.0)

        # Point estimate
        ax.plot(d, i, 'o', markersize=6, color='#1f77b4', markeredgecolor='black', markeredgewidth=0.5)

        # CI caps
        ax.plot([lower, lower], [i-0.1, i+0.1], 'k-', linewidth=1.0)
        ax.plot([upper, upper], [i-0.1, i+0.1], 'k-', linewidth=1.0)

    # Null line (d=0)
    ax.axvline(0, color='gray', linestyle='--', linewidth=1.0, zorder=0)

    # Labels
    ax.set_yticks(y_positions)
    ax.set_yticklabels(tests)
    ax.set_xlabel("Cohen's d (effect size)")
    ax.set_xlim(-0.8, 0.8)
    ax.set_ylim(-0.5, len(tests) - 0.5)
    ax.invert_yaxis()  # Top to bottom

    # Grid
    ax.grid(axis='x', alpha=0.3, linewidth=0.5)
    ax.set_axisbelow(True)

    # Add summary text
    ax.text(0.98, 0.02, 'All CIs overlap zero\n(no evidence for L2 advantage)',
            transform=ax.transAxes, ha='right', va='bottom',
            fontsize=7, style='italic', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8, edgecolor='gray'))

    plt.tight_layout()
    save_figure(fig, "figure5_l2_rag_forest_plot")
    plt.close(fig)


def main():
    """Generate all figures."""
    print("Generating NeurIPS figures...")

    figure_3_rate_time_compensation()
    print("✓ Figure 3: Rate-Time Compensation")

    figure_4_movement_effect()
    print("✓ Figure 4: Movement Effect")

    figure_5_l2_rag_forest_plot()
    print("✓ Figure 5: L2 RAG Falsification Forest Plot")

    print(f"\nAll figures saved to: {OUTPUT_DIR}")
    print("PDF: vector graphics for publication")
    print("PNG: preview at 300 dpi")


if __name__ == "__main__":
    main()

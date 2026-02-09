#!/usr/bin/env python3
"""
Generate Figure 2: DOE Progression Timeline for NeurIPS paper.

Publication-quality figure showing all 29 DOE experiments across phases,
with key milestones annotated.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from pathlib import Path

# Ensure output directory exists
output_dir = Path(__file__).parent
output_dir.mkdir(parents=True, exist_ok=True)

# DOE data structure
does = [
    # Phase 0: Infrastructure/Baselines
    {"id": 1, "phase": "0", "episodes": 210, "sig": False, "label": "Mock data bug", "milestone": False},
    {"id": 2, "phase": "0", "episodes": 150, "sig": False, "label": "INVALIDATED", "milestone": False},

    # Phase 1a: Parameter exploration
    {"id": 5, "phase": "1a", "episodes": 150, "sig": False, "label": "Zero variance", "milestone": False},
    {"id": 6, "phase": "1a", "episodes": 150, "sig": False, "label": "Bug fixed", "milestone": False},

    # Phase 1b: Scenario selection
    {"id": 7, "phase": "1b", "episodes": 210, "sig": False, "label": "Scenario selected", "milestone": False},
    {"id": 8, "phase": "1b", "episodes": 150, "sig": True, "label": "FIRST significant (p<0.001)", "milestone": True},
    {"id": 9, "phase": "1b", "episodes": 270, "sig": False, "label": "Parameters irrelevant", "milestone": False},

    # Phase 1c: Strategy landscape
    {"id": 10, "phase": "1c", "episodes": 150, "sig": False, "label": "Random ≈ structured", "milestone": False},
    {"id": 11, "phase": "1c", "episodes": 150, "sig": False, "label": "Strafing trade-off", "milestone": False},

    # Phase 1d: Action space
    {"id": 12, "phase": "1d", "episodes": 150, "sig": False, "label": "Compound = sequential", "milestone": False},
    {"id": 13, "phase": "1d", "episodes": 150, "sig": False, "label": "Attack ratio null", "milestone": False},
    {"id": 14, "phase": "1d", "episodes": 150, "sig": False, "label": "Threshold 0 optimal", "milestone": False},
    {"id": 15, "phase": "1d", "episodes": 150, "sig": False, "label": "basic.cfg unusable", "milestone": False},
    {"id": 16, "phase": "1d", "episodes": 150, "sig": False, "label": "corridor floor effect", "milestone": False},

    # Phase 1e: Replication/best-of-breed
    {"id": 17, "phase": "1e", "episodes": 150, "sig": False, "label": "L0 deficit replicated", "milestone": False},
    {"id": 18, "phase": "1e", "episodes": 150, "sig": False, "label": "adaptive_kill best kr", "milestone": False},
    {"id": 19, "phase": "1e", "episodes": 150, "sig": False, "label": "L0 worst (3x confirmed)", "milestone": False},
    {"id": 20, "phase": "1e", "episodes": 150, "sig": False, "label": "burst_3 best kills", "milestone": False},

    # Phase 2a: L2 RAG testing
    {"id": 21, "phase": "2a", "episodes": 180, "sig": False, "label": "Evolution converges", "milestone": False},
    {"id": 22, "phase": "2a", "episodes": 120, "sig": True, "label": "L2 null (1st)", "milestone": True},
    {"id": 23, "phase": "2a", "episodes": 360, "sig": False, "label": "doom_skill=72% variance", "milestone": False},

    # Phase 2b: Falsification
    {"id": 24, "phase": "2b", "episodes": 360, "sig": False, "label": "L2 null (2nd)", "milestone": False},
    {"id": 25, "phase": "2b", "episodes": 180, "sig": False, "label": "5-action tiers", "milestone": False},
    {"id": 26, "phase": "2b", "episodes": 150, "sig": True, "label": "L2 FALSIFIED (3rd)", "milestone": True},

    # Phase 2c: Mechanistic understanding
    {"id": 27, "phase": "2c", "episodes": 210, "sig": False, "label": "Rate-time compensation", "milestone": True},
    {"id": 28, "phase": "2c", "episodes": 150, "sig": False, "label": "Tactical invariance", "milestone": False},
    {"id": 29, "phase": "2c", "episodes": 120, "sig": True, "label": "Movement sole determinant (d=1.41)", "milestone": True},
]

# Phase metadata
phases = {
    "0": {"name": "Phase 0\nInfrastructure", "color": "#CCCCCC", "y": 0},
    "1a": {"name": "Phase 1a\nParameter\nExploration", "color": "#4A90E2", "y": 1},
    "1b": {"name": "Phase 1b\nScenario\nSelection", "color": "#5DA5E8", "y": 2},
    "1c": {"name": "Phase 1c\nStrategy\nLandscape", "color": "#70BAEE", "y": 3},
    "1d": {"name": "Phase 1d\nAction\nSpace", "color": "#83CFF4", "y": 4},
    "1e": {"name": "Phase 1e\nReplication", "color": "#96E4FA", "y": 5},
    "2a": {"name": "Phase 2a\nL2 RAG\nTesting", "color": "#FF8C42", "y": 6},
    "2b": {"name": "Phase 2b\nFalsification", "color": "#FF6B35", "y": 7},
    "2c": {"name": "Phase 2c\nMechanistic\nUnderstanding", "color": "#E63946", "y": 8},
}

# Set up figure with publication styling
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif'],
    'font.size': 9,
    'axes.labelsize': 9,
    'axes.titlesize': 10,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.0,
})

fig, (ax_main, ax_cumul) = plt.subplots(2, 1, figsize=(7, 4.5),
                                         height_ratios=[3, 1],
                                         sharex=True)

# Main timeline plot
for doe in does:
    phase_info = phases[doe["phase"]]
    y = phase_info["y"]
    x = doe["id"]

    # Marker style
    if doe["sig"]:
        marker = 'o'  # Filled circle for significant
        markersize = 7
        alpha = 1.0
    else:
        marker = 'o'  # Open circle for null
        markersize = 6
        alpha = 0.6

    # Plot marker
    ax_main.scatter(x, y,
                   c=phase_info["color"],
                   marker=marker,
                   s=markersize**2,
                   alpha=alpha,
                   edgecolors='black' if doe["sig"] else phase_info["color"],
                   linewidths=1.2 if doe["sig"] else 0.8,
                   zorder=10)

    # Annotate milestones
    if doe["milestone"]:
        # Small annotation for key milestones
        if doe["id"] == 8:
            ax_main.annotate('First\nsignificant',
                           xy=(x, y), xytext=(x-2, y+1.5),
                           fontsize=7, ha='center',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='yellow',
                                   alpha=0.7,
                                   edgecolor='black',
                                   linewidth=0.5),
                           arrowprops=dict(arrowstyle='->',
                                         connectionstyle='arc3,rad=0.3',
                                         lw=0.8))
        elif doe["id"] == 22:
            ax_main.annotate('L2 null\n(1st)',
                           xy=(x, y), xytext=(x+2, y+1.0),
                           fontsize=7, ha='center',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='yellow',
                                   alpha=0.7,
                                   edgecolor='black',
                                   linewidth=0.5),
                           arrowprops=dict(arrowstyle='->',
                                         connectionstyle='arc3,rad=-0.3',
                                         lw=0.8))
        elif doe["id"] == 26:
            ax_main.annotate('L2\nFALSIFIED',
                           xy=(x, y), xytext=(x-1, y+1.2),
                           fontsize=7, ha='center', weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='#FFD700',
                                   alpha=0.9,
                                   edgecolor='red',
                                   linewidth=1.0),
                           arrowprops=dict(arrowstyle='->',
                                         connectionstyle='arc3,rad=0.2',
                                         lw=1.0,
                                         color='red'))
        elif doe["id"] == 27:
            ax_main.annotate('Rate-time\ncompensation',
                           xy=(x, y), xytext=(x+1.5, y-1.8),
                           fontsize=7, ha='center',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='yellow',
                                   alpha=0.7,
                                   edgecolor='black',
                                   linewidth=0.5),
                           arrowprops=dict(arrowstyle='->',
                                         connectionstyle='arc3,rad=-0.3',
                                         lw=0.8))
        elif doe["id"] == 29:
            ax_main.annotate('Movement\nsole determinant',
                           xy=(x, y), xytext=(x, y-2.0),
                           fontsize=7, ha='center', weight='bold',
                           bbox=dict(boxstyle='round,pad=0.3',
                                   facecolor='#FFD700',
                                   alpha=0.9,
                                   edgecolor='darkgreen',
                                   linewidth=1.0),
                           arrowprops=dict(arrowstyle='->',
                                         lw=1.0,
                                         color='darkgreen'))

# Phase background rectangles
for phase_key, phase_info in phases.items():
    y = phase_info["y"]
    # Find x range for this phase
    phase_does = [d for d in does if d["phase"] == phase_key]
    if phase_does:
        x_min = min(d["id"] for d in phase_does) - 0.5
        x_max = max(d["id"] for d in phase_does) + 0.5

        # Background rectangle
        rect = FancyBboxPatch((x_min, y-0.4), x_max-x_min, 0.8,
                             boxstyle="round,pad=0.05",
                             facecolor=phase_info["color"],
                             alpha=0.15,
                             edgecolor='none',
                             zorder=1)
        ax_main.add_patch(rect)

# Y-axis labels (phase names)
y_labels = []
y_ticks = []
for phase_key in sorted(phases.keys(), key=lambda k: phases[k]["y"]):
    y_ticks.append(phases[phase_key]["y"])
    y_labels.append(phases[phase_key]["name"])

ax_main.set_yticks(y_ticks)
ax_main.set_yticklabels(y_labels, fontsize=7)
ax_main.set_ylim(-1, 9)
ax_main.set_xlim(0, 30)
ax_main.set_ylabel('Research Phase', fontsize=9, weight='bold')
ax_main.spines['top'].set_visible(False)
ax_main.spines['right'].set_visible(False)

# Legend
legend_elements = [
    plt.Line2D([0], [0], marker='o', color='w',
              markerfacecolor='gray', markeredgecolor='black',
              markersize=7, linewidth=0, label='Significant (p<0.05)'),
    plt.Line2D([0], [0], marker='o', color='w',
              markerfacecolor='lightgray', markeredgecolor='gray',
              markersize=6, linewidth=0, alpha=0.6, label='Null result'),
]
ax_main.legend(handles=legend_elements, loc='upper left', frameon=False, ncol=2)

# Cumulative episodes plot
cumul_episodes = np.cumsum([d["episodes"] for d in does])
doe_ids = [d["id"] for d in does]

ax_cumul.bar(doe_ids, [d["episodes"] for d in does],
            width=0.8,
            color=[phases[d["phase"]]["color"] for d in does],
            alpha=0.6,
            edgecolor='black',
            linewidth=0.5)

# Add cumulative line
ax_cumul.plot(doe_ids, cumul_episodes, 'k-', linewidth=1.5, label='Cumulative')
ax_cumul.scatter(doe_ids, cumul_episodes, c='black', s=15, zorder=10)

# Annotate final total
ax_cumul.annotate(f'Total: {cumul_episodes[-1]:,}',
                 xy=(29, cumul_episodes[-1]),
                 xytext=(26, cumul_episodes[-1] + 300),
                 fontsize=8, weight='bold',
                 arrowprops=dict(arrowstyle='->', lw=0.8))

ax_cumul.set_xlabel('DOE Number', fontsize=9, weight='bold')
ax_cumul.set_ylabel('Episodes', fontsize=8)
ax_cumul.set_ylim(0, max(cumul_episodes) * 1.15)
ax_cumul.spines['top'].set_visible(False)
ax_cumul.spines['right'].set_visible(False)
ax_cumul.grid(axis='y', alpha=0.3, linewidth=0.5)

# X-axis ticks
ax_cumul.set_xticks(range(0, 31, 5))

plt.tight_layout()

# Save outputs
pdf_path = output_dir / "figure2_doe_timeline.pdf"
png_path = output_dir / "figure2_doe_timeline.png"

plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

print(f"✓ Saved PDF: {pdf_path}")
print(f"✓ Saved PNG: {png_path}")
print(f"✓ Figure size: 7.0 x 4.5 inches (NeurIPS column width)")
print(f"✓ DPI: 300 (publication quality)")
print(f"✓ Total DOEs: {len(does)}")
print(f"✓ Total episodes: {cumul_episodes[-1]:,}")
print(f"✓ Significant results: {sum(1 for d in does if d['sig'])}")
print(f"✓ Key milestones annotated: {sum(1 for d in does if d['milestone'])}")

plt.close()

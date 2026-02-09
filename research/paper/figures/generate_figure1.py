#!/usr/bin/env python3
"""
Generate Figure 1: Agent Architecture Diagram for NeurIPS paper.

4-level hierarchical decision system with latency profiles.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

def main():
    # Create figure (7 inches wide x 3.5 inches tall)
    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Color scheme (green → orange → grey)
    colors = {
        'L0': '#2ecc71',  # Green (fastest)
        'L1': '#f39c12',  # Orange
        'L2': '#e67e22',  # Darker orange
        'L3': '#95a5a6',  # Grey (offline)
    }

    # Box dimensions
    box_width = 2.0
    box_height = 0.8
    x_start = 0.5
    y_spacing = 1.2

    # Level positions (top to bottom)
    levels = [
        {
            'name': 'L0: Hardcoded Rules',
            'tech': 'Rust, <1ms',
            'desc': 'Dodge when health < 20\nAttack nearest enemy\nDeterministic floor',
            'y': 4.5,
            'color': colors['L0'],
            'linestyle': '-',
        },
        {
            'name': 'L1: Episode Cache',
            'tech': 'DuckDB, <10ms',
            'desc': 'Per-agent play history (last 100 episodes)\nPeriodic action patterns\nOffline generation',
            'y': 3.0,
            'color': colors['L1'],
            'linestyle': '-',
        },
        {
            'name': 'L2: Strategy Retrieval',
            'tech': 'OpenSearch kNN, <100ms',
            'desc': 'Strategy document corpus\nk=5 nearest neighbors\nScore documents against game state\n[FALSIFIED - core thesis]',
            'y': 1.5,
            'color': colors['L2'],
            'linestyle': '-',
        },
        {
            'name': 'L3: Retrospection',
            'tech': 'Claude Code, offline (seconds)',
            'desc': 'Post-episode analysis\nStrategy document generation\nNever runs during gameplay',
            'y': 0.0,
            'color': colors['L3'],
            'linestyle': '--',
        },
    ]

    # Draw level boxes
    for level in levels:
        # Main box
        box = FancyBboxPatch(
            (x_start, level['y']),
            box_width, box_height,
            boxstyle="round,pad=0.05",
            edgecolor='black',
            facecolor=level['color'],
            linewidth=1.5 if level['linestyle'] == '-' else 1.0,
            linestyle=level['linestyle'],
            alpha=0.7,
        )
        ax.add_patch(box)

        # Level name (bold)
        ax.text(
            x_start + box_width / 2, level['y'] + box_height / 2,
            level['name'],
            fontsize=9,
            weight='bold',
            ha='center', va='center',
        )

    # Draw description boxes (to the right)
    desc_x = x_start + box_width + 0.3
    desc_width = 3.5
    desc_height = 0.8

    for level in levels:
        # Description box
        desc_box = FancyBboxPatch(
            (desc_x, level['y']),
            desc_width, desc_height,
            boxstyle="round,pad=0.05",
            edgecolor='gray',
            facecolor='white',
            linewidth=0.8,
            alpha=0.9,
        )
        ax.add_patch(desc_box)

        # Technology (bold, top)
        ax.text(
            desc_x + desc_width / 2, level['y'] + box_height - 0.15,
            level['tech'],
            fontsize=8,
            weight='bold',
            ha='center', va='top',
        )

        # Description (smaller, multi-line)
        ax.text(
            desc_x + 0.1, level['y'] + 0.4,
            level['desc'],
            fontsize=7,
            ha='left', va='center',
            linespacing=1.3,
        )

    # Draw flow arrows (decision flow from L0 → L1 → L2)
    arrow_x = x_start + box_width / 2
    for i in range(len(levels) - 2):  # L0 → L1 → L2 (not L3)
        y_from = levels[i]['y']
        y_to = levels[i + 1]['y'] + box_height

        arrow = FancyArrowPatch(
            (arrow_x, y_from),
            (arrow_x, y_to),
            arrowstyle='->,head_width=0.3,head_length=0.2',
            color='black',
            linewidth=1.5,
            mutation_scale=15,
        )
        ax.add_patch(arrow)

        # Label: "no decisive action" between levels
        ax.text(
            arrow_x + 0.15, (y_from + y_to) / 2,
            'no decisive\naction',
            fontsize=7,
            style='italic',
            ha='left', va='center',
        )

    # Draw separate arrow from L3 (offline) to L1 (feeds cache)
    l3_y = levels[3]['y'] + box_height / 2
    l1_y = levels[1]['y']

    # Curved arrow from L3 to L1 (right side)
    offline_arrow = FancyArrowPatch(
        (desc_x + desc_width, l3_y),
        (desc_x + desc_width, l1_y),
        arrowstyle='->,head_width=0.3,head_length=0.2',
        connectionstyle="arc3,rad=0.3",
        color='gray',
        linewidth=1.5,
        linestyle='--',
        mutation_scale=15,
    )
    ax.add_patch(offline_arrow)

    # Label for offline arrow
    ax.text(
        desc_x + desc_width + 0.3, (l3_y + l1_y) / 2,
        'offline\ngeneration',
        fontsize=7,
        style='italic',
        color='gray',
        ha='left', va='center',
    )

    # Draw "Game Environment" box on the left
    game_x = x_start - 0.2
    game_y = 2.5
    game_width = 0.15
    game_height = 2.5

    game_box = FancyBboxPatch(
        (game_x - game_width, game_y),
        game_width, game_height,
        boxstyle="round,pad=0.02",
        edgecolor='black',
        facecolor='lightblue',
        linewidth=1.2,
        alpha=0.8,
    )
    ax.add_patch(game_box)

    # Rotated text for "Game Environment"
    ax.text(
        game_x - game_width / 2, game_y + game_height / 2,
        'Game\nEnvironment\n(VizDoom)',
        fontsize=8,
        weight='bold',
        ha='center', va='center',
        rotation=90,
    )

    # Arrow from Game to L0
    game_arrow = FancyArrowPatch(
        (game_x, game_y + game_height / 2),
        (x_start, levels[0]['y'] + box_height / 2),
        arrowstyle='<->,head_width=0.3,head_length=0.2',
        color='black',
        linewidth=1.2,
        mutation_scale=15,
    )
    ax.add_patch(game_arrow)

    # Label for game arrow
    ax.text(
        (game_x + x_start) / 2, game_y + game_height / 2 + 0.3,
        'game state\n(28.6ms @ 35fps)',
        fontsize=7,
        ha='center', va='bottom',
    )

    # Add title
    fig.suptitle(
        'Figure 1: Four-Level Agent Architecture with Latency Profiles',
        fontsize=11,
        weight='bold',
        y=0.98,
    )

    # Add caption at bottom
    caption = (
        "Agent decision system with four levels. L0 (hardcoded rules) provides a deterministic floor with <1ms latency. "
        "L1 (episode cache) stores periodic action patterns generated offline. L2 (strategy retrieval) uses kNN search "
        "over a corpus of strategy documents. L3 (retrospection) runs offline after episodes to generate new strategies. "
        "The core thesis that L2 provides useful guidance was falsified by DOE-001~020 experiments."
    )
    ax.text(
        5.0, -0.5,
        caption,
        fontsize=7,
        ha='center', va='top',
        wrap=True,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.3, edgecolor='gray'),
    )

    # Add "FALSIFIED" marker on L2 box
    falsified_x = x_start + box_width + 0.05
    falsified_y = levels[2]['y'] + box_height / 2
    ax.text(
        falsified_x, falsified_y,
        '✗',
        fontsize=20,
        weight='bold',
        color='red',
        ha='left', va='center',
    )

    # Tight layout
    plt.tight_layout(rect=[0, 0.05, 1, 0.95])

    # Save as PDF and PNG
    pdf_path = '/Users/sangyi/workspace/research/clau-doom/research/paper/figures/figure1_architecture.pdf'
    png_path = '/Users/sangyi/workspace/research/clau-doom/research/paper/figures/figure1_architecture.png'

    plt.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.savefig(png_path, format='png', bbox_inches='tight', dpi=300)

    print(f"✓ Saved: {pdf_path}")
    print(f"✓ Saved: {png_path}")

    plt.close()

if __name__ == '__main__':
    main()

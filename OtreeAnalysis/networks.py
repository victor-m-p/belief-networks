import numpy as np 
import pandas as pd 
import os 
import json 
import networkx as nx 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

dir = 'data_clean'
files = os.listdir(dir)

def load_file(dir, f):
    with open(os.path.join(dir, f), 'r') as f: 
        loaded_dict = json.load(f)
    return loaded_dict 

# labels colors 
def color_nodes(G, node_types): 
    label_to_source = {entry['text']: entry['source'] for entry in node_types}
    source_to_color = {
        'ACCEPTED': 'tab:blue',
        'USER': 'tab:orange',
        'MODIFIED': 'tab:green',
    }
    node_colors = [
        source_to_color.get(label_to_source.get(label, 'USER'), 'tab:gray')
        for label in G.nodes()
    ]
    
    return node_colors, source_to_color

tst = {'ACCEPTED': 'tab:blue', 'USER': 'tab:orange', 'MODIFIED': 'tab:green'}
tst.get('ACCEPTED')

def plot_network(participant_id: str, node_dict: dict, edge_dict: dict, node_types=False, label_nodes=True):

    G = nx.Graph()

    # Add nodes with position and radius
    pos = {}
    radii = {}
    for node in node_dict:
        label = node['label']
        G.add_node(label)
        pos[label] = (node['x'], node['y'])
        radii[label] = node['radius']

    # Optionally add color
    if node_types:
        node_colors, source_to_color = color_nodes(G, node_types)
    else: 
        node_colors = 'tab:gray' 
        source_to_color = {}

    # Step 3: Add edges with polarity
    for edge in edge_dict:
        G.add_edge(edge['fromLabel'], edge['toLabel'], polarity=edge['polarity'])

    # Step 4: Prepare colors and sizes
    edge_colors = ['tab:red' if G[u][v]['polarity'] == 'positive' else 'tab:blue' for u, v in G.edges()]
    node_sizes = [radii[n] ** 2 for n in G.nodes()]  # area-based scaling

    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=2)

    # Manually draw labels with clip_on=False
    if label_nodes: 
        for label, (x, y) in pos.items():
            ax.annotate(
                label,
                (x, y),
                textcoords='offset points',
                xytext=(0, 0),
                ha='center',
                va='center',
                fontsize=12,
                clip_on=False  # <-- this allows text to go beyond axes
            )

    # Problems with clipping on x axis 
    x_vals, _ = zip(*pos.values())
    x_margin = (max(x_vals) - min(x_vals)) * 0.3
    ax.set_xlim(min(x_vals) - x_margin, max(x_vals) + x_margin)
    ax.axis('off')
    
    # Legend patches
    legend_handles = [
        mpatches.Patch(color=source_to_color.get('ACCEPTED'), label='Accepted'),
        mpatches.Patch(color=source_to_color.get('USER'), label='User'),
        mpatches.Patch(color=source_to_color.get('MODIFIED'), label='Modified'),
    ]

    # Place legend *outside* the axes, in fixed bottom right of figure
    fig.legend(
        handles=legend_handles,
        #loc='upper right',
        bbox_to_anchor=(0.98, 0.02), 
        borderaxespad=0.2,
        frameon=False,
        fontsize=12
    )
    
    # Let tight_layout reposition the figure canvas to include overhanging labels
    fig.tight_layout()

    # Save without cropping
    plt.savefig(f'fig/networks/{participant_id}.png', dpi=300, bbox_inches='tight')
    plt.close()

p_dicts = [load_file(dir, f) for f in files]
for dic in p_dicts: 
    id = dic['code']
    nodes = dic['pos_3']
    edges = dic['edges_3']
    node_types = dic['final_nodes']
    plot_network(id, nodes, edges, node_types, label_nodes=True)


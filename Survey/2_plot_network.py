import numpy as np 
import pandas as pd 
import networkx as nx 
import matplotlib.pyplot as plt 
from matplotlib.lines import Line2D
import os 

### testing ###
def filter_bidirectional_same_type(edges_df):
    # Create a set of tuples including relation_type
    edge_set = set(zip(edges_df['focal_node'], edges_df['other_node'], edges_df['direction']))

    # Check if reverse edge with SAME relation_type exists
    def is_bidirectional_same_type(row):
        return (row['other_node'], row['focal_node'], row['direction']) in edge_set

    # Mark edges meeting criteria
    edges_df['bidirectional_same_type'] = edges_df.apply(is_bidirectional_same_type, axis=1)

    # Keep only edges satisfying both conditions
    filtered_edges = edges_df[edges_df['bidirectional_same_type']].drop(columns=['bidirectional_same_type'])

    return filtered_edges

def create_network(dir, participant_id):
    node_file = f"nodes3_{participant_id}.csv"
    edge_file = f"couplings4_{participant_id}.csv"
    df_nodes = pd.read_csv(os.path.join(dir, node_file))
    df_edges = pd.read_csv(os.path.join(dir, edge_file))

    # fixes nodes and edges: 
    df_nodes['node'] = df_nodes['concept'] + ', ' + df_nodes['type']
    df_edges['focal_node'] = df_edges['focal_target'] + ', ' + df_edges['focal_target_type']
    df_edges['other_node'] = df_edges['other_target'] + ', ' + df_edges['other_target_type']

    # Quick fix; but actually fix
    df_edges['direction'] = df_edges['direction'].where(df_edges['direction'].isin(['POSITIVE', 'NEGATIVE']), 'OTHER')
    #df_edges = df_edges[df_edges['relation_type']=='EXPLICIT']
    #df_edges = filter_bidirectional_same_type(df_edges)
    #df_edges = df_edges[df_edges['relation_type']=='EXPLICIT']

    # Map importance to numerical sizes
    size_mapping = {'HIGH': 1500, 'MEDIUM': 800, 'LOW': 400}
    df_nodes['size'] = df_nodes['importance'].map(size_mapping)

    # Create an undirected graph
    G = nx.Graph()

    # Add nodes with attributes
    for _, row in df_nodes.iterrows():
        G.add_node(row['node'], size=row['size'], type=row['type'], label=row['concept'])

    # Add edges with attributes
    for _, row in df_edges.iterrows():
        G.add_edge(row['focal_node'], row['other_node'], direction=row['direction'])
    
    return G

def draw_belief_network(G, participant_id):

    # Define position layout
    pos = nx.spring_layout(G, iterations=50, seed=42)

    # Extract node sizes and labels from node attributes
    node_sizes = [G.nodes[node]['size'] for node in G.nodes]
    labels = {node: G.nodes[node]['label'] for node in G.nodes}

    # Node colors based on node type (assuming attribute 'type' as PERSONAL or SOCIAL)
    node_colors = ['tab:orange' if G.nodes[node]['type'] == 'PERSONAL' else 'tab:green' for node in G.nodes]

    # Edge colors based on edge attribute 'direction'
    edge_colors = ['tab:red' if G[u][v]['direction'] == 'POSITIVE' else 'tab:blue' for u, v in G.edges]

    # Start plotting
    plt.figure(figsize=(9, 6))

    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                        node_size=node_sizes,
                        node_color=node_colors,
                        alpha=0.9)

    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)

    # Draw labels using 'concept' attribute
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=11)

    # Define custom legend
    node_legend = [
        Line2D([0], [0], marker='o', color='w', label='Personal', markerfacecolor='tab:orange', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Social', markerfacecolor='tab:green', markersize=10)
    ]

    edge_legend = [
        Line2D([0], [0], color='tab:red', lw=2, label='Positive'),
        Line2D([0], [0], color='tab:blue', lw=2, label='Negative')
    ]

    # Position legend neatly in lower right corner
    plt.legend(handles=node_legend + edge_legend,
            loc='lower right', fontsize=12)

    # Clean layout
    plt.axis('off')
    plt.title(f"Concept Network ({participant_id})", fontsize=16)
    plt.tight_layout(pad=1.5)

    # Save figure without cutting off
    plt.savefig(f"fig/participant_networks/{participant_id}_all.png", bbox_inches='tight', dpi=300)
    plt.close();
    
# load  
dir = f'data/llama-3.3-70b-versatile-network'
participant_id = [16, 17, 18, 19, 22, 26, 27]
for p_id in participant_id: 
    G = create_network(dir, p_id)
    draw_belief_network(G, p_id)


'''
Notes: 
1. There is some variation; do everyone twice. Maybe we can use this for something?
2. We get MANY more couplings when we do it iteratively: also fewer mistakes.

Wait, who is who? 
16: Peter
17: Victor
18: Josh 
19: Daniele
22: Miruna 
26: Lasmi
27: Mirta? 
'''

import numpy as np 
import pandas as pd 
import networkx as nx 
import matplotlib.pyplot as plt 
from matplotlib.lines import Line2D

# load  
data_path = 'data/gpt_codings_new'
participant_id = 16
df_nodes = pd.read_csv(f'{data_path}/nodes2_{participant_id}.csv')
df_edges = pd.read_csv(f'{data_path}/couplings2_{participant_id}.csv')

# fixes nodes and edges: 
df_nodes['node'] = df_nodes['concept'] + ', ' + df_nodes['type']
df_edges['focal_node'] = df_edges['focal_target'] + ', ' + df_edges['focal_target_type']
df_edges['other_node'] = df_edges['other_target'] + ', ' + df_edges['other_target_type']

# Quick fix; but actually fix
df_edges['direction'] = df_edges['direction'].where(df_edges['direction'].isin(['POSITIVE', 'NEGATIVE']), 'OTHER')

# Map importance to numerical sizes
size_mapping = {'HIGH': 1500, 'MEDIUM': 800, 'LOW': 400}
df_nodes['size'] = df_nodes['importance'].map(size_mapping)

# Create an undirected graph
G = nx.Graph()

# Add nodes with attributes
for _, row in df_nodes.iterrows():
    G.add_node(row['node'], size=row['size'], type=row['type'])

# Add edges with attributes
for _, row in df_edges.iterrows():
    G.add_edge(row['focal_node'], row['other_node'], direction=row['direction'])

# Generate layout
pos = nx.spring_layout(G, seed=42)

# Node colors mapping
node_color_map = {'PERSONAL': 'tab:orange', 'SOCIAL': 'tab:green'}
node_colors = [node_color_map[G.nodes[node]['type']] for node in G.nodes]

# Edge colors mapping
edge_color_map = {'POSITIVE': 'tab:red', 'NEGATIVE': 'tab:blue', 'OTHER': 'tab:gray'}
edge_colors = [edge_color_map[G[u][v]['direction']] for u, v in G.edges]

# Draw nodes
nx.draw_networkx_nodes(G, pos,
                       node_size=[G.nodes[node]['size'] for node in G.nodes],
                       node_color=node_colors,
                       alpha=0.9)

# Draw edges
nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=2)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=10)

# Custom legends
node_legend = [Line2D([0], [0], marker='o', color='w', label='Personal',
                      markerfacecolor='tab:orange', markersize=10),
               Line2D([0], [0], marker='o', color='w', label='Social',
                      markerfacecolor='tab:green', markersize=10)]

edge_legend = [Line2D([0], [0], color='tab:red', lw=2, label='Positive'),
               Line2D([0], [0], color='tab:blue', lw=2, label='Negative')]

# Add legends to the plot
plt.legend(handles=node_legend + edge_legend,
           loc='upper right', bbox_to_anchor=(1.15, 1))

# Clean up the plot
plt.axis('off')
plt.title("Concept Network", fontsize=14)
plt.tight_layout()
plt.show()

'''
Notes: 
1. There is some variation; do everyone twice. Maybe we can use this for something?
2. We get MANY more couplings when we do it iteratively: also fewer mistakes.
'''

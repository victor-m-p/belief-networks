import numpy as np
import pandas as pd 
import os 
import json 

# setup 
path = 'llm_codings'
participant_id = 16
nodes_edges_path = os.path.join(path, 'nodes_edges', f"{participant_id}.json")
edges_path = os.path.join(path, 'edges', f"{participant_id}.json")

# loads 
with open(nodes_edges_path, 'r') as f: 
    nodes_edges = json.load(f)

with open(edges_path, 'r') as f: 
    reason_links = json.load(f)

nodes_edges = nodes_edges['results']
reason_links = reason_links['results']

pd.set_option('display.max_colwidth', None)

# wrangling
focal_node = 'meat eating'
nodes = pd.DataFrame(nodes_edges)

edges = nodes 
edges = edges.rename(columns={'stance': 'x'})
edges['y'] = focal_node

# links between concepts 
links = pd.DataFrame(reason_links)
links = links.rename(columns={
    'stance_1': 'x',
    'stance_2': 'y'
})

mapping = {
    'POSITIVE': 'FAVOR',
    'NEGATIVE': 'AGAINST'
}
links['direction'] = links['direction'].map(mapping)

# concat them 
links = links[['x', 'y', 'direction']]
edges = edges[['x', 'y', 'direction']]
edges_df = pd.concat([links, edges])

# add focal node (fix this)
new_node = pd.DataFrame([{
    'stance': focal_node,
    'importance': "MEDIUM",
    'direction': "AGAINST"
}])

# Add it to the original
nodes_df = pd.concat([nodes, new_node], ignore_index=True)

# Quick strip 
strip_string = "I agree with the following: "
nodes_df['stance'] = nodes_df['stance'].str.replace(
    strip_string, "", regex=False)
edges_df['x'] = edges_df['x'].str.replace(
    strip_string, "", regex=False)
edges_df['y'] = edges_df['y'].str.replace(
    strip_string, "", regex=False)

# add focal node to nodes
# Create an undirected graph
import networkx as nx 
import matplotlib.pyplot as plt 

G = nx.Graph()

# Add nodes with attributes
for _, row in nodes_df.iterrows():
    G.add_node(row['stance'], 
               importance=row['importance'], 
               direction=row['direction'])

# Add edges with direction (only if both nodes are in G)
for _, row in edges_df.iterrows():
    if row['x'] in G.nodes and row['y'] in G.nodes:
        G.add_edge(row['x'], row['y'], direction=row['direction'])

# ---- Map node sizes based on importance ----
size_map = {'LOW': 100, 'MEDIUM': 500, 'HIGH': 1500}
node_sizes = [size_map[G.nodes[n]['importance']] for n in G.nodes]

# ---- Map node colors based on direction ----
color_map = {'FAVOR': 'green', 'AGAINST': 'red'}
node_colors = [color_map[G.nodes[n]['direction']] for n in G.nodes]

# ---- Edge color based on edge direction ----
edge_colors = [color_map[G[u][v]['direction']] for u, v in G.edges]

# ---- Draw graph ----
pos = nx.spring_layout(G, seed=42)

nx.draw(G, pos,
        with_labels=True,
        node_size=node_sizes,
        node_color=node_colors,
        edge_color=edge_colors,
        font_size=8,
        font_color='black',
        linewidths=1,
        width=1.5)

plt.margins(0.2)
plt.tight_layout()
plt.show()
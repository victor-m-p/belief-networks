import numpy as np 
import pandas as pd 
import networkx as nx 
import json

# load nodes 
with open('data/nodes.json') as f:
        nodes = json.loads(f.read())

# load edges
df_edges = pd.read_csv('data/edges.csv')

# quick plot # 
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

G_personal = nx.Graph()

# Add only personal-belief nodes to G_personal
for node_id, data in nodes.items():
    if data.get("type") == "belief":
        G_personal.add_node(node_id, **data)
G_personal.nodes(data=True)

# Add edges only if both ends are personal-belief nodes
for e in df_edges.to_dict(orient="records"):
    src = e["source"]
    tgt = e["target"]
    if src in G_personal and tgt in G_personal:
        G_personal.add_edge(src, tgt, **e)
    
pos_personal = nx.spring_layout(G_personal, seed=4)

### try to plot social ###
G_master = nx.Graph()

for node_id, data in nodes.items():
    G_master.add_node(node_id, **data)

for e in df_edges.to_dict(orient='records'):
    src = e["source"]
    tgt = e["target"]
    G_master.add_edge(src, tgt, **e)

for node_id, attr in G_master.nodes(data=True):
    if attr.get("type") == "social_belief":
        # Check all neighbors
        neighbors = list(G_master[node_id])

        personal_neighbors = [
            nb for nb in neighbors
            if G_master.nodes[nb].get("type") == "belief"
        ]

pos_personal = nx.spring_layout(G_personal, seed=4)

pos_master = {}

# 1) Copy personal node positions
for node_id, attr in G_personal.nodes(data=True):
    pos_master[node_id] = pos_personal[node_id]

# 2) Place social nodes around their personal node
import math

r = 0.2  # small radius for the social nodes

for node_id, attr in G_master.nodes(data=True):
    if attr.get("type") == "social_belief":
        # Find personal neighbor
        personal_neighbors = [
            nb for nb in G_master[node_id]
            if G_master.nodes[nb].get("type") == "belief"
        ]
        if len(personal_neighbors) == 1:
            personal_node = personal_neighbors[0]
            px, py = pos_master[personal_node]

            # Just place the social node at some offset angle
            # For example, we could just do a random angle or 
            # place them all at the same offset if you only have 1 neighbor
            angle = 2 * math.pi * 0.25  # 90 degrees, or do random, etc.
            offset_x = r * math.cos(angle)
            offset_y = r * math.sin(angle)

            pos_master[node_id] = (px + offset_x, py + offset_y)
        else:
            # If there's no (or more than one) personal neighbor, handle it
            pos_master[node_id] = (0, 0)  # fallback or skip

# For each personal node, gather social neighbors, then place them in a circle
for p_node, p_attr in G_master.nodes(data=True):
    if p_attr.get("type") == "belief":
        # find social neighbors
        social_neighbors = [
            nb for nb in G_master[p_node]
            if G_master.nodes[nb].get("type") == "social_belief"
        ]
        if not social_neighbors:
            continue
        
        px, py = pos_master[p_node]
        
        n = len(social_neighbors)
        for i, s_node in enumerate(social_neighbors):
            angle = 2 * math.pi * i / n
            offset_x = r * math.cos(angle)
            offset_y = r * math.sin(angle)
            pos_master[s_node] = (px + offset_x, py + offset_y)

direction_color_map = {
    'pro': "tab:red",
    'con': "tab:blue",
}

node_colors = []
node_sizes = []

for node_id, attr in G_master.nodes(data=True):
    # --- Color by level ---
    direction = attr.get("direction", -1)  
    # Default to "gray" if for some reason 'level' is missing
    node_color = direction_color_map.get(direction, "tab:gray")
    node_colors.append(node_color)
    
    # --- Size by abs_importance ---
    # abs_importance might be stored as a string, so let's handle that:
    abs_importance = attr.get("abs_importance", 10) # 10 default if missing
    
    # Choose a scaling factor to make the node sizes visible
    # e.g. 300 base + 100 * abs_importance_val
    node_size = 10 * abs_importance
    node_sizes.append(node_size)

plt.figure(figsize=(10, 8))
nx.draw_networkx(
    G_master,
    pos=pos_master,
    with_labels=True,
    node_color=node_colors,
    node_size=node_sizes,
    font_size=8
)
legend_elems = [
    #Patch(facecolor="tab:gray", label="Focal Belief"),
    Patch(facecolor="tab:red", label="For consuming animal products"),
    Patch(facecolor="tab:blue", label="Against consuming animal products"),
]
plt.legend(
    handles=legend_elems, 
    #loc="upper left", 
    bbox_to_anchor=(0.5, 1.1)  # Move legend just outside the axes
)
plt.axis("off")
plt.show()
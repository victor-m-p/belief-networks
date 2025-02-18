import numpy as np 
import pandas as pd 
import networkx as nx 
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# participant id 
participant_id = 17

# load nodes 
with open(f'data/personal_nodes_{participant_id}.json') as f:
        personal_nodes = json.loads(f.read())

### fix edges ###
personal_edges = pd.read_csv(f'data/personal_edges_{participant_id}.csv')

# first drop neutral edges
personal_edges = personal_edges[personal_edges['direction'] != 'neut']

# first fix the inner layer
p_edges_focal = personal_edges[personal_edges['target'] == 'focal']
p_edges_focal['coupling_direction'] = p_edges_focal['coupling'] * p_edges_focal['direction'].apply(lambda x: 1 if x == 'pro' else -1)
p_edges_focal['coupling_scaled'] = p_edges_focal['coupling_direction'] * 0.01

# now fix outer layer 
def likert_conversion(n): 
    scale_dict = {}
    for i in range(1, n+1):
        val = -1 + 2 * (i - 1) / (n - 1) if n > 1 else 0
        scale_dict[i] = val
    return scale_dict
likert_scale_7 = likert_conversion(7)

p_edges_secondary = personal_edges[personal_edges['target'] != 'focal']
p_edges_secondary['coupling_scaled'] = p_edges_secondary['coupling'].map(likert_scale_7)

# basically our sanity check here # 
# this should be 1 or very close to 1. 
p_edges_secondary[p_edges_secondary['source'] == p_edges_secondary['target']]['coupling_scaled'].mean()

# okay now collect the edges
p_edges_secondary = p_edges_secondary[['source', 'target', 'coupling_scaled']]
p_edges_focal = p_edges_focal[['source', 'target', 'coupling_scaled']]
p_edges = pd.concat([p_edges_secondary, p_edges_focal])

# threshold edges ? # 
# ...

# remove self-loops
p_edges = p_edges[p_edges['source'] != p_edges['target']]

# initialize graph from edgeslist
G = nx.from_pandas_edgelist(
    p_edges, 
    'source', 
    'target', 
    edge_attr=True,
    create_using=nx.DiGraph()
)

# add node information 
for node_id, data in personal_nodes.items():
    G.add_node(node_id, **data)

# collect node information
node_size = nx.get_node_attributes(G, 'abs_importance')
node_color = nx.get_node_attributes(G, 'direction_num')
pos = nx.spring_layout(G, seed=4, weight='coupling_scaled')

# collect edge information
edge_coupling = nx.get_edge_attributes(G, 'coupling_scaled')

nx.draw_networkx_nodes(
    G, 
    pos, 
    node_size=[x*10 for x in node_size.values()],
    vmin=-1,
    vmax=1,
    cmap=plt.cm.coolwarm,
    node_color=node_color.values(),
)
nx.draw_networkx_labels(G, pos, font_size=8)
nx.draw_networkx_edges(
    G,
    pos,
    edge_color=edge_coupling.values(),
    edge_cmap=plt.cm.coolwarm,
    edge_vmin=-1,
    edge_vmax=1,
    arrowstyle='->',
    arrowsize=12   
)
plt.axis("off")
plt.show();

# curate social # 
with open(f'data/social_nodes_{participant_id}.json') as f:
        social_nodes = json.loads(f.read())

### fix edges ###
social_edges = pd.read_csv(f'data/social_edges_{participant_id}.csv')

# ahh this might not completely work # 
# actually cannot really remove null edges here
# because they are really the ones with pressure
# like if you said something is an important reason for
# and they thing it is not a reason at all... 
social_edges['coupling_scaled'] = social_edges['coupling'].map(likert_scale_7)
s_edges = social_edges[['source', 'target', 'coupling_scaled']]

# collect combined edges 
all_edges = pd.concat([p_edges, s_edges])

# collect combined nodes 
df_p_nodes = pd.DataFrame(personal_nodes)
df_p_nodes


### try to plot social ###
G_combined = nx.from_pandas_edgelist(
    all_edges, 
    'source', 
    'target', 
    edge_attr=True,
    create_using=nx.DiGraph()
)



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
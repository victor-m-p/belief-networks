import numpy as np 
import pandas as pd 
import networkx as nx 
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# participant id 
participant_id = 16

# load nodes 
with open(f'data/personal_nodes_{participant_id}.json') as f:
        personal_nodes = json.loads(f.read())

### fix edges ###
personal_edges = pd.read_csv(f'data/personal_edges_{participant_id}.csv')

# first drop neutral edges
personal_edges = personal_edges[personal_edges['direction'] != 'neut']

# first fix the inner layer
p_edges_focal = personal_edges[personal_edges['target'] == 'b_focal']
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

p_edges_secondary = personal_edges[personal_edges['target'] != 'b_focal']
p_edges_secondary['coupling_scaled'] = p_edges_secondary['coupling'].map(likert_scale_7)

# basically our sanity check here # 
# this should be 1 or very close to 1. 
p_edges_secondary[p_edges_secondary['source'] == p_edges_secondary['target']]['coupling_scaled'].mean()

# okay now collect the edges
p_edges_secondary = p_edges_secondary[['source', 'target', 'coupling_scaled', 'type']]
p_edges_focal = p_edges_focal[['source', 'target', 'coupling_scaled', 'type']]
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
node_size = nx.get_node_attributes(G, 'importance')
node_color = nx.get_node_attributes(G, 'value_num')
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

legend_elems = [
    #Patch(facecolor="tab:gray", label="Focal Belief"),
    Patch(facecolor="tab:red", label="For meat consumption"),
    Patch(facecolor="tab:blue", label="Against meat consumption"),
]
plt.legend(
    handles=legend_elems, 
    #loc="upper left", 
    bbox_to_anchor=(0.5, 1.1)  # Move legend just outside the axes
)
plt.axis("off")
plt.tight_layout()
plt.savefig(f"fig/personal_{participant_id}_directed.png")

#### plot social network ####

# curate social # 
with open(f'data/social_nodes_{participant_id}.json') as f:
        social_nodes = json.loads(f.read())

### fix edges ###
social_edges = pd.read_csv(f'data/social_edges_{participant_id}.csv')
social_edges['coupling_scaled'] = social_edges['coupling'] * 0.01
s_edges = social_edges[['source', 'target', 'coupling_scaled', 'type']]

# collect combined edges 
all_edges = pd.concat([p_edges, s_edges])

### try to plot social ###
G_combined = nx.from_pandas_edgelist(
    all_edges, 
    'source', 
    'target', 
    edge_attr=True,
    create_using=nx.DiGraph()
)

# add node data
for node_id, data in personal_nodes.items(): 
    G_combined.add_node(node_id, **data)
for node_id, data in social_nodes.items(): 
    G_combined.add_node(node_id, **data)

# 1) Copy personal node positions
pos_combined = {}
for node_id, attr in G.nodes(data=True):
    pos_combined[node_id] = pos[node_id]

# 2) Place social nodes around their personal node
import math

r = 0.25  # small radius for the social nodes
quick_maths = {
    '0': 0.25,
    '1': 0.20,
    '2': 0.15
}

for node_id, attr in G_combined.nodes(data=True):
    if attr.get("type") == "social_belief":
        # find personal neighbor
        personal_neighbor = social_edges[social_edges['source']==node_id]['target'].values[0]
        px, py = pos_combined[personal_neighbor]

        # social_num
        num_social = node_id.split("_")[1]
        
        # Just place the social node at some offset angle
        # For example, we could just do a random angle or 
        # place them all at the same offset if you only have 1 neighbor
        angle = 2 * math.pi * quick_maths[num_social]  # 90 degrees, or do random, etc.
        offset_x = r * math.cos(angle)
        offset_y = r * math.sin(angle)

        pos_combined[node_id] = (px + offset_x, py + offset_y)

# get node attributes
node_size = nx.get_node_attributes(G_combined, 'importance')

# modify node size by factor 3 for social
node_size = {
    x: (y * 0.33 if "s_" in x else y)
    for x, y in node_size.items()
}

node_color = nx.get_node_attributes(G_combined, 'value_num')

# get edge attributes
G_combined.edges(data=True)

edge_color = nx.get_edge_attributes(G_combined, 'coupling_scaled')

nx.draw_networkx_nodes(
    G_combined, 
    pos_combined, 
    node_size=[x*5 for x in node_size.values()],
    vmin=-1,
    vmax=1,
    cmap=plt.cm.coolwarm,
    node_color=node_color.values(),
)
nx.draw_networkx_labels(G_combined, pos_combined, font_size=8)
nx.draw_networkx_edges(
    G_combined,
    pos_combined,
    edge_color=edge_color.values(),
    edge_cmap=plt.cm.coolwarm,
    edge_vmin=-1,
    edge_vmax=1,
    arrowstyle='->',
    arrowsize=12   
)

legend_elems = [
    #Patch(facecolor="tab:gray", label="Focal Belief"),
    Patch(facecolor="tab:red", label="For meat consumption"),
    Patch(facecolor="tab:blue", label="Against meat consumption"),
]
plt.legend(
    handles=legend_elems, 
    #loc="upper left", 
    bbox_to_anchor=(0.5, 1.1)  # Move legend just outside the axes
)
plt.axis("off")
plt.tight_layout()
plt.savefig(f'fig/complete_{participant_id}_directed.png')
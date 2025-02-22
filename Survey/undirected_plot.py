import numpy as np 
import pandas as pd 
import networkx as nx 
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import math 

type = 'gpt'
participant_id = 27

with open(f'data/gpt_clean/metadict_{participant_id}.json', 'r') as f:
    metadict = json.load(f)

### fix edges ###
personal_edges = metadict['personal_edges']
personal_edges = pd.DataFrame(personal_edges)

# first drop neutral edges
personal_edges = personal_edges[personal_edges['direction'] != 'neut']

# remove self-loops
p_edges = personal_edges[personal_edges['source'] != personal_edges['target']]

# make it undirected 
p_edges_agg = (
    p_edges
    .groupby(['source', 'target'], as_index=False)
    .agg({'coupling_scaled': 'mean'})
)

# initialize graph from edgeslist
G = nx.from_pandas_edgelist(
    p_edges_agg, 
    'source', 
    'target', 
    edge_attr=True,
    create_using=nx.Graph()
)

# add node information 
personal_nodes = metadict['personal_nodes']
for node_id, data in personal_nodes.items():
    G.add_node(node_id, **data)

# collect node information
node_size = nx.get_node_attributes(G, 'importance')
node_color = nx.get_node_attributes(G, 'value_num')
pos = nx.spring_layout(G, seed=4, weight='coupling_scaled', k=1)

#### plot social network ####
social_nodes = metadict['social_nodes']
social_edges = metadict['social_edges']
social_edges = pd.DataFrame(social_edges)
p_edges_agg['type'] = 'personal'
p_edges_agg = p_edges_agg[['source', 'target', 'coupling_scaled', 'type']]
s_edges = social_edges[['source', 'target', 'coupling_scaled', 'type']]

# collect combined edges 
all_edges = pd.concat([p_edges_agg, s_edges])

### try to plot social ###
G_combined = nx.from_pandas_edgelist(
    all_edges, 
    'source', 
    'target', 
    edge_attr=True,
    create_using=nx.Graph()
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

r = 0.25  # small radius for the social nodes
quick_maths = {
    '0': 0.25,
    '1': 0.20,
    '2': 0.15
}

for node_id, attr in G_combined.nodes(data=True):
    if attr.get("type") == "social_belief":
        print(node_id)
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
# ahh here it goes wrong I think
edge_color = nx.get_edge_attributes(G_combined, 'coupling_scaled')
edge_coupling = nx.get_edge_attributes(G_combined, 'coupling_scaled')

fig, ax = plt.subplots(figsize=(5, 4))

nx.draw_networkx_nodes(
    G_combined, 
    pos_combined, 
    node_size=[x*6 for x in node_size.values()],
    vmin=-1,
    vmax=1,
    cmap=plt.cm.coolwarm,
    node_color=node_color.values(),
    edgecolors='black',
)
nx.draw_networkx_labels(G_combined, pos_combined, font_size=8)
nx.draw_networkx_edges(
    G_combined,
    pos_combined,
    edge_color=edge_color.values(),
    edge_cmap=plt.cm.coolwarm,
    edge_vmin=-1,
    edge_vmax=1,
    width=[abs(x)*3 for x in edge_coupling.values()],
)

legend_elems = [
    #Patch(facecolor="tab:gray", label="Focal Belief"),
    Patch(facecolor="tab:red", label="For meat consumption"),
    Patch(facecolor="tab:blue", label="Against meat consumption"),
]
plt.legend(
    handles=legend_elems, 
    bbox_to_anchor=(0.5, 1.1)  # Move legend just outside the axes
)
plt.axis("off")
plt.tight_layout()
plt.savefig(f'fig/net_sym_{type}_{participant_id}.png')

# function down here to actually plot them # 

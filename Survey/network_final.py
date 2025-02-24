import numpy as np 
import pandas as pd 
import networkx as nx 
import json
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import math 

# get labels 
def get_labels(G):
    labels = {}
    for node_id in G.nodes():
        if node_id == "b_focal":
            labels[node_id] = "B"
        elif "b_" in node_id:
            b_num = node_id.split("_")[1]
            b_num = int(b_num)
            if b_num >= 5: 
                labels[node_id] = "C"
            else: 
                labels[node_id] = "P"
        elif "s_" in node_id:
            labels[node_id] = "S"
    return labels 

# combined position
def combined_position(pos, G, G_combined, social_edges):

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
    
    return pos_combined
    
def aggregate_edges(metadict):

    # extract edges 
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
    
    return p_edges_agg

participant_id = 17
type = 'human'
with open(f"data/human_clean/metadict_{participant_id}.json", "r") as f:
    metadict = json.load(f)

def get_params(metadict, pos=None):

    p_edges_agg = aggregate_edges(metadict)

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

    # get position
    if pos is None: 
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

    pos_combined = combined_position(
        pos, 
        G, 
        G_combined, 
        social_edges
    )

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

    # labels
    labels = get_labels(G_combined)

    return G_combined, pos_combined, node_size, node_color, edge_color, edge_coupling, labels

def draw_network(
    G, 
    pos, 
    node_size,
    node_color,
    edge_color,
    edge_coupling,
    labels,
    ax_num,
    subplot_text=None):

    nx.draw_networkx_nodes(
        G, 
        pos, 
        node_size=[x*6 for x in node_size.values()],
        vmin=-1,
        vmax=1,
        cmap=plt.cm.coolwarm,
        node_color=node_color.values(),
        edgecolors='black',
        ax=ax[ax_num]
    )
    nx.draw_networkx_labels(
        G, 
        pos, 
        labels=labels,
        font_size=8,
        ax=ax[ax_num])
    nx.draw_networkx_edges(
        G,
        pos,
        edge_color=edge_color.values(),
        edge_cmap=plt.cm.coolwarm,
        edge_vmin=-1,
        edge_vmax=1,
        width=[abs(x)*3 for x in edge_coupling.values()],
        ax=ax[ax_num]
    )
    if subplot_text:
        ax[ax_num].text(
            0.05, 
            0.95, 
            subplot_text,
            transform=ax[ax_num].transAxes, 
            fontsize=15, 
            va='top', 
            ha='left'
        )

participant_ids = [16, 18, 26]
participant_type = ['human', 'gpt']

param_dict = {}
for participant_id in participant_ids: 
    for type in participant_type: 
        if type == 'human': 
            print('human', participant_id)
            with open(f"data/human_clean/metadict_{participant_id}.json", "r") as f:
                metadict = json.load(f)
            G, pos, node_size, node_color, edge_color, edge_coupling, labels = get_params(metadict)
            param_dict[f"{participant_id}_{type}"] = {
                "G": G,
                "pos": pos,
                "node_size": node_size,
                "node_color": node_color,
                "edge_color": edge_color,
                "edge_coupling": edge_coupling,
                "labels": labels
            }
        else: 
            print('gpt', participant_id)
            with open(f"data/gpt_clean/metadict_{participant_id}.json", "r") as f:
                metadict = json.load(f)
            pos = param_dict[f"{participant_id}_human"]['pos']
            G, pos, node_size, node_color, edge_color, edge_coupling, labels = get_params(metadict, pos=pos)
            param_dict[f"{participant_id}_{type}"] = {
                "G": G,
                "pos": pos,
                "node_size": node_size,
                "node_color": node_color,
                "edge_color": edge_color,
                "edge_coupling": edge_coupling,
                "labels": labels
            }

fig, ax = plt.subplots(3, 2, figsize=(8, 12))
ax = ax.flatten()
num = 0
for participant_id in participant_ids: 
    for type in participant_type: 
        # extract params
        key = f"{participant_id}_{type}"
        G_combined = param_dict[key]['G']
        pos_combined = param_dict[key]['pos']
        node_size = param_dict[key]['node_size']
        node_color = param_dict[key]['node_color']
        edge_color = param_dict[key]['edge_color']
        edge_coupling = param_dict[key]['edge_coupling']
        labels = param_dict[key]['labels']
        
        # extract text 
        if type=='human': 
            text_type = 'Human'
        else:
            text_type = '+ LLM'
        
        draw_network(
            G_combined,
            pos_combined,
            node_size,
            node_color,
            edge_color,
            edge_coupling,
            labels,
            num,
            subplot_text=f"{text_type} (ID: {participant_id})"
        )
        num += 1

plt.tight_layout()
plt.savefig("fig/paper/network_plot.pdf", bbox_inches='tight')
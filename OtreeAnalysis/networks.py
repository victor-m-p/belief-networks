import pandas as pd 
import numpy as np 
import json 

import networkx as nx 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
import math 

# meta variables
session = '2025-06-24'

# load data
with open(f'data_clean/prolific/data_{session}.json', 'r') as f:
    data = json.load(f)

# participant keys 
keys = [key for key, _ in data.items()]

# do for one participant at a time 
idx = 1
key = keys[idx]
p = data[keys[idx]] # first participant
final_nodes = p['nodes']['final']
generated_nodes = p['nodes']['generated']

#### MAIN NETWORK #### 
text_mapping = {node['text']: node['belief'] for node in final_nodes}
text_mapping['Meat Eating'] = 'Meat Eating'
type_mapping = {node['stance']: [node['type'], node['category']] for node in generated_nodes}
type_mapping['Meat Eating'] = ['PERSONAL', 'BEHAVIOR']

def category_to_color(node_type, node_category):
    if node_type == 'PERSONAL' and node_category == 'MOTIVATION':
        return 'tab:blue'
    elif node_type == 'PERSONAL' and node_category == 'BEHAVIOR':
        return 'tab:grey'
    elif node_type == 'SOCIAL' and node_category == 'MOTIVATION':
        return 'tab:orange'
    else: 
        return 'tab:green'

def get_colors(node_text):
    node_text_clean = text_mapping.get(node_text)
    node_type, node_category = type_mapping.get(node_text_clean)
    return category_to_color(node_type, node_category)

def plot_network(node_dict, edge_dict, savefig=False, centering=False):

    G = nx.Graph()
    pos = {}
    radii = {}

    for node in node_dict: 
        label = node['label']
        G.add_node(label)
        pos[label] = (node['x'], node['y'])
        radii[label] = node['radius']

    # test flipping y
    max_y = max(y for _, y in pos.values())
    pos = {label: (x, max_y - y) for label, (x, y) in pos.items()}

    for edge in edge_dict: 
        G.add_edge(edge['from'], edge['to'], polarity=edge['polarity'], size=edge['strength'])

    # node and edge properties / visuals 
    edge_colors = ['tab:green' if G[u][v]['polarity'] == 'positive' else 'tab:red' for u, v in G.edges()]
    edge_size = [G[u][v]['size']/10 for u, v in G.edges()]
    node_sizes = [radii[n] ** 2 for n in G.nodes()] 
    node_colors = [get_colors(n) for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.axis('off')
    
    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_size)

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

    # centering the "Meat Eating" node
    if centering: 
        center_x, center_y = pos['Meat Eating']
        all_x = [x for x, y in pos.values()]
        all_y = [y for x, y in pos.values()]
        x_margin = max(abs(x-center_x) for x in all_x)
        y_margin = max(abs(y-center_y) for y in all_y)
        margin = max(x_margin, y_margin) * 1.1 # 10% padding
        ax.set_xlim(center_x - margin, center_x + margin)
        ax.set_ylim(center_y - margin, center_y + margin)

    if savefig: 
        plt.savefig(savefig, dpi=300)
    else: 
        plt.show();
    plt.close()
    
# ahhh this looks fucked with the central node
# did they actually just place it right on top of it?
node_dict = p['positions']['pos_5']
edge_dict = p['edges']['edges_5']
plot_network(
    node_dict = node_dict, 
    edge_dict = edge_dict,
    savefig = f'fig/networks_{session}/{key}_main.png'
    )

#### Look at correlation between node importance vs. node size #### 
def plot_ratings(node_dict, node_importance, savefig=False):

    x_vals = []
    y_vals = []
    labels = []

    for node in node_dict:
        label = node['label']
        if label in node_importance:
            x_vals.append(node['radius'])
            y_vals.append(node_importance[label])
            labels.append(label)

    # Plot
    plt.figure(figsize=(6, 6))
    plt.scatter(x_vals, y_vals)

    # Annotate points
    for x, y, label in zip(x_vals, y_vals, labels):
        plt.annotate(label, (x, y), textcoords='offset points', xytext=(5, 5))

    plt.xlabel('Radius')
    plt.ylabel('Explicit Rating')
    plt.title('Radius vs Explicit Rating')
    plt.grid(True)
    plt.tight_layout()
    
    if savefig: 
        plt.savefig(savefig, dpi=300)
    else: 
        plt.show()
    plt.close()

node_importance = p['node_importance']

plot_ratings(
    node_dict = node_dict,
    node_importance = node_importance,
    savefig = f'fig/validation/test.png'
)

# plot correlation


#### DISTANCE FROM CENTRAL (how much influence) #### 
def plot_closeness(node_dict, main_label='Meat Eating', savefig=None):

    # Find "Meat Eating" coordinates
    me_x, me_y = next((node['x'], node['y']) for node in node_dict if node['label'] == main_label)

    # Compute distances
    data = []
    for node in node_dict:
        node_label = node['label']
        if node_label != main_label:
            dx = node['x'] - me_x
            dy = node['y'] - me_y
            dist = math.hypot(dx, dy)
            color = get_colors(node_label)
            data.append((node_label, dist, color))

    # Sort
    data.sort(key=lambda x: x[1])
    
    labels = [label for label, _, _ in data]
    values = [dist for _, dist, _ in data]
    colors = [color for _, _, color in data]
    
    # Custom y positions with big spacing
    spacing = 1.5
    y_pos = [i * spacing for i in range(len(labels))]

    # Make a bigger figure to accommodate spacing
    plt.figure(figsize=(6, len(labels) * spacing * 0.5))  # Scale figure height

    # Plot bars
    plt.barh(y_pos, values, height=1.0, color=colors)

    # Set y-ticks
    plt.yticks(y_pos, labels)

    # Set y-limits to prevent autoscaling from squishing
    min_y = min(y_pos) - spacing
    max_y = max(y_pos) + spacing
    plt.ylim(min_y, max_y)

    plt.xlabel('Distance from "Meat Eating"')
    plt.title('Node distances from "Meat Eating"')
    plt.tight_layout()
    
    if savefig: 
        plt.savefig(savefig, dpi=300)
    else: 
        plt.show();
    plt.close()

plot_closeness(
    node_dict = node_dict,
    savefig = f'fig/networks_{session}/{key}_rank.png'
)
# --- SECOND NETWORK REPRESENTATION ---

# --- ENERGY ---
# --- E Simple ---
meat_categories = [
    "never",
    "less than once a week",
    "one or two days a week",
    "three or four days a week",
    "five or six days a week",
    "every day"
]
meat_conversion = {ele: num for num, ele in enumerate(meat_categories)}
likert_keys = [x+1 for x in range(7)]
val_zero_to_one = np.linspace(0, 1, num=len(likert_keys))
val_minus_to_plus = np.linspace(-1, 1, num=len(likert_keys))

map_zero_to_one = dict(zip(likert_keys, val_zero_to_one))
map_minus_to_plus = dict(zip(likert_keys, val_minus_to_plus))

meat_present_lik = meat_conversion.get(meat_present) 
meat_present_num = map_minus_to_plus.get(meat_present_lik)

# attention
attention_pers_num = map_zero_to_one.get(attention_pers)
attention_soc_num = map_zero_to_one.get(attention_soc)

# pressure social behaviors
## take all of these out ...

# direct personal influence 
## take all of these out ... 

# then rescale somehow (not entirely clear though)
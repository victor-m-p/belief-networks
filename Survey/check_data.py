import numpy as np 
import pandas as pd 
import os 

def is_numeric_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

# data
d = pd.read_csv('data/data_project_1044868_2025_02_11.csv', sep=';')

# just start with one person 
d = d[d['lfdn'] == 22].reset_index()
focal_topic = 'animal products'

### textual data ###
free_thoughts = d['v_722'][0]
production_thoughts = d['v_1348'][0]
impact_thoughts = d['v_1349'][0]
consumption_thoughts = d['v_723'][0]

### behavioral outcome (focal) ### 
consumption_coding = {
    1: f'Only eat {focal_topic}',
    2: f'Daily {focal_topic}',
    3: f'Limited {focal_topic}',
    4: 'Vegeratian',
    5: 'Vegan',
}
consumption_likert = d['v_1269'][0]

### central belief nodes ###
n_beliefs = 10

# okay so this is a bit of a mess... 
# labels for positive and negative beliefs
belief_labels_con = [f'con_{x+1}' for x in range(int(n_beliefs/2))]
belief_labels_pro = [f'pro_{x+1}' for x in range(int(n_beliefs/2))]
belief_labels = belief_labels_con + belief_labels_pro 

# keys for positive and negative belief free writing
belief_free_pro_idx = [f"v_{x+1001}" for x in range(int(n_beliefs/2))]
belief_free_con_idx = [f"v_{x+1012}" for x in range(int(n_beliefs/2))]
belief_free_idx = belief_free_pro_idx + belief_free_con_idx

# keys for positive and negative belief ratings (absolute)
belief_importance_pro_abs_idx = [f"v_{x+1017}" for x in range(int(n_beliefs/2))]
belief_importance_con_abs_idx = [f"v_{x+1072}" for x in range(int(n_beliefs/2))]
belief_importance_abs_idx = belief_importance_pro_abs_idx + belief_importance_con_abs_idx

# keys for positive and negative belief ratings (relative)
belief_importance_pro_rel_idx = [f"v_{x+1022}" for x in range(int(n_beliefs/2))]
belief_importance_con_rel_idx = [f"v_{x+1077}" for x in range(int(n_beliefs/2))]
belief_importance_rel_idx = belief_importance_pro_rel_idx + belief_importance_con_rel_idx

# keys for attention rating 
belief_attention_idx = [f"v_{x+1338}" for x in range(n_beliefs)]

belief_nodes = {}
num = 0
for label, free, abs_rating, rel_rating, attention in zip(
    belief_labels, 
    belief_free_idx, 
    belief_importance_abs_idx, 
    belief_importance_rel_idx,
    belief_attention_idx):
    num += 1
    # Check if col_val is actually a string (and not one of the sentinel numbers)
    if isinstance(d[free][0], str) and not is_numeric_string(d[free][0]):
        belief_nodes[f"b_{num}"] = {
            "direction": label.split('_')[0],
            "num": label.split('_')[1],
            "belief": d[free][0],
            "abs_importance": d[abs_rating][0],
            "rel_importance": d[rel_rating][0],
            "attention": d[attention][0],
        }

# we can already make the belief network now 


# coupling to focal 
# coupling_focal_idx = [f"v_{x+1168}" for x in range(int(n_beliefs*3))]

### secondary beliefs ### 
secondary_order = ['v_717', 'v_718', 'v_719']
secondary_beliefs = [f'{x+11}' for x in range(n_beliefs)]

secondary_belief_dict = {}
for i, label in zip(secondary_beliefs, belief_labels): 
    temporary_list = []
    for j in secondary_order: 
        if isinstance(d[f'{j}_{i}'][0], str) and not is_numeric_string(d[f'{j}_{i}'][0]): 
            temporary_list.append(d[f'{j}_{i}'][0])
    if temporary_list:
        secondary_belief_dict[label] = temporary_list

### social contacts ### 
n_social_max = 8
social_labels = [(f"v_{x+901}", f"v_{x+927}", f"v_{x+1285}", f"s_{x+1}") for x in range(n_social_max)]

social_nodes = {}
for col_name, col_rating, col_focal, node_type in social_labels: 
    if isinstance(d[col_name][0], str) and not is_numeric_string(d[col_name][0]): 
        social_nodes[node_type] = {
            "name": d[col_name][0],
            "rating": d[col_rating][0],
            "focal": d[col_focal][0]} 

### social --> focal ###


### social --> other ### 


### mapping things ### 
rows = []

for node_name, attrs in belief_nodes.items():
    direction = attrs["direction"]  # e.g. "con" or "pro"
    # e.g. if node_name == "b_2", then index_part == "2"
    index_part = node_name.split("_")[1]
    
    # second-level dict key, e.g. "con_2" or "pro_2"
    second_level_key = f"{direction}_{index_part}"
    
    if second_level_key in secondary_belief_dict:
        # For each text in that second-level list
        for i, text in enumerate(secondary_belief_dict[second_level_key], start=1):
            second_level_node_name = f"{second_level_key}_{i}"
            
            # Collect a row for the DataFrame
            rows.append([
                node_name,              # "b_2"
                second_level_node_name, # "con_2_1", "con_2_2", etc.
                text                    # "belief a", etc.
            ])

df_second_level = pd.DataFrame(
    rows, 
    columns=["first_level_node", "second_level_node", "second_level_text"]
)

# network viz # 
import networkx as nx 
import matplotlib.pyplot as plt 
G = nx.Graph()

# Focal node
focal_node = "focal"
G.add_node(focal_node)

# Add first-level belief nodes and connect them to focal
for node_name, attrs in belief_nodes.items():
    G.add_node(node_name, **attrs)  # store their attributes
    G.add_edge(focal_node, node_name, direction=attrs["direction"])

# Add second-level nodes
# We'll connect them to their respective first-level nodes.
for row in df_second_level.itertuples(index=False):
    first_level = row.first_level_node
    second_level = row.second_level_node
    text = row.second_level_text

    # Add the second-level node with the text as a node attribute
    # Also mark it as "second_level" so we can style it differently if we want
    G.add_node(second_level, text=text, node_type="second_level")

    # Add an edge from the first-level node to this second-level node
    # We can store a custom 'direction' or anything else we want
    G.add_edge(first_level, second_level, direction="secondary")

##############################################
# 4) Draw / visualize
##############################################
pos = nx.spring_layout(G, seed=42)  # fix a seed for repeatable layouts

# Separate edges by direction (pro, con, secondary)
pro_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "pro"]
con_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "con"]
sec_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "secondary"]

# Draw edges in different colors
nx.draw_networkx_edges(G, pos, edgelist=pro_edges, edge_color="tab:red", width=2)
nx.draw_networkx_edges(G, pos, edgelist=con_edges, edge_color="tab:blue", width=2)
nx.draw_networkx_edges(G, pos, edgelist=sec_edges, edge_color="black", style="dotted")

# We can size the focal node and the first-level nodes differently
focal_node_list = [focal_node]
first_level_nodes = [n for n in belief_nodes.keys()]  # 'con_1', 'con_2', ...
second_level_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "second_level"]

# Node sizes for first-level beliefs (scale abs_importance by some factor)
first_level_sizes = [belief_nodes[n]["abs_importance"] * 10 for n in first_level_nodes]

# Draw focal node (single node)
nx.draw_networkx_nodes(G, pos, nodelist=focal_node_list,
                       node_size=600, node_color="yellow")

# Draw first-level nodes
nx.draw_networkx_nodes(G, pos, nodelist=first_level_nodes,
                       node_size=first_level_sizes, node_color="lightgray")

# Draw second-level nodes (smaller, a different color)
nx.draw_networkx_nodes(G, pos, nodelist=second_level_nodes,
                       node_size=200, node_color="lightblue")

# Add labels to all nodes
nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

plt.axis("off")
plt.show()

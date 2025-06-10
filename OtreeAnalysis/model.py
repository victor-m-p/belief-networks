import numpy as np 
import pandas as pd 
import os 
import json 
import matplotlib.pyplot as plt 

dir = 'data_clean'
files = os.listdir(dir)
possible_nodes = ["ACCEPTED", "USER", "MODIFIED"]

def load_file(dir, f):
    with open(os.path.join(dir, f), 'r') as f: 
        loaded_dict = json.load(f)
    return loaded_dict 

p_dicts = [load_file(dir, f) for f in files]

def organize_nodes_edges(participant_dict: dict):

    # add direction to edges + take out list 
    for num, x in enumerate(participant_dict['edges_3']):
        participant_dict['edges_3'][num]['direction'] = 1 if x['polarity']=='positive' else -1
    edge_list = participant_dict['edges_3']

    # take out node list and create a dict with label as key
    node_list = participant_dict['pos_3']
    node_dict = {}
    for n in node_list: 
        node_dict[n['label']] = {'x': n['x'], 'y': n['y'], 'radius': n['radius']}

    return edge_list, node_dict 

# scale radius:
max_radius = 80
min_radius = 8 

user_nodes_edges = {}
for p_dict in p_dicts:
    user_id = p_dict['code']
    edges, nodes = organize_nodes_edges(p_dict)
    user_nodes_edges[user_id] = {
        'edges': edges,
        'nodes': nodes
    }

# has to be a better setup than this
def find_other_nodes(node_label, edge_list):
    multiplication = []
    for e in edge_list:
        if node_label == e['fromLabel']:
            other_node = e['toLabel']
            e_mult = e['direction']
            multiplication.append((other_node, e_mult))
        elif node_label == e['toLabel']:
            other_node = e['fromLabel']
            e_mult = e['direction']
            multiplication.append((other_node, e_mult))
        else:
            continue 
    return multiplication

def calculate_H(node_dict, edge_list, edge_scaling=20):
    node_pressure_list = []
    total_pressure = 0
    for key, val in node_dict.items(): 
        node_pressure = 0 
        focal_weight = val['radius']
        active_edges = find_other_nodes(key, edge_list)
        
        node_pressure += focal_weight # per definition positive
        
        # edges 
        for other_node, direction in active_edges:
            other_weight = node_dict[other_node]['radius']    
            node_pressure += direction * (focal_weight/edge_scaling) * (other_weight/edge_scaling)
        
        # add the minus 
        node_pressure = -node_pressure  # as per definition, we want the pressure to be negative
        total_pressure += node_pressure
        
        node_pressure_list.append((key, focal_weight, node_pressure))

    return node_pressure_list, total_pressure

energy_dict = {}

edge_scaling = 20
for user_id, data in user_nodes_edges.items():
    edges = data['edges']
    nodes = data['nodes']
    # Calculate H for each user
    h_list, h_total = calculate_H(nodes, edges, edge_scaling=edge_scaling)
    energy_dict[user_id] = {
        'H_list': h_list,
        'H_total': h_total
    }

# check energy of systems: 
H_dict = {}
for user_id, data in energy_dict.items():
    H_dict[user_id] = data['H_total']

# plot all of the nodes here
fig, ax = plt.subplots(figsize=(4, 3))
for user_id, data in energy_dict.items():
    h_list = data['H_list']
    xy = [(x, y) for _, x, y in h_list]
    plt.scatter(*zip(*xy), label=user_id, alpha=0.5)
plt.xlabel('Radius of node')
plt.ylabel('H(node)')
plt.savefig(f'fig/model/energy_{edge_scaling}.png', dpi=300, bbox_inches='tight')

# find H > 0
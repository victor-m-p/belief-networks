import pandas as pd 
import numpy as np 
import json

coupling_codes = {
    1: "con",
    2: "con",
    3: "con",
    4: "neut",
    5: "pro",
    6: "pro",
    7: "pro",
}

def likert_conversion(n): 
    scale_dict = {}
    for i in range(1, n+1):
        val = -1 + 2 * (i - 1) / (n - 1) if n > 1 else 0
        scale_dict[i] = val
    return scale_dict
likert_scale_7 = likert_conversion(7)

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Add other type conversions if needed
        return super().default(obj)

def likert_conversion(n):
    return np.linspace(-1, 1, n)

def is_numeric_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

# data
d = pd.read_csv('data/data_project_1046442_2025_02_18.csv', sep=';')

# just start with one person 
participant_id = 17
d = d[d['lfdn'] == participant_id].reset_index()
focal_topic = 'animal products'

# Initialize master node/edge containers
nodes = {}
edges = []

# 1) Focal node
coupling_focal = d['v_1460'][0]
nodes['focal'] = {
    'type': 'belief',
    'level': 0,
    'direction': coupling_codes[coupling_focal],
    'direction_num': likert_scale_7.get(coupling_focal),
    'domain': 'consumption of animal products',
    'likert': coupling_focal,
    'abs_importance': d['v_1615'][0],
    'belief_text': d['v_722'][0],
}

n_beliefs = 10

# nodes 
belief_free_pro_idx = [f"v_{x+1012}" for x in range(int(n_beliefs/2))]
belief_free_con_idx = [f"v_{x+1001}" for x in range(int(n_beliefs/2))]
belief_free_idx = belief_free_pro_idx + belief_free_con_idx

# node values
belief_val_pro = [f"v_{x+1461}" for x in range(int(n_beliefs/2))]
belief_val_con = [f"v_{x+1622}" for x in range(int(n_beliefs/2))]
belief_val_idx = belief_val_pro + belief_val_con

# couplings to focal 
belief_coupling_pro = [f"v_{x+1466}" for x in range(int(n_beliefs/2))]
belief_coupling_con = [f"v_{x+1627}" for x in range(int(n_beliefs/2))]
belief_coupling_idx = belief_coupling_pro + belief_coupling_con

# keep track of which beliefs exist
b_num = []

node_counter = 0
for i in range(n_beliefs):
    # direction is 'con' if i < 5, else 'pro'
    direction = "pro" if i < 5 else "con"
    
    # Check if there's a valid string for the free text
    free_val = d[belief_free_idx[i]][0]
    
    if isinstance(free_val, str) and not is_numeric_string(free_val):
        b_num.append(i)
        b_id = f"b_{node_counter}"   # "b_1", "b_2", etc.
        
        # add node
        nodes[b_id] = {
            "type": "belief",
            "level": 1,
            "direction": direction,
            "direction_num": 1 if direction == "pro" else -1,
            "belief_text": free_val,
            "abs_importance": d[belief_val_idx[i]][0],
        }
        
        # add edge
        edges.append({
            "source": b_id,
            "target": "focal",
            "direction": direction,
            "direction_num": 1 if direction == "pro" else -1,
            "type": "belief_to_focal",
            "coupling": d[belief_coupling_idx[i]][0]
        })
        
    node_counter += 1

# belief couplings 
# each of these is a list (I believe)
fix_mapping = {
    0: 5,
    1: 6,
    2: 7,
    3: 8,
    4: 9,
    5: 0,
    6: 1,
    7: 2,
    8: 3,
    9: 4,
}

for n_source in range(n_beliefs):
    for n_target in range(n_beliefs): 
        source_label = n_source + 1814
        target_label = n_target + 11
        coupling_column = f"v_{source_label}_{target_label}"
        if d[coupling_column][0] >= 0: 
            coupling_value = d[coupling_column][0]
            source_raw = fix_mapping[n_source]
            target_raw = fix_mapping[n_target]
            edges.append({
                "source": f"b_{source_raw}", 
                "target": f"b_{target_raw}", 
                "direction": coupling_codes[coupling_value],
                "direction_num": 1 if coupling_codes[coupling_value] == "pro" else -1,
                "type": "belief_to_belief",
                "coupling": coupling_value,
            })

# save data
with open(f'data/nodes_{participant_id}.json', 'w') as f:
    f.write(json.dumps(nodes, cls=NumpyEncoder))

df_edges = pd.DataFrame(edges)
df_edges.to_csv(f'data/edges_{participant_id}.csv', index=False)

# social overall here # 

### social contacts ### 
n_social_max = 3
social_labels = [(f"v_{x+901}", f"v_{x+927}", f"v_{x+1285}", f"s_{x+1}") for x in range(n_social_max)]
social_nodes = {}
for col_name, col_importance, col_focal, node_type in social_labels: 
    if isinstance(d[col_name][0], str) and not is_numeric_string(d[col_name][0]): 
        social_nodes[node_type] = {
            "name": d[col_name][0],
            "rating": d[col_importance][0],
            "focal": d[col_focal][0]} 
        nodes[node_type] = {
            "type": "social_belief",
            "level": 0,
            "value": d[col_focal][0],
            "social_name": d[col_name][0],
            "abs_importance": d[col_importance][0],
        }
        edges.append({
            "source": node_type,
            "target": "focal",
            "type": "social_to_focal",
        })

### social --> other ### 
# must be a smarter way to do this 
potential_beliefs = [f"b_{x+1}" for x in range(10)]
actual_beliefs = [x for x in nodes.keys() if nodes[x]['level'] == 1]
social_belief_idx = [f"v_{x+1358}" for x in range(n_beliefs)]
indices = [potential_beliefs.index(b) for b in actual_beliefs]
social_belief_idx = [social_belief_idx[x] for x in indices]

n_social = len(social_nodes)
social_contact_idx = [x+1 for x in range(n_social_max)]

# social_beliefs = {}
#social_i = 0
for person in range(n_social): 
    social_i = 0
    belief_list = []
    for belief_idx, belief_link in zip(social_belief_idx, actual_beliefs): 
        social_i += 1
        social_belief_string = f"{belief_idx}_{person+1}"
        social_belief = d[social_belief_string][0]
        nodes[f"s_{person+1}_{social_i}"] = {
            "type": "social_belief",
            "level": 1,
            "belief_text": social_belief,
            "social_contact": social_nodes[f"s_{person+1}"]['name'],
            "abs_importance": social_nodes[f"s_{person+1}"]['rating'],
            "focal": social_nodes[f"s_{person+1}"]['focal']
        }
        edges.append({
            "source": f"s_{person+1}_{social_i}",
            "target": belief_link,
            "type": "social_belief_connection"
        })

# save data
with open('data/nodes.json', 'w') as f:
    f.write(json.dumps(nodes, cls=NumpyEncoder))

df_edges = pd.DataFrame(edges)
df_edges.to_csv('data/edges.csv', index=False)

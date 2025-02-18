import pandas as pd 
import numpy as np 
import json

def likert_conversion(n):
    return np.linspace(-1, 1, n)

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

consumption_coding = {
    1: f'Only eat {focal_topic}',
    2: f'Daily {focal_topic}',
    3: f'Limited {focal_topic}',
    4: 'Vegeratian',
    5: 'Vegan',
}

# Initialize master node/edge containers
nodes = {}
edges = []

# 1) Focal node
nodes['focal'] = {
    'type': 'belief',
    'level': 0,
    'domain': 'consumption of animal products',
    'likert': d['v_1269'][0],
    'likert_code': consumption_coding[d['v_1269'][0]],
    'brainstorm': d['v_722'][0],
    'production': d['v_1348'][0],
    'impact': d['v_1349'][0],
    'consumption': d['v_723'][0],
    'abs_importance': 100, # placeholder 
}

# We'll store a dict that maps "con_1" -> "b_1", "pro_1" -> "b_6", etc.
n_beliefs = 10

belief_free_pro_idx = [f"v_{x+1001}" for x in range(int(n_beliefs/2))]
belief_free_con_idx = [f"v_{x+1012}" for x in range(int(n_beliefs/2))]
belief_free_idx = belief_free_pro_idx + belief_free_con_idx

belief_importance_pro_abs_idx = [f"v_{x+1017}" for x in range(int(n_beliefs/2))]
belief_importance_con_abs_idx = [f"v_{x+1072}" for x in range(int(n_beliefs/2))]
belief_importance_abs_idx = belief_importance_pro_abs_idx + belief_importance_con_abs_idx

belief_importance_pro_rel_idx = [f"v_{x+1022}" for x in range(int(n_beliefs/2))]
belief_importance_con_rel_idx = [f"v_{x+1077}" for x in range(int(n_beliefs/2))]
belief_importance_rel_idx = belief_importance_pro_rel_idx + belief_importance_con_rel_idx

belief_attention_idx = [f"v_{x+1338}" for x in range(n_beliefs)]

# Now let's build the first-level beliefs properly
first_level_ids = []  # We'll keep track of which IDs we create, in order.

node_counter = 0
for i in range(n_beliefs):
    node_counter += 1
    # direction is 'con' if i < 5, else 'pro'
    direction = "con" if i < 5 else "pro"
    
    # Check if there's a valid string for the free text
    free_val = d[belief_free_idx[i]][0]
    if isinstance(free_val, str) and not is_numeric_string(free_val):
        b_id = f"b_{node_counter}"   # "b_1", "b_2", etc.
        
        # Build the node
        nodes[b_id] = {
            "type": "belief",
            "level": 1,
            "direction": direction,
            "belief_text": free_val,
            "abs_importance": d[belief_importance_abs_idx[i]][0],
            "rel_importance": d[belief_importance_rel_idx[i]][0],
            "attention": d[belief_attention_idx[i]][0],
        }
        
        # Keep track of it (for edges or later reference)
        first_level_ids.append(b_id)

# Now create edges from the focal node to each first-level belief
for b_id in first_level_ids:
    edges.append({
        "source": "focal",
        "target": b_id,
        "type": "focal_to_belief"
    })

        
### secondary beliefs ### 
secondary_order = ['v_717', 'v_718', 'v_719']
secondary_beliefs = [f'{x+11}' for x in range(n_beliefs)]
secondary_labels = [f'b_{x+1}' for x in range(n_beliefs)]

secondary_belief_dict = {}
for i, label in zip(secondary_beliefs, secondary_labels): 
    temporary_list = []
    for j in secondary_order: 
        if isinstance(d[f'{j}_{i}'][0], str) and not is_numeric_string(d[f'{j}_{i}'][0]): 
            temporary_list.append(d[f'{j}_{i}'][0])
    if temporary_list:
        secondary_belief_dict[label] = temporary_list

# add secondary beliefs to nodes
# add secondary beliefs to edges
for parent_b_id, sec_belief_list in secondary_belief_dict.items():
    for i, sec_text in enumerate(sec_belief_list, start=1):
        # Construct a new node ID like "b_1_1", "b_1_2", etc.
        new_b_id = f"{parent_b_id}_{i}"
        
        # Create the node
        nodes[new_b_id] = {
            "type": "belief",
            "level": 2,               # or "second_level"
            "direction": nodes[parent_b_id]["direction"],
            "belief_text": sec_text,
            "parent": parent_b_id
        }

        # Create an edge from the parent (first-level) belief to this new second-level node
        edges.append({
            "source": new_b_id,
            "target": parent_b_id,
            "type": "personal_belief_connection"
        })

### social contacts ### 
n_social_max = 8
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

# save data
with open('data/nodes.json', 'w') as f:
    f.write(json.dumps(nodes, cls=NumpyEncoder))

df_edges = pd.DataFrame(edges)
df_edges.to_csv('data/edges.csv', index=False)

import json 
import numpy as np 
import pandas as pd

### setup ### 
def likert_conversion(x, y, n):
    linspace = np.linspace(x, y, n)
    return {i: val for i, val in enumerate(linspace, 1)}

# import data 
def clean_gpt(participant_id):
    with open(f'data/gpt_raw/metadict_{participant_id}.json', 'r') as f:
        data = json.load(f)

    focal_node_gpt = data['focal_node_gpt']
    personal_nodes_gpt = data['personal_nodes_gpt']
    personal_edges_gpt = data['personal_edges_gpt']
    social_focal_gpt = data['social_focal_gpt']
    social_personal_gpt = data['social_personal_gpt']
    metavar_gpt = data['metavar_gpt']

    likert_scale_7 = likert_conversion(-1, 1, 7)

    nodes_pro_con = {
        'b_0': 'pro',
        'b_1': 'pro',
        'b_2': 'pro',
        'b_3': 'pro',
        'b_4': 'pro',
        'b_5': 'con',
        'b_6': 'con',
        'b_7': 'con',
        'b_8': 'con',
        'b_9': 'con',
    }

    ### personal network ### 
    personal_nodes = {}
    personal_edges = []

    # add focal 
    personal_nodes['b_focal'] = {
        'type': 'personal_belief',
        'level': 0,
        'value': focal_node_gpt['consumption'],
        'value_num': likert_scale_7[focal_node_gpt['consumption']],
        'importance': focal_node_gpt['importance'],
        'importance_scaled': focal_node_gpt['importance'] / 100
    } 

    # add personal to focal
    for i, (name, importance, coupling) in enumerate(zip(personal_nodes_gpt['name'], personal_nodes_gpt['importance'], personal_nodes_gpt['coupling'])):
        direction_val = 1 if nodes_pro_con[name]=='pro' else -1
        personal_nodes[name] = {
            'type': 'personal_belief',
            'level': 1,
            'value': 1, #direction_val,
            'value_num': 1, #direction_val,
            'direction': nodes_pro_con[name],
            'importance': importance,
            'importance_scaled': importance / 100
        }
        personal_edges.append(
            {
                'type': 'belief_coupling',
                'source': name,
                'target': 'b_focal',
                'direction': nodes_pro_con[name],
                'value_num': direction_val,
                'coupling': coupling,
                'coupling_scaled': coupling * 0.01 * direction_val
            }
        )

    # add personal to personal (couplings)
    for i, (source, target, coupling) in enumerate(zip(personal_edges_gpt['source'], personal_edges_gpt['target'], personal_edges_gpt['coupling'])):
        # this direction thing is really not necessary anymore
        direction_val = 1 if nodes_pro_con[source]=='pro' else -1
        personal_edges.append(
            {
                'type': 'belief_coupling',
                'source': source,
                'target': target,
                'direction': nodes_pro_con[source],
                'value_num': direction_val,
                'coupling': coupling,
                'coupling_scaled': likert_scale_7[coupling]
            }
        )
        

    ### social network ###
    social_nodes = {}
    social_edges = []

    # social focal 
    for i, (name, consumption, importance) in enumerate(zip(social_focal_gpt['name'], social_focal_gpt['consumption'], social_focal_gpt['importance'])):
        social_nodes[f's_{i}'] = {
            'type': 'social_belief',
            'level': 0,
            'label': name,
            'value': consumption,
            'value_num': likert_scale_7[consumption],
            'importance': importance,
            'importance_scaled': importance * 0.01
        }
        social_edges.append(
            {
                'type': 'social_coupling',
                'source': f's_{i}',
                'target': 'b_focal',
                'coupling': importance,
                'coupling_scaled': importance * 0.01
            }
        )

    # social edges 
    social_coding = {
        'A': 0,
        'B': 1,
        'C': 2
    }

    for i, (name, motivation, rating) in enumerate(zip(social_personal_gpt['name'], social_personal_gpt['motivation'], social_personal_gpt['rating'])):
        direction_val = 1 if nodes_pro_con[motivation]=='pro' else -1
        b_num = motivation.split('_')[1]
        social_num = social_coding[name]
        
        # we need to flip the likert scale if b_num is con
        multiplier = 1 if int(b_num) < 5 else -1 
        
        social_nodes[f"s_{social_num}_{b_num}"] = {
            'type': 'social_belief',
            'level': 1,
            'label': name,
            'value': rating,
            'value_num': likert_scale_7[rating] * multiplier,
            'importance': social_nodes[f's_{social_num}']['importance'],
            'importance_scaled': social_nodes[f's_{social_num}']['importance'] * 0.01
        } 
        social_edges.append(
            {
                'type': 'social_coupling',
                'source': f's_{social_num}_{b_num}',
                'target': motivation,
                'coupling': social_nodes[f's_{social_num}']['importance'],
                'coupling_scaled': social_nodes[f's_{social_num}']['importance'] * 0.01
            }
        )

    metadict_gpt = {
        'personal_nodes': personal_nodes,
        'personal_edges': personal_edges,
        'social_nodes': social_nodes,
        'social_edges': social_edges,
        'metavar': metavar_gpt
    }

    with open(f'data/gpt_clean/metadict_{participant_id}.json', 'w') as f:
        f.write(json.dumps(metadict_gpt))

# run 
participant_ids = [16, 17, 18, 19, 22, 26, 27]
for p_id in participant_ids: 
    clean_gpt(p_id)
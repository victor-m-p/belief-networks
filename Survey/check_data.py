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
belief_keys = [f'v_{x+1001}' for x in range(int(n_beliefs/2))] + [f'v_{x+1012}' for x in range(int(n_beliefs/2))]
belief_labels = [f'c_{x+1}' for x in range(int(n_beliefs/2))] + [f'p_{x+1}' for x in range(int(n_beliefs/2))]
belief_nodes = {}
for col_name, node_type in zip(belief_keys, belief_labels):
    # Check if col_val is actually a string (and not one of the sentinel numbers)
    if isinstance(d[col_name][0], str) and not is_numeric_string(d[col_name][0]):
        belief_nodes[node_type] = d[col_name][0]

# belief node importance?


### secondary beliefs ### 
secondary_order = ['v_717', 'v_718', 'v_719']
secondary_beliefs = [f'{x+11}' for x in range(10)]

secondary_belief_dict = {}
for i, label in zip(secondary_beliefs, belief_labels): 
    temporary_list = []
    for j in secondary_order: 
        if isinstance(d[f'{j}_{i}'][0], str) and not is_numeric_string(d[f'{j}_{i}'][0]): 
            temporary_list.append(d[f'{j}_{i}'][0])
    if temporary_list:
        secondary_belief_dict[label] = temporary_list

str_cols = d.select_dtypes(include=['object'])
str_cols.dtypes
str_cols['v_717_11']
str_cols['v_717_12']
str_cols['v_718_11']
str_cols['v_718_12']

### coupling to focal ### 


### social contacts ### 
n_social_max = 8
social_labels = [(f"v_{x+901}", f"v_{x+927}", f"v_{x+1285}", f"s_{x+1}") for x in range(n_social_max)]

social_nodes = {}
for col_name, col_rating, col_focal, node_type in social_labels: 
    if isinstance(d[col_name][0], str): 
        social_nodes[node_type] = {
            "name": d[col_name][0],
            "rating": d[col_rating][0],
            "focal": d[col_focal][0]} 


### social --> focal ###

### predictions ### 
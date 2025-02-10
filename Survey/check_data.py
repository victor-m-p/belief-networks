import numpy as np 
import pandas as pd 
import os 

# data
d = pd.read_csv('data/export.csv', sep=';')
focal_topic = 'animal products'

### textual data ###
free_thoughts = d['v_722'][0]
#production_thoughts = d['v_1348'][0]
#impact_thoughts = d['v_1349'][0]
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
belief_labels = [
    ("v_1001", 'c_1'), 
    ("v_1002", 'c_2'), 
    ("v_1003", 'c_3'),
    ("v_1004", 'c_4'),
    ("v_1005", 'c_5'),
    ('v_1012', 'p_1'),
    ('v_1013', 'p_2'),
    ('v_1014', 'p_3'),
    ('v_1015', 'p_4'),
    ('v_1016', 'p_5')]
belief_nodes = {}

for col_name, node_type in belief_labels:
    # Check if col_val is actually a string (and not one of the sentinel numbers)
    if isinstance(d[col_name][0], str):
        belief_nodes[node_type] = d[col_name][0]

### secondary beliefs ### 
# how the fuck do I get that out? # 

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
import numpy as np 
import pandas as pd 

d = pd.read_csv('data/all_apps_wide-2025-05-15.csv')
d.columns[39:49]

# base path 
base_str = 'otreesurvey_app.1.player'

# demographics
age = d[[f"{base_str}.age"]]
closest = d[[f"{base_str}.feel_closest"]]
closest_pty = d[[f"{base_str}.feel_closest_party"]]
polarized = d[[f'{base_str}.how_polarised']]

# positions
import json 
json_str = d[f"{base_str}.positions"].iloc[0]
pos_list = json.loads(json_str)

# edges
json_str = d[f"{base_str}.edges"].iloc[0]
edge_list = json.loads(json_str)

# all of the writing
q1 = d[f"{base_str}.main_q1_response"].iloc[0] # etc.

# all of the nodes
n1 = d[f"{base_str}.label_1"].iloc[0] # etc.
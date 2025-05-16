
import numpy as np 
import pandas as pd 

d = pd.read_csv('data/all_apps_wide-2025-05-16.csv')

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
n_answers = 5 
answer_list = [d[f'{base_str}.answer{i+1}'].iloc[0] for i in range(n_answers)]

# all of the LLM 
prompt_used = d[f'{base_str}.prompt_used'].iloc[0]
llm_result = json.loads(d[f'{base_str}.llm_result'].iloc[0])
generated_nodes = json.loads(d[f'{base_str}.generated_nodes'].iloc[0])
accepted_nodes = json.loads(d[f'{base_str}.accepted_nodes'].iloc[0])

### things to calculate / test ###
# save prompt ... 

import numpy as np 
import pandas as pd 
import json 

d = pd.read_csv('data/all_apps_wide-2025-05-28-pretest.csv')

# base path 
base_str = 'otreesurvey_app.1.player'

# demographics
age = d[[f"{base_str}.age"]] # how is this nan for one person__
gender = d[[f"{base_str}.gender"]] 
education = d[[f"{base_str}.education"]]
politics = d[[f'{base_str}.politics']]

# answers 
n_answers = 5 
answer_list = [d[f'{base_str}.answer{i+1}'].iloc[0] for i in range(n_answers)]

# LLM proposed  
prompt_used = d[f'{base_str}.prompt_used'].iloc[0]
llm_result = json.loads(d[f'{base_str}.llm_result'].iloc[0])
generated_nodes = json.loads(d[f'{base_str}.generated_nodes'].iloc[0])

# LLM+Human
''' Try to do this properly. '''
revised_nodes = json.loads(d[f'{base_str}.revised_beliefs'].iloc[0])
final_nodes = json.loads(d[f'{base_str}.final_nodes'].iloc[0])
user_nodes = json.loads(d[f'{base_str}.user_nodes'].iloc[0]) 

# Network (NB: where is importance?)
def json_loads_helper(df, column):
    return json.loads(df[column].iloc[0])

## Stage 1  
pos_1 = json_loads_helper(d, f"{base_str}.positions_1")

## Stage 2 
pos_2 = json_loads_helper(d, f"{base_str}.positions_2")
edges_2 = json_loads_helper(d, f"{base_str}.edges_2")

## stage 3 
pos_3 = json_loads_helper(d, f"{base_str}.positions_3")
edges_3 = json_loads_helper(d, f"{base_str}.edges_3")


import numpy as np 
import pandas as pd 
import json 
from collections import Counter

d = pd.read_csv('data/all_apps_wide-2025-05-28-pretest.csv')

def position_to_dict(
    df, 
    position,
    base_str="otreesurvey_app.1.player", 
    n_answers=5,
    n_questionnaire=3):

    everything = {
        # code + demographics + questionnaire 
        'code': df[f"participant.code"].iloc[position],
        'age': df[f"{base_str}.age"].iloc[position],
        'gender': df[f"{base_str}.gender"].iloc[position],
        'education': df[f"{base_str}.education"].iloc[position],
        'politics': df[f"{base_str}.education"].iloc[position],
        'questionnaire': [df[f"{base_str}.policy_{i+1}"].iloc[position] for i in range(n_questionnaire)],
        
        # writing 
        'answers': [df[f"{base_str}.answer{i+1}"].iloc[position] for i in range(n_answers)],
        
        # nodes 
        'llm_nodes': json.loads(df[f"{base_str}.generated_nodes"].iloc[position]),
        'revised_nodes': json.loads(df[f"{base_str}.revised_beliefs"].iloc[position]),
        'final_nodes': json.loads(df[f"{base_str}.final_nodes"].iloc[position]),
        
        # positions
        'pos_1': json.loads(df[f"{base_str}.positions_1"].iloc[position]),
        'pos_2': json.loads(df[f"{base_str}.positions_2"].iloc[position]),
        'edges_2': json.loads(df[f"{base_str}.edges_2"].iloc[position]),
        'pos_3': json.loads(df[f"{base_str}.positions_3"].iloc[position]),
        'edges_3': json.loads(df[f"{base_str}.edges_3"].iloc[position]),
        
        # evaluation
        'network_rating': df[f"{base_str}.network_reflection_rating"].iloc[position],
        'network_reflection': d[f"{base_str}.network_reflection_text"].iloc[position],

    }
    
    return everything

participant_ids = [i+2 for i in range(9)]

for participant_id in participant_ids: 
    user_dict = position_to_dict(
        df = d,
        base_str = "otreesurvey_app.1.player",
        position = participant_id,
        n_answers = 5)

    with open(f'data_clean/dict_{participant_id}.json', 'w') as f:
        json.dump(user_dict, f)
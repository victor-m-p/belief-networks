import numpy as np 
import pandas as pd 
import json 
import json

df = pd.read_csv('data/prolific/all_apps_wide-2025-06-24.csv')
base_str = 'otreesurvey_app.1.player'
n_answers = 4
position = 0

# remove rows with na participant label
df = df.dropna(subset=['participant.label'])
n_rows = len(df)

# helper variables and functions
five_point_scale = {
    1: 'Not at all',
    2: 'Slightly',
    3: 'Moderately',
    4: 'Very well',
    5: 'Extremely well'
}

polarity_conversion = {
    0: "No Influence",
    1: "Positive Influence",
    2: "Negative Influence" 
}

def safe_json_loads(value, fallback="NA"):
    try:
        if pd.isna(value):
            return fallback
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return fallback

vemi_questions = [
    "I want to be healthy",
    "Plant-based diets are better for the environment",
    "Animals do not have to suffer",
    "Animals’ rights are respected",
    "I want to live a long time",
    "Plant-based diets are more sustainable",
    "I care about my body",
    "Eating meat is bad for the planet",
    "Animal rights are important to me",
    "Plant-based diets are environmentally-friendly",
    "It does not seem right to exploit animals",
    "Plants have less of an impact on the environment than animal products",
    "I am concerned about animal rights",
    "My health is important to me",
    "I don’t want animals to suffer"
    ]

# build dictionary 
data = {}
for i in range(n_rows):
    
    # things we need to precompute
    network_reflection_rating = df[f'{base_str}.network_reflection_rating'].iloc[i]
    
    # create the dictionary 
    code_i = df['participant.code'].iloc[i]
    data[code_i] = {
        'demographics': {
            'age': df[f'{base_str}.age'].iloc[i],
            'gender': df[f'{base_str}.gender'].iloc[i],
            'education': df[f'{base_str}.education'].iloc[i],
            'politics': df[f'{base_str}.politics'].iloc[i],
            'state': df[f'{base_str}.state'].iloc[i],
            'zipcode': df[f'{base_str}.zipcode'].iloc[i],
        },
        'answers': {
            'answer1': df[f'{base_str}.answer1'].iloc[i],
            'answer2': df[f'{base_str}.answer2'].iloc[i],
            'answer3': df[f'{base_str}.answer3'].iloc[i],
            'answer4': df[f'{base_str}.answer4'].iloc[i],
        },
        'meat_scale': {
            'present': df[f'{base_str}.meat_consumption_present'].iloc[i],
            'past': df[f'{base_str}.meat_consumption_past'].iloc[i],
            'future': df[f'{base_str}.meat_consumption_future'].iloc[i]
        },
        'meat_social': json.loads(df[f'{base_str}.social_circle_distribution'].iloc[i]),
        'LLM': {
            'prompt': df[f'{base_str}.prompt_used'].iloc[i],
            'results': json.loads(df[f'{base_str}.llm_result'].iloc[i])
        },
        'nodes': {
            'generated': json.loads(df[f'{base_str}.generated_nodes'].iloc[i]), 
            'final': json.loads(df[f'{base_str}.final_nodes'].iloc[i]),
            'ratings': json.loads(df[f'{base_str}.generated_nodes_ratings'].iloc[i]) 
        },
        'positions': {
            'pos_1': json.loads(df[f'{base_str}.positions_1'].iloc[i]),
            'pos_2': json.loads(df[f'{base_str}.positions_2'].iloc[i]),
            'pos_3': json.loads(df[f'{base_str}.positions_3'].iloc[i]),
            'pos_4': json.loads(df[f'{base_str}.positions_4'].iloc[i]),
            'pos_5': json.loads(df[f'{base_str}.positions_5'].iloc[i])
        },
        'edges': {
            'edges_2': json.loads(df[f'{base_str}.edges_2'].iloc[i]),
            'edges_3': json.loads(df[f'{base_str}.edges_3'].iloc[i]),
            'edges_4': json.loads(df[f'{base_str}.edges_4'].iloc[i]),
            'edges_5': json.loads(df[f'{base_str}.edges_5'].iloc[i])
        },
        'network_rating': {
            'rating_int': network_reflection_rating,
            'rating_str': five_point_scale.get(network_reflection_rating) 
        },
        'network_reflection': {
            'difficult': df[f'{base_str}.network_reflection_text'].iloc[i],
            'missing': df[f'{base_str}.network_surprise_text'].iloc[i], 
            'learn': df[f'{base_str}.network_learn_text'].iloc[i]
        },
        'plausibility': {
            'edge_pair_ratings': safe_json_loads(df[f'{base_str}.plausibility_edge_pairs_data'].iloc[i]),            'e1_polarity': df[f'{base_str}.plausibility_edge_1_type'].iloc[i],
            'e1_strength': df[f'{base_str}.plausibility_edge_1_strength'].iloc[i],
            'e2_polarity': df[f'{base_str}.plausibility_edge_2_type'].iloc[i],
            'e2_strength': df[f'{base_str}.plausibility_edge_2_strength'].iloc[i],
            'e3_polarity': df[f'{base_str}.plausibility_edge_3_type'].iloc[i],
            'e3_strength': df[f'{base_str}.plausibility_edge_3_strength'].iloc[i]
        },
        'node_importance': safe_json_loads(df[f'{base_str}.importance_ratings'].iloc[i]),
        'social_pressure': safe_json_loads(df[f'{base_str}.social_pressure_personal_beliefs'].iloc[i]),
        'vemi': {ele: df[f'{base_str}.vemi_{num+1}'].iloc[i] for num, ele in enumerate(vemi_questions)},
        'attention': {
            'personal': df[f'{base_str}.attention_personal'].iloc[i],
            'social': df[f'{base_str}.attention_social'].iloc[i]
        }
    }

# save data 
with open('data_clean/prolific/data_2025-06-24.json', 'w') as f:
    json.dump(data, f, indent=2)

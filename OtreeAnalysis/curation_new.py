import numpy as np 
import pandas as pd 
import json 
from collections import Counter

df = pd.read_csv('data/all_apps_wide-2025-06-18(1).csv')
base_str = 'otreesurvey_app.1.player'
n_answers = 4
position = 0

# --- DEMOGRAPHICS ---
code = df[f'participant.code'].iloc[0]
age = df[f'{base_str}.age'].iloc[0]
gender = df[f'{base_str}.gender'].iloc[0]
edu = df[f'{base_str}.education'].iloc[0]
pol = df[f'{base_str}.politics'].iloc[0]
state = df[f'{base_str}.state'].iloc[0]
zipcode = df[f'{base_str}.zipcode'].iloc[0]

# --- ANSWERS TO QUESTIONS ---
answers = [df[f"{base_str}.answer{i+1}"].iloc[position] for i in range(n_answers)],

# --- MEAT SCALE ---
meat_present = df[f'{base_str}.meat_consumption_present'].iloc[0]
meat_past = df[f'{base_str}.meat_consumption_past'].iloc[0]
meat_future = df[f'{base_str}.meat_consumption_future'].iloc[0]

# --- SOCIAL CIRCLE ---
meat_social = json.loads(df[f'{base_str}.social_circle_distribution'].iloc[0])
assert sum(meat_social.values()) == 100, "social distribution does not sum to 100"

# --- LLM ---
prompt_used = df[f'{base_str}.prompt_used'].iloc[0]
llm_result = json.loads(df[f'{base_str}.llm_result'].iloc[0])
generated_nodes = json.loads(df[f'{base_str}.generated_nodes'].iloc[0])
final_nodes = json.loads(df[f'{base_str}.final_nodes'].iloc[0])
node_ratings = json.loads(df[f'{base_str}.generated_nodes_ratings'].iloc[0])

# --- POSITIONS ---
pos_1 = json.loads(df[f'{base_str}.positions_1'].iloc[0])
pos_2 = json.loads(df[f'{base_str}.positions_2'].iloc[0])
pos_3 = json.loads(df[f'{base_str}.positions_3'].iloc[0])
pos_4 = json.loads(df[f'{base_str}.positions_4'].iloc[0])
pos_5 = json.loads(df[f'{base_str}.positions_5'].iloc[0])

edges_2 = json.loads(df[f'{base_str}.edges_2'].iloc[0])
edges_3 = json.loads(df[f'{base_str}.edges_3'].iloc[0])
edges_4 = json.loads(df[f'{base_str}.edges_4'].iloc[0])
edges_5 = json.loads(df[f'{base_str}.edges_5'].iloc[0])

# --- NETWORK REFLECTION ---
five_point_scale = {
    1: 'Not at all',
    2: 'Slightly',
    3: 'Moderately',
    4: 'Very well',
    5: 'Extremely well'
}
network_rating_int = df[f'{base_str}.network_reflection_rating'].iloc[0]
network_rating_str = five_point_scale.get(network_rating_int)

network_difficult_text = df[f'{base_str}.network_reflection_text'].iloc[0]
network_missing_text = df[f'{base_str}.network_surprise_text'].iloc[0]
network_learn_text = df[f'{base_str}.network_learn_text'].iloc[0]

# --- PLAUSIBILITY ---
polarity_conversion = {
    0: "No Influence",
    1: "Positive Influence",
    2: "Negative Influence" 
}
edge_pair_ratings = json.loads(df[f'{base_str}.plausibility_edge_pairs_data'].iloc[0])
e1_polarity = df[f'{base_str}.plausibility_edge_1_type'].iloc[0]
e1_strength = df[f'{base_str}.plausibility_edge_1_strength'].iloc[0]
e2_polarity = df[f'{base_str}.plausibility_edge_2_type'].iloc[0]
e2_strength = df[f'{base_str}.plausibility_edge_2_strength'].iloc[0]
e3_polarity = df[f'{base_str}.plausibility_edge_3_type'].iloc[0]
e3_strength = df[f'{base_str}.plausibility_edge_3_strength'].iloc[0]

# --- RATINGS ---
importance_rating = json.loads(df[f'{base_str}.importance_ratings'].iloc[0])
social_pressure_beliefs = json.loads(df[f'{base_str}.social_pressure_personal_beliefs'].iloc[0])

# --- VEMI ---
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
vemi_data = {ele: df[f'{base_str}.vemi_{num+1}'].iloc[0] for num, ele in enumerate(vemi_questions)}

# --- ATTENTION ---
attention_pers = df[f'{base_str}.attention_personal'].iloc[0]
attention_soc = df[f'{base_str}.attention_social'].iloc[0]
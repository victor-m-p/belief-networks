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

# --- ANALYSIS ---
# --- NETWORKS ---
import networkx as nx 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches

text_mapping = {node['text']: node['belief'] for node in final_nodes}
text_mapping['Meat Eating'] = 'Meat Eating'
type_mapping = {node['stance']: [node['type'], node['category']] for node in generated_nodes}
type_mapping['Meat Eating'] = ['PERSONAL', 'BEHAVIOR']

def category_to_color(node_type, node_category):
    if node_type == 'PERSONAL' and node_category == 'MOTIVATION':
        return 'tab:blue'
    elif node_type == 'PERSONAL' and node_category == 'BEHAVIOR':
        return 'tab:grey'
    elif node_type == 'SOCIAL' and node_category == 'MOTIVATION':
        return 'tab:orange'
    else: 
        return 'tab:green'

def get_colors(node_text):
    node_text_clean = text_mapping.get(node_text)
    node_type, node_category = type_mapping.get(node_text_clean)
    return category_to_color(node_type, node_category)

def plot_network(node_dict, edge_dict):

    G = nx.Graph()
    pos = {}
    radii = {}

    for node in node_dict: 
        label = node['label']
        G.add_node(label)
        pos[label] = (node['x'], node['y'])
        radii[label] = node['radius']

    # test flipping y
    max_y = max(y for _, y in pos.values())
    pos = {label: (x, max_y - y) for label, (x, y) in pos.items()}

    for edge in edge_dict: 
        G.add_edge(edge['from'], edge['to'], polarity=edge['polarity'], size=edge['strength'])

    # node and edge properties / visuals 
    edge_colors = ['tab:green' if G[u][v]['polarity'] == 'positive' else 'tab:red' for u, v in G.edges()]
    edge_size = [G[u][v]['size']/10 for u, v in G.edges()]
    node_sizes = [radii[n] ** 2 for n in G.nodes()] 
    node_colors = [get_colors(n) for n in G.nodes()]

    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_size)

    for label, (x, y) in pos.items():
        ax.annotate(
            label,
            (x, y),
            textcoords='offset points',
            xytext=(0, 0),
            ha='center',
            va='center',
            fontsize=12,
            clip_on=False  # <-- this allows text to go beyond axes
        )

    plt.show();
    
node_dict = pos_5
edge_dict = edges_5

plot_network(node_dict, edge_dict)

# --- SECOND NETWORK REPRESENTATION ---

# --- ENERGY ---
# --- E Simple ---
meat_categories = [
    "never",
    "less than once a week",
    "one or two days a week",
    "three or four days a week",
    "five or six days a week",
    "every day"
]
meat_conversion = {ele: num for num, ele in enumerate(meat_categories)}
likert_keys = [x+1 for x in range(7)]
val_zero_to_one = np.linspace(0, 1, num=len(likert_keys))
val_minus_to_plus = np.linspace(-1, 1, num=len(likert_keys))

map_zero_to_one = dict(zip(likert_keys, val_zero_to_one))
map_minus_to_plus = dict(zip(likert_keys, val_minus_to_plus))

meat_present_lik = meat_conversion.get(meat_present) 
meat_present_num = map_minus_to_plus.get(meat_present_lik)

# attention
attention_pers_num = map_zero_to_one.get(attention_pers)
attention_soc_num = map_zero_to_one.get(attention_soc)

# pressure social behaviors
## take all of these out ...

# direct personal influence 
## take all of these out ... 

# then rescale somehow (not entirely clear though)
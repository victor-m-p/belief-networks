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

text_mapping = {node['belief']: node['text'] for node in final_nodes}
generated_nodes
node_dict = pos_3
edge_dict = edges_3

# 1. this is on its head for some reason 
# 2. the colors should be red/green 
# 3. how do I scale it to be exactly like they see it?
# 4. need to color based on category: a little complicated but okay. 
G = nx.Graph()
pos = {}
radii = {}

for node in node_dict: 
    label = node['label']
    G.add_node(label)
    pos[label] = (node['x'], node['y'])
    radii[label] = node['radius']

for edge in edge_dict: 
    G.add_edge(edge['from'], edge['to'], polarity=edge['polarity'], size=edge['strength'])

# node and edge properties / visuals 
edge_colors = ['tab:red' if G[u][v]['polarity'] == 'positive' else 'tab:blue' for u, v in G.edges()]
edge_size = [G[u][v]['size']/10 for u, v in G.edges()]
node_sizes = [radii[n] ** 2 for n in G.nodes()] 


fig, ax = plt.subplots(figsize=(8, 8))

# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, edgecolors='black')
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

def plot_network(participant_id: str, node_dict: dict, edge_dict: dict, node_types=False, label_nodes=True):

    G = nx.Graph()

    # Add nodes with position and radius
    pos = {}
    radii = {}
    for node in node_dict:
        label = node['label']
        G.add_node(label)
        pos[label] = (node['x'], node['y'])
        radii[label] = node['radius']

    # Optionally add color
    if node_types:
        node_colors, source_to_color = color_nodes(G, node_types)
    else: 
        node_colors = 'tab:gray' 
        source_to_color = {}

    # Step 3: Add edges with polarity
    for edge in edge_dict:
        G.add_edge(edge['fromLabel'], edge['toLabel'], polarity=edge['polarity'])

    # Step 4: Prepare colors and sizes
    edge_colors = ['tab:red' if G[u][v]['polarity'] == 'positive' else 'tab:blue' for u, v in G.edges()]
    node_sizes = [radii[n] ** 2 for n in G.nodes()]  # area-based scaling

    fig, ax = plt.subplots(figsize=(8, 8))

    # Draw nodes and edges
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=node_sizes, node_color=node_colors, edgecolors='black')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=2)

    # Manually draw labels with clip_on=False
    if label_nodes: 
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

    # Problems with clipping on x axis 
    x_vals, _ = zip(*pos.values())
    x_margin = (max(x_vals) - min(x_vals)) * 0.3
    ax.set_xlim(min(x_vals) - x_margin, max(x_vals) + x_margin)
    ax.axis('off')
    
    # Legend patches
    legend_handles = [
        mpatches.Patch(color=source_to_color.get('ACCEPTED'), label='Accepted'),
        mpatches.Patch(color=source_to_color.get('USER'), label='User'),
        mpatches.Patch(color=source_to_color.get('MODIFIED'), label='Modified'),
    ]

    # Place legend *outside* the axes, in fixed bottom right of figure
    fig.legend(
        handles=legend_handles,
        #loc='upper right',
        bbox_to_anchor=(0.98, 0.02), 
        borderaxespad=0.2,
        frameon=False,
        fontsize=12
    )
    
    # Let tight_layout reposition the figure canvas to include overhanging labels
    fig.tight_layout()

    # Save without cropping
    if partici
    plt.savefig(f'fig/networks/{participant_id}.png', dpi=300, bbox_inches='tight')
    plt.close()

plot_network(
    id = 'whatever',
    
)

p_dicts = [load_file(dir, f) for f in files]
for dic in p_dicts: 
    id = dic['code']
    nodes = dic['pos_3']
    edges = dic['edges_3']
    node_types = dic['final_nodes']
    plot_network(id, nodes, edges, node_types, label_nodes=True)

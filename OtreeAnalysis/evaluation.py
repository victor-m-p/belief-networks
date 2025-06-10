import numpy as np 
import pandas as pd 
import os 
import json 
import networkx as nx 
import matplotlib.pyplot as plt 
import matplotlib.patches as mpatches
from collections import Counter
import seaborn as sns 
from matplotlib.ticker import MaxNLocator

dir = 'data_clean'
files = os.listdir(dir)
possible_nodes = ["ACCEPTED", "USER", "MODIFIED"]

def load_file(dir, f):
    with open(os.path.join(dir, f), 'r') as f: 
        loaded_dict = json.load(f)
    return loaded_dict 

p_dicts = [load_file(dir, f) for f in files]

# curate node types 
def count_node_types(p_dicts): 
    participant_nodes = {}

    for dic in p_dicts: 
        
        # access basic values
        participant_id = dic['code']
        llm_nodes = dic['llm_nodes']
        n_proposed = len(llm_nodes)
        final_nodes = dic['final_nodes']
        final_nodes_types = [node['source'] for node in final_nodes]
        counts = Counter(final_nodes_types)
        type_counts = {key: counts.get(key, 0) for key in possible_nodes}
        type_counts['PROPOSED'] = n_proposed
        
        # calculate additional counts
        type_counts['PROPOSED+USER'] = type_counts['PROPOSED'] + type_counts['USER']
        type_counts['A+U+M'] = type_counts['ACCEPTED'] + type_counts['USER'] + type_counts['MODIFIED']
        type_counts["REJECTED"] = type_counts["PROPOSED"] - type_counts["ACCEPTED"]

        # % accepted 
        type_counts['% ACCEPTED'] = (type_counts['ACCEPTED'] / type_counts['PROPOSED']) * 100
        type_counts['% MODIFIED'] = (type_counts['MODIFIED'] / type_counts['PROPOSED']) * 100
        type_counts['% REJECTED'] = (type_counts['REJECTED'] / type_counts['PROPOSED']) * 100
        
        # % user nodes
        type_counts['% USER'] = (type_counts['USER'] / type_counts['A+U+M']) * 100

        # TP, TN, FP, FN
        #type_counts['TP'] = type_counts['ACCEPTED'] / type_counts['A+U+M']
        #type_counts['FP'] = 1 - (type_counts['PROPOSED'] / type_counts['ACCEPTED'])

        # store in dict
        participant_nodes[participant_id] = type_counts 
    
    return participant_nodes

participant_nodes = count_node_types(p_dicts)

# dataframe 
records = [
    {'Participant': pid, 'Metric': metric, 'Percentage': value}
    for pid, metrics in participant_nodes.items()
    for metric, value in metrics.items()  # include only % metrics
]
df_long = pd.DataFrame(records) 

# plot boxplots
def plot_boxplot(df, metrics, outname=False):

    # subset 
    df_long = df[df['Metric'].isin(metrics)].copy()

    plt.figure(figsize=(6, 4))
    sns.boxplot(data=df_long, x='Metric', y='Percentage')

    plt.title('Accuracy Metrics')
    plt.ylabel('Percentage')
    plt.xlabel('')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if outname: 
        plt.savefig(f"fig/evaluation/{outname}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

metrics = ['% ACCEPTED', '% MODIFIED', '% REJECTED', '% USER']
plot_boxplot(df_long, metrics, outname='accuracy_metrics')

# plot number of nodes per participant
# the scale for network rating is 1-5
def gather_ratings(p_dicts: list):

    evaluation_dict = {
        1: "Not at all",
        2: "Slightly",
        3: "Moderately",
        4: "Very well",
        5: "Extremely well"
    }

    eval_net = {}
    for dic in p_dicts: 
        participant_id = dic['code']    
        network_rating = dic['network_rating']
        rating_text = evaluation_dict.get(network_rating)
        network_reflection = dic['network_reflection']
        eval_net[participant_id] = {
            'network_rating': network_rating,
            'rating_text': rating_text,
            'network_reflection': network_reflection
        }
    
    return eval_net

# Get list of rating_text values
eval_net = gather_ratings(p_dicts)

def plot_evaluation_ratings(p_dicts: list, eval_net: dict, outname=False):
    rating_texts = [entry['rating_text'] for entry in eval_net.values() if entry['rating_text']]

    df = pd.DataFrame({'rating_text': rating_texts})

    plt.figure(figsize=(8, 5))
    ax = sns.countplot(data=df, x='rating_text',
                       order=['Not at all', 'Slightly', 'Moderately', 'Very well', 'Perfectly'])

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))  # <--- Force integer y-axis ticks

    plt.title('Network Ratings')
    plt.xlabel('Likert-scale Rating Category')
    plt.ylabel('Num Responses')
    plt.xticks(rotation=30)
    plt.tight_layout()

    if outname:
        plt.savefig(f"fig/evaluation/{outname}.png", dpi=300, bbox_inches='tight')
    else:
        plt.show()
    plt.close()

plot_evaluation_ratings(p_dicts, eval_net, outname='network_rating')

# save all of the participant evaluations 
def write_reflections(eval_net: dict):
    user_string = ""
    for user in eval_net.keys():
        network_rating = eval_net[user]['network_rating']
        network_reflection = eval_net[user]['network_reflection']
        rating_text = eval_net[user]['rating_text']
        if isinstance(network_reflection, str): 
            user_string += f"User {user}\nRating: {network_rating} ({rating_text})\nReflection: {network_reflection}\n\n"
    
    with open('fig/evaluation/network_reflections.txt', 'w') as f:
        f.write(user_string)

write_reflections(eval_net)

# plot number of nodes against answer length
# (run this again without the filter).
def resolution_plot(p_dicts: list):
    x_vals = []
    y_vals = []
    for dic in p_dicts:     
        llm_nodes = dic['llm_nodes']
        len_llm_nodes = len(llm_nodes)
        answers = dic['answers']
        answer_num_char = sum(len(a) for a in answers)
        x_vals.append(answer_num_char)
        y_vals.append(len_llm_nodes)
    plt.scatter(x_vals, y_vals)
    plt.xlabel('Input length (char)')
    plt.ylabel('Numberf of LLM-proposed nodes')
    plt.title('Input length and number nodes proposed')
    plt.savefig('fig/evaluation/resolution.png', dpi=300, bbox_inches='tight')
    plt.close();
    
resolution_plot(p_dicts)
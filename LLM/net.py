import numpy as np
import pandas as pd 
import networkx as nx 
import json 
import os 
import matplotlib.pyplot as plt 
from fun import load_and_clean, replacements

def networkx_simple(G, node_size, edge_width, node_color, output=None):

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.axis('off')
    pos = nx.spring_layout(G, seed=516)
    nx.draw_networkx_nodes(
        G, 
        pos=pos, 
        node_size=[ns*500 for ns in node_size],
        node_color=node_color,
        cmap=plt.cm.coolwarm,
        vmin=-1,
        vmax=1)
    nx.draw_networkx_edges(
        G, 
        pos=pos, 
        width=[ew*10 for ew in edge_width], 
        edge_color='gray')
    nx.draw_networkx_labels(
        G, 
        pos=pos)
    plt.tight_layout()

    if output:
        plt.savefig(output)
    else:
        plt.show();

inpath='data_output'
taker='z6k.json'
with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)

nodes = load_and_clean(data['answer_1'], replacements)
edges = load_and_clean(data['answer_2'], replacements)

df_edges = pd.DataFrame(edges, columns=['source', 'target', 'weight'])
df_nodes = pd.DataFrame(nodes, columns=['belief long', 'belief', 'agreement', 'importance'])

G = nx.from_pandas_edgelist(df_edges, 'source', 'target', ['weight'])

df_nodes_indexed = df_nodes.set_index('belief')
node_attr_dict = df_nodes_indexed.to_dict('index')
nx.set_node_attributes(G, node_attr_dict)

edge_width = [G[u][v]['weight'] for u,v in G.edges()]
node_size = [G.nodes[n]['importance'] for n in G.nodes()] # not good at getting difference here: might be better to just have it order from most to least.
node_color = [G.nodes[n]['agreement'] for n in G.nodes()]

networkx_simple(G, node_size, edge_width, node_color, f'fig/{taker}_simple.png')

# try the other network 
nodes = load_and_clean(data['answer_3'], replacements)
edges = load_and_clean(data['answer_4'], replacements)

df_edges = pd.DataFrame(edges, columns=['source', 'target', 'weight'])
df_nodes = pd.DataFrame(nodes, columns=['belief long', 'belief',  'agreement', 'importance'])

G = nx.from_pandas_edgelist(df_edges, 'source', 'target', ['weight'])

df_nodes_indexed = df_nodes.set_index('belief')
node_attr_dict = df_nodes_indexed.to_dict('index')
nx.set_node_attributes(G, node_attr_dict)

edge_width = [G[u][v]['weight'] for u,v in G.edges()]
node_size = [G.nodes[n]['importance'] for n in G.nodes()]
node_color = [G.nodes[n]['agreement'] for n in G.nodes()]

networkx_simple(G, node_size, edge_width, node_color, f'fig/{taker}_elaborate.png')

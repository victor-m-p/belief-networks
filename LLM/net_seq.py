import numpy as np
import pandas as pd 
import networkx as nx 
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

inpath = 'data_output_seq'
case = 'onw.json'
df_nodes = pd.read_csv(os.path.join(inpath, f'{case}_nodes.csv'))
df_edges_directed = pd.read_csv(os.path.join(inpath, f'{case}_edges_directed.csv'))
df_edges_undirected = pd.read_csv(os.path.join(inpath, f'{case}_edges_undirected.csv'))

G = nx.from_pandas_edgelist(df_edges_undirected, 'belief_x', 'belief_y', ['influence'])

df_nodes_indexed = df_nodes.set_index('belief')
node_attr_dict = df_nodes_indexed.to_dict('index')
nx.set_node_attributes(G, node_attr_dict)

edge_width = [G[u][v]['influence'] for u,v in G.edges()]
node_size = [G.nodes[n]['attention'] for n in G.nodes()] # not good at getting difference here: might be better to just have it order from most to least.
node_color = [G.nodes[n]['stance'] for n in G.nodes()]

networkx_simple(G, node_size, edge_width, node_color)

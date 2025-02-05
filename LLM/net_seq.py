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
    
    # determine if node_color is already assigned (string)
    # or whether it is not (a number)
    if isinstance(node_color[0], str): 
        print('string')
        nx.draw_networkx_nodes(
            G,
            pos=pos,
            node_size=[ns*700 for ns in node_size],
            node_color=node_color
        )
    else: 
        nx.draw_networkx_nodes(
            G, 
            pos=pos, 
            node_size=[ns*700 for ns in node_size],
            node_color=node_color,
            cmap=plt.cm.coolwarm,
            vmin=-1,
            vmax=1
            )
    nx.draw_networkx_edges(
        G, 
        pos=pos, 
        width=[ew*5 for ew in edge_width], 
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
outpath = 'fig_seq'
case = 'z6k.json'
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

networkx_simple(G, node_size, edge_width, node_color, output=os.path.join(outpath, f'{case}_simple.png'))

## okay now do the extended network ## 
# nodes
df_nodes_additional = pd.read_csv(os.path.join(inpath, f'{case}_nodes_additional.csv'))
df_nodes_additional['type'] = "inferred"
df_nodes['type'] = "original"
df_nodes_combined = pd.concat([df_nodes, df_nodes_additional])
df_nodes_combined['color'] = df_nodes_combined['type'].apply(lambda x: 'tab:orange' if x == 'inferred' else 'tab:blue')

# edges
df_edges_undirected_additional = pd.read_csv(os.path.join(inpath, f'{case}_edges_undirected_additional.csv'))
df_edges = pd.concat([df_edges_undirected, df_edges_undirected_additional])

# now just do the plot 
G = nx.from_pandas_edgelist(df_edges, 'belief_x', 'belief_y', ['influence'])

df_nodes_indexed = df_nodes_combined.set_index('belief')
node_attr_dict = df_nodes_indexed.to_dict('index')
nx.set_node_attributes(G, node_attr_dict)

edge_width = [G[u][v]['influence'] for u,v in G.edges()]
node_size = [G.nodes[n]['attention'] for n in G.nodes()] # not good at getting difference here: might be better to just have it order from most to least.
node_color = [G.nodes[n]['color'] for n in G.nodes()]

networkx_simple(G, node_size, edge_width, node_color, output=os.path.join(outpath, f'{case}_extended.png'))

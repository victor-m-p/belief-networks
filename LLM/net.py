import numpy as np
import pandas as pd 
import networkx as nx 
import json 
import os 
import re 
import ast 

def string_to_list(string): 
    clean_string = re.sub(r"\s+", " ", string).strip()
    clean_list = ast.literal_eval(clean_string)
    return clean_list

inpath='data_output'
taker='vmp.json'
with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)
        
edges = data['answer_2']
edges = string_to_list(edges)

nodes = data['answer_1']
nodes = string_to_list(nodes)

df_edges = pd.DataFrame(edges, columns=['source', 'target', 'weight'])
df_nodes = pd.DataFrame(nodes, columns=['topic', 'assertion', 'agreement', 'importance'])

G = nx.from_pandas_edgelist(df_edges, 'source', 'target', ['weight'])

df_nodes_indexed = df_nodes.set_index('topic')
node_attr_dict = df_nodes_indexed.to_dict('index')
nx.set_node_attributes(G, node_attr_dict)

edge_width = [G[u][v]['weight'] for u,v in G.edges()]
node_size = [G.nodes[n]['importance'] for n in G.nodes()] # not good at getting difference here: might be better to just have it order from most to least.

pos = nx.spring_layout(G)
nx.draw_networkx_nodes(G, pos=pos, node_size=[ns*300 for ns in node_size])
nx.draw_networkx_edges(G, pos=pos, width=[ew*10 for ew in edge_width])
nx.draw_networkx_labels(G, pos=pos)
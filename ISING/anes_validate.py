import pandas as pd 
import numpy as np
from fun import *

# load params 
path = 'ANES/anes_2016.txt_params.dat'
n_nodes = 17
fields, couplings = load_mpf_params(n_nodes, path)
p = p_dist(fields, couplings)
states = bin_states(n_nodes)
states[states == -1] = 0

# also load the data
anes_2016 = pd.read_csv('ANES/anes_2016.csv')
anes_2016 = anes_2016.drop(columns='weight')

# focus on p for now
item_list = anes_2016.columns.tolist()
df_p = pd.DataFrame(p, columns=['p'])
df_c = pd.DataFrame(states, columns=item_list)
df_pc = pd.concat([df_p, df_c], axis=1)
df_pc['p'] = df_pc['p'].round(3)
df_pc['idx'] = df_pc.index

# check whether the states are valid
# now instead we have to check whether each row is in the allowed states
valid_states = generate_valid_states([4, 3, 4, 3, 3])
df_valid = pd.DataFrame(valid_states, columns=item_list)
df_valid = df_pc.merge(df_valid, on = item_list, how = 'inner')
df_valid = df_valid.sort_values('p', ascending=False)
df_valid['p'].sum() # 88.2% of the probability mass (now only 50% for the big model)

''' the most favored states
gay marry, imm stay: >50% 
gay union, imm stay: 8.6%
gay marry, imm cit: 4.3%
gay marry, imm restrict: 4.3%
gay no, imm stay: 4.3%
gay marry, imm dep: 3.7%
gay no, imm dep: 1.5%
'''

df_valid['p_reweight'] = df_valid['p'] / df_valid['p'].sum()

''' reweighting this we get: 
65.4% <- why is the top one so high? 
9.75%
4.88%
4.88%
4.88%
4.2%
1.7%
...
'''

# check the actual top frequencies
anes_2016 = anes_2016.groupby(item_list).size().reset_index(name='count')
anes_2016['observed_frequency'] = anes_2016['count'] / anes_2016['count'].sum()
anes_2016.sort_values('observed_frequency', ascending=False)

# merge everything
df_valid = df_valid.rename(columns={'p': 'p_model',
                                    'p_reweight': 'p_model_norm'})
df_combined = df_valid.merge(anes_2016, on = item_list, how = 'inner')

''' frequencies: 
gay marry, imm stay: 37.4%
gay union, imm stay: 13.2%
gay marry, imm cit: 9.12%
gay no, imm stay: 7.8%
gay marry, imm rest: 7.5%
gay marry, imm dep: 6.3%
'''

##### plotting #####
from fun import plot_probabilities
p_true = df_combined['observed_frequency'].to_numpy()
p_model = df_combined['p_model_norm'].to_numpy()
plot_probabilities(p_true, p_model) # overestimating the most observed (still)

# look at parameters 
def node_edge_lst(J, h, labels=None): 
    if not labels: 
        labels = [node+1 for node in range(len(h))]
    comb = list(itertools.combinations(labels, 2))
    df_edgelist = pd.DataFrame(comb, columns = ['n1', 'n2'])
    df_edgelist['weight'] = J
    df_nodes = pd.DataFrame(labels, columns = ['n'])
    df_nodes['size'] = h
    df_nodes = df_nodes.set_index('n')
    dict_nodes = df_nodes.to_dict('index')
    return df_edgelist, dict_nodes

df_edgelist, dict_nodes = node_edge_lst(couplings, fields, labels=item_list)

### now plot this ###
import networkx as nx


G = nx.from_pandas_edgelist(
    df_edgelist,
    'n1',
    'n2',
    edge_attr=['weight'] 
)

for key, val in dict_nodes.items():
    G.nodes[key]['size'] = val['size']

labeldict = {}
for i in G.nodes(): 
    labeldict[i] = i

cmap = plt.cm.coolwarm
pos = nx.nx_agraph.graphviz_layout(G, prog='fdp')

fig, ax = plt.subplots()
plt.axis('off')

size_list = list(nx.get_node_attributes(G, 'size').values())
weight_list = list(nx.get_edge_attributes(G, 'weight').values())
weight_absolute = np.abs(weight_list)

vmax_edges = np.max(list(np.abs(weight_list)))
vmin_edges = -vmax_edges

vmax_nodes = np.max(list(np.abs(size_list)))
vmin_nodes = -vmax_nodes

nx.draw_networkx_nodes(
    G, pos, 
    node_size = 600,
    node_color = size_list, 
    edgecolors = 'black',
    linewidths = 0.5,
    cmap = cmap, vmin = vmin_nodes, vmax = vmax_nodes 
)
nx.draw_networkx_edges(
    G, pos,
    width = weight_absolute, 
    edge_color = weight_list, 
    alpha = 0.7, 
    edge_cmap = cmap, edge_vmin = vmin_edges, edge_vmax = vmax_edges)
nx.draw_networkx_labels(G, pos, font_size = 14, labels = labeldict)

# gets much worse with large N. 

# make a nice plot

# also, actually can we do some prediction now?
# like we have a measure of p
# and we can make a distance measure
# 1) number of flips
# 2) distance of flips (like hamming)

# okay, calculate distance
# way 1: n changed beliefs
# way 2: total distance
# --> but then we are back to treating them as equally far
# --> that might be really weird 
# --> question is whether that now is "in" the model somehow
# --> i.e. in the $p$ 
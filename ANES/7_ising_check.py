import numpy as np
import pandas as pd 
from fun import *
import networkx as nx
import seaborn as sns 

# load data 2016
fields_2016, couplings_2016 = load_mpf_params(
    n_nodes=6,
    path="mpf/anes_2016.txt_params.dat"
)

# load data 2020 
fields_2020, couplings_2020 = load_mpf_params(
    n_nodes=6,
    path="mpf/anes_2020.txt_params.dat"
)

# probabilities
configs = bin_states(6)
configs[configs < 0] = 0
p_2016 = p_dist(fields_2016, couplings_2016)
p_2020 = p_dist(fields_2020, couplings_2020)

# find observed rates 
questions = ['abort', 'church', 'gay', 'imm', 'tax', 'temp']
anes_2016 = pd.read_csv('mpf/anes_2016_wide.csv')
anes_2020 = pd.read_csv('mpf/anes_2020_wide.csv')

# make categorical to ensure that we get counts for all groups
anes_2016[questions] = anes_2016[questions].astype('category')
anes_2020[questions] = anes_2020[questions].astype('category')

obs_2016 = anes_2016.groupby(questions, observed=False).size().reset_index(name='count')
obs_2020 = anes_2020.groupby(questions, observed=False).size().reset_index(name='count')

obs_2016['freq'] = obs_2016['count'] / obs_2016['count'].sum()
obs_2020['freq'] = obs_2020['count'] / obs_2020['count'].sum()

# plot the basic params 
obs_2016['combination'] = obs_2016[questions].apply(lambda row: tuple(row), axis = 1)
obs_2020['combination'] = obs_2020[questions].apply(lambda row: tuple(row), axis = 1)

# param ordered
config_df = pd.DataFrame(configs, columns=questions)
config_df['ID'] = config_df.index

config_2016 = config_df.copy()
config_2020 = config_df.copy()

config_2016['p'] = p_2016
config_2020['p'] = p_2020

# merge
merge_2016 = config_2016.merge(obs_2016, on = questions, how = 'inner')
merge_2020 = config_2020.merge(obs_2020, on = questions, how = 'inner')

#### p vs observed ####
plot_probabilities(
    p_true = merge_2016['freq'], 
    p_est = merge_2016['p'], 
    ymax = 0.3)

plot_probabilities(
    p_true = merge_2020['freq'], 
    p_est = merge_2020['p'],
    ymax = 0.3)

# most common transitions
# well so this really blows up quickly actually

# just basic plot first
edgelist_2016, nodelist_2016 = node_edge_lst(couplings_2016, fields_2016, questions)
edgelist_2020, nodelist_2020 = node_edge_lst(couplings_2020, fields_2020, questions)

# okay so basically everything positively coupled
# so we would expect all positive and all negative to be common.
# then we have two strong couplings which might form other wedges.
def plot_nx(edgelist: pd.DataFrame, nodelist: dict, nodesize=500, edgesize=5):

    G = nx.from_pandas_edgelist(
        edgelist,
        'n1',
        'n2',
        edge_attr=['weight'] 
    )

    for key, val in nodelist.items():
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
    weight_absolute = np.abs(weight_list)*edgesize

    vmax_edges = np.max(list(np.abs(weight_list)))
    vmin_edges = -vmax_edges

    vmax_nodes = np.max(list(np.abs(size_list)))
    vmin_nodes = -vmax_nodes

    nx.draw_networkx_nodes(
        G, pos, 
        node_size = nodesize,
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

plot_nx(edgelist_2016, nodelist_2016)
plot_nx(edgelist_2020, nodelist_2020)

### most common states
# 1) all liberal
# 2) all liberal + church
# 3) all conservative
# 4) all conservative -imm
# 5) all conservative -imm -tax
# 6) all conservative -imm -tax -temp 
merge_2016.sort_values('count', ascending=False).head(10)

### most common states
# 1) all liberal
# 2) all liberal + church
# 3) all conservative
# 4) all conservative -imm
# 5) all conservative -imm -tax -temp
# 6) liberal +abort +church
merge_2020.sort_values('count', ascending=False).head(10)

### compute stability (empirical)
anes_2016['c_2016'] = anes_2016[questions].apply(lambda row: tuple(row), axis = 1)
anes_2020['c_2020'] = anes_2020[questions].apply(lambda row: tuple(row), axis = 1)

anes_2016_s = anes_2016[['ID', 'c_2016']]
anes_2020_s = anes_2020[['ID', 'c_2020']]

anes_2016_s['year'] = 2016
anes_2020_s['year'] = 2020

anes_merge = anes_2016_s.merge(anes_2020_s, on='ID', how='inner')
anes_merge['stay'] = anes_merge['c_2016'] == anes_merge['c_2020']
empirical_stability = anes_merge.groupby('c_2016')['stay'].mean().reset_index(name='stability')

# plot this against N 
anes_merge_2016_sub = merge_2016[['combination', 'p', 'freq']]
empirical_stability = empirical_stability.rename(columns={"c_2016": "combination"})
empirical_stability = empirical_stability.merge(anes_merge_2016_sub, on='combination', how='inner')

fig, ax = plt.subplots()
sns.scatterplot(data=empirical_stability, x='freq', y='stability', color='tab:blue')
sns.scatterplot(data=empirical_stability, x='p', y='stability', color='tab:orange')
sns.regplot(data=empirical_stability, x='freq', y='stability', color='tab:blue')
sns.regplot(data=empirical_stability, x='p', y='stability', color='tab:orange')
plt.xlabel('Observed Frequency (2016) & p(config)')
plt.ylabel('Empirical Stability (2016-2020)')

# would be fun to color by majority class maybe;
from configuration import Configuration

# okay p(move) for each state
states = np.arange(0, 64)
prob_move = []
for id in states: 
    ConfObj = Configuration(
        id=id, 
        states=configs, 
        probabilities=p_2016)
    prob_move.append((id, ConfObj.p_move()))

# a bit hacky here
df_pmove = pd.DataFrame(prob_move, columns=['id', 'p_move'])
empirical_stability['id'] = empirical_stability.index
stability_df = df_pmove.merge(empirical_stability, on='id', how='inner')
stability_df['p_stay'] = 1 - stability_df['p_move']
stability_df['log(p)'] = np.log(stability_df['p'])

# plot 
# why is it that this should be linear with log?
# there must be some good reason for this somehow
fig, ax = plt.subplots()
sns.scatterplot(data=stability_df, x='log(p)', y='p_stay')
sns.regplot(data=stability_df, x='log(p)', y='p_stay')
plt.xlabel(r'$log(p)$')
plt.ylabel(r'$p(i \rightarrow i)$')

# anyways plot the actual thing
fig, ax = plt.subplots()
sns.scatterplot(data=stability_df, x='p_stay', y='stability')
sns.regplot(data=stability_df, x='p_stay', y='stability')
plt.xlabel(r'$p(i \rightarrow i)$')
plt.ylabel(r'obs$(i \rightarrow i)$')

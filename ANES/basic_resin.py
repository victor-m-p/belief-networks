import pyreadstat
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import pickle
# https://electionstudies.org/data-center/2016-2020-panel-merged-file/

df, meta = pyreadstat.read_sav("2016_2020_mergedpanel.sav")

# ------- data selection ----------------- #

df['V161231'] # position gay marriage (pre-2016)
df['V201416'] # position gay marriage (pre-2020)

'''
1: legally marry
2: union but not marry
3: no legal recognition
'''

df['V161192'] # unauthorized immigrants (pre-2016)
df['V201417'] # unauthorized immigrants (pre-2020)

'''
1: most conservative
2: ...
3: ...
4: most liberal 
'''

df['V161224'] # rising temp (pre-2016)
df['V201401'] # rising temp (pre-2020)

'''
1: do more
2: do less
3: right amount
'''

df['V161232'] # abortion (pre-2016)
df['V201336'] # abortion (pre-2020)

'''
1: never permitted
2: three exceptions
3: other need
4: choice
'''

df_test = df[[
    'V161231', 
    'V201416', 
    'V161192', 
    'V201417', 
    'V161224',
    'V201401',
    'V161232',
    'V201336',
    #'V161347', --feminism mostly nan
    #'V202476' --feminism mostly nan
    ]]
df_test = df_test.rename(
    columns={
        'V161231': 'gay2016',
        'V201416': 'gay2020',
        'V161192': 'imm2016',
        'V201417': 'imm2020',
        'V161224': 'temp2016',
        'V201401': 'temp2020',
        'V161232': 'abort2016',
        'V201336': 'abort2020',
        #'V161347': 'fem2016',
        #'V202476': 'fem2020'
    }
)

# give meaningful names
recode_gay = {1: "marry", 2: "union", 3: "no"}
recode_imm = {1: "deport", 2: "restrict", 3: "stay", 4: "citizen"}
recode_temp = {1: "more", 2: "less", 3: "right"}
recode_abort = {1: "never", 2: "exceptions", 3: "need", 4: "choice"}
df_test['gay2016'] = df_test['gay2016'].map(recode_gay).fillna(np.nan)
df_test['gay2020'] = df_test['gay2020'].map(recode_gay).fillna(np.nan)
df_test['imm2016'] = df_test['imm2016'].map(recode_imm).fillna(np.nan)
df_test['imm2020'] = df_test['imm2020'].map(recode_imm).fillna(np.nan)
df_test['temp2016'] = df_test['temp2016'].map(recode_temp).fillna(np.nan)
df_test['temp2020'] = df_test['temp2020'].map(recode_temp).fillna(np.nan)
df_test['abort2016'] = df_test['abort2016'].map(recode_abort).fillna(np.nan)
df_test['abort2020'] = df_test['abort2020'].map(recode_abort).fillna(np.nan)

df_2016 = df_test[['gay2016', 'imm2016', 'temp2016', 'abort2016']]
df_2020 = df_test[['gay2020', 'imm2020', 'temp2020', 'abort2020']]

df_2016.isna().sum() # few nan
df_2020.isna().sum() # few nan

df_2016 = df_2016.dropna()

# get dummies
df_2016 = pd.get_dummies(df_2016)

# ----------------- network ---------------------- #
# calculate all pairwise correlations
corr = df_2016.corr() # consider nan. 

# remove negative things.
corr[corr < 0] = 0

# calculate the phi thing
import networkx as nx
# Create a NetworkX graph from the correlation matrix
G = nx.from_pandas_adjacency(corr)

# 1. Remove self-loops
G.remove_edges_from(nx.selfloop_edges(G))

# 2. Set positions for nodes
pos = nx.spring_layout(G, iterations=5000)

# 3. Scale edge widths based on weights
edge_multiplier = 10
edge_weights = [data['weight'] * edge_multiplier for _, _, data in G.edges(data=True)]  # Scale factor: 5

# 4. Draw the graph
plt.figure(figsize=(10, 7))

# Draw nodes and edges
nx.draw_networkx_nodes(G, pos, node_size=500, node_color="lightblue")
nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.7)

# Draw labels
labels = {node: node for node in G.nodes}
nx.draw_networkx_labels(G, pos, labels, font_size=12, font_color="black")

# Show the graph
plt.title("Correlation Graph", fontsize=16)
plt.axis("off")
plt.show()

# --------------------------------------- # 

# taking the positions; which are already 2-dimensional.
pos_list = [list(v) for v in pos.values()]

from sklearn.decomposition import PCA

# then PCA with 2 components? 
pca = PCA(n_components=2)
pca.fit(pos_list)
x_pca = pca.transform(pos_list)

new_pos = {}
for i, key in enumerate(pos.keys()): 
    new_pos[key] = [x_pca[i, 0], x_pca[i, 1]]

# 4. Draw the graph
plt.figure(figsize=(10, 5))

# Draw nodes and edges
nx.draw_networkx_nodes(G, new_pos, node_size=500, node_color="lightblue")
nx.draw_networkx_edges(G, new_pos, width=edge_weights, alpha=0.7)

# Draw labels
labels = {node: node for node in G.nodes}
nx.draw_networkx_labels(G, new_pos, labels, font_size=12, font_color="black")

# Show the graph
plt.title("Correlation Graph", fontsize=16)
plt.axis("off")
plt.savefig("correlation_graph.png")
plt.show()

# -------------- save data ----------------- #
df_test.to_csv("anes_data.csv", index=False)

with open('pos.pkl', 'wb') as f:
    pickle.dump(pos, f)

with open('new_pos.pkl', 'wb') as f:
    pickle.dump(new_pos, f)


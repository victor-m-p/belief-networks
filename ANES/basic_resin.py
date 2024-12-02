import pyreadstat
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
# https://electionstudies.org/data-center/2016-2020-panel-merged-file/

df, meta = pyreadstat.read_sav("data/2016_2020_mergedpanel.sav")

# ------- data selection ----------------- #
df = df[[
    'V161231', # gay marriage pre-2016
    'V201416', # gay marriage pre-2020
    'V161192', # unauth. immigrants pre-2016
    'V201417', # unauth. immigrants pre-2020
    'V161224', # rising temperature pre-2016
    'V201401', # rising temperature pre-2020
    'V161232', # abortion pre-2016
    'V201336', # abortion pre-2020
    'V162140', # rich tax pre-2016
    'V202325', # rich tax pre-2020
    'V162136', # econ mobility pre-2016
    'V202318', # econ mobility pre-2020
    ]]
df = df.rename(
    columns={
        'V161231': 'gay2016',
        'V201416': 'gay2020',
        'V161192': 'imm2016',
        'V201417': 'imm2020',
        'V161224': 'temp2016',
        'V201401': 'temp2020',
        'V161232': 'abort2016',
        'V201336': 'abort2020',
        'V162140': 'tax2016',
        'V202325': 'tax2020',
        'V162136': 'econ2016',
        'V202318': 'econ2020'
    }
)

# ----------------- data cleaning ---------------------- #

df = df.astype(int)
df['ID'] = df.index
df_long = df.melt(id_vars='ID', var_name='question', value_name='value')
df_long['year'] = df_long['question'].str.extract(r'(\d+)')
df_long['question'] = df_long['question'].str.extract(r'([a-zA-Z]+)')

# add question interpretation # 
code_answers = [
    ('gay', 1, 'marry'),
    ('gay', 2, 'union'),
    ('gay', 3, 'no'),
    ('imm', 1, 'deport'),
    ('imm', 2, 'restrict'),
    ('imm', 3, 'stay'),
    ('imm', 4, 'citizen'),
    ('abort', 1, 'never'),
    ('abort', 2, 'exceptions'),
    ('abort', 3, 'need'),
    ('abort', 4, 'choice'),
    ('tax', 1, 'favor'),
    ('tax', 2, 'oppose'),
    ('tax', 3, 'neither'),
    ('econ', 1, 'better'),
    ('econ', 2, 'worse'),
    ('econ', 3, 'same'),
]

code_answers = pd.DataFrame(code_answers, columns=['question', 'value', 'answer'])
df_long = pd.merge(df_long, code_answers, on=['question', 'value'], how='inner')

# full answers from all IDs otherwise drop
id_grouped = df_long.groupby('ID').size().reset_index(name='N')
max_n = id_grouped['N'].max()
id_grouped = id_grouped[id_grouped['N'] == max_n]
id_grouped = id_grouped['ID'].drop_duplicates()
df_long = df_long.merge(id_grouped, on='ID', how='inner').reset_index(drop=True)

# ----------------- data visualization ---------------------- #

df_2016 = df_long[df_long['year'] == '2016']
df_2016_wide = df_2016.pivot(index='ID', columns='question', values='answer')
df_2016_dummies = pd.get_dummies(df_2016_wide)

# ----------------- network ---------------------- #
# calculate all pairwise correlations
corr = df_2016_dummies.corr() # consider nan. 

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
plt.savefig("fig/correlation_graph.png")

# -------------- save data ----------------- #

# fix pos first 
df_pos = pd.DataFrame(new_pos).T.reset_index()
df_pos.columns = ['ID', 'xvalue', 'yvalue']
df_pos = df_pos.drop(columns='yvalue')
df_pos['question'] = df_pos['ID'].str.split('_').str[0]
df_pos['answer'] = df_pos['ID'].str.split('_').str[1]
df_pos['year'] = 2016
df_pos = df_pos.drop(columns='ID')

# now save 
df_pos.to_csv("data/anes_pos.csv", index=False)
df_long.to_csv("data/anes_data.csv", index=False)

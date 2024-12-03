import pyreadstat
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from sklearn.decomposition import PCA

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

# add question interpretation 
code_answers = [
    ('gay', 1, 'marry'),
    ('gay', 2, 'union'),
    ('gay', 3, 'no'),
    ('imm', 1, 'deport'),
    ('imm', 2, 'restrict'),
    ('imm', 3, 'stay'),
    ('imm', 4, 'citizen'),
    ('temp', 1, 'do more'),
    ('temp', 2, 'do less'),
    ('temp', 3, 'right'),
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

# recode such that they follow reasonable likert
recode_map = {
    ('temp', 'do less'): 3,
    ('temp', 'right'): 2,
    ('tax', 'oppose'): 3,
    ('tax', 'neither'): 2,
    ('econ', 'worse'): 3,
    ('econ', 'same'): 2
}
def recode_values(row): 
    key = (row['question'], row['answer'])
    return recode_map[key] if key in recode_map else row['value']

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
nx.draw_networkx_nodes(G, new_pos, node_size=200, node_color="lightblue")
nx.draw_networkx_edges(G, new_pos, width=edge_weights, alpha=0.7)

# Draw labels
labels = {node: node for node in G.nodes}
nx.draw_networkx_labels(G, new_pos, labels, font_size=10, font_color="black")

# Show the graph
plt.title("ResIN on ANES", fontsize=16)
plt.axis("off")
plt.savefig("fig/correlation_graph.png")

# -------------- save data ----------------- #

def pos_to_df(pos):
    df_pos = pd.DataFrame(pos).T.reset_index()
    df_pos.columns = ['ID', 'xvalue', 'yvalue']
    df_pos['question'] = df_pos['ID'].str.split('_').str[0]
    df_pos['answer'] = df_pos['ID'].str.split('_').str[1]
    df_pos['year'] = 2016
    df_pos = df_pos.drop(columns='ID')
    return df_pos

df_pos_resin = pos_to_df(new_pos)
df_pos_basic = pos_to_df(pos)

# now save 
df_pos_resin.to_csv("data/anes_pos_resin.csv", index=False)
df_pos_basic.to_csv("data/anes_pos_basic.csv", index=False)
df_long.to_csv("data/anes_data.csv", index=False)

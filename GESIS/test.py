import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np

# load GESIS data
data = pd.read_stata("data/data/stata/ZA5665_a1_v54-0-0.dta", convert_categoricals=False)

# begin to find variables; 
clch_waves= ["bczd035a", "cczd032a", "dczd032a", "eczd032a",  "fczd032a", "hczd031a", "ibzd031a", "jbzd031a", "kbzd030a"]
d_cl = data[clch_waves]

# remove nan. 
nas = [-11, -22, -33, -44, -55, -66, -77, -88, -99, -111]
d_cl = d_cl.replace(nas, np.nan)

# the scale changed 
# so only take the ones that have 11 as max.
max_val = d_cl.max().reset_index(name='max') # has to be 11 I guess.
valid_cols = max_val[max_val['max']==11]['index'].tolist()
d_cl = d_cl[valid_cols]

# remove the ones that have 7 as max 
d_cl.isna().sum() # should always grow; and does.
d_cl = d_cl.dropna()

# 1: climate change not serious at all
# 11: extremely serious 
dates = []
for col in d_cl.columns:
    id = col[:2]
    data[id+'zp205a'] = pd.to_datetime(data[id+'zp205a'], errors='coerce')
    valid_dates = data[id+'zp205a'].dropna()
    mean_date = valid_dates.mean().strftime('%Y')
    dates.append(mean_date)
colnames = ['clch-'+date for date in dates]

d_cl = d_cl.rename(columns=dict(zip(d_cl.columns, colnames)))

# okay now we can make the transition plot I guess
waves = d_cl.columns
transitions = []

for i in range(len(waves) - 1):
    source_wave = waves[i]
    target_wave = waves[i + 1]
    counts = d_cl.groupby([source_wave, target_wave]).size().reset_index(name='count')
    counts['source'] = counts[source_wave].apply(lambda x: f"{source_wave} - Level {x}")
    counts['target'] = counts[target_wave].apply(lambda x: f"{target_wave} - Level {x}")
    transitions.append(counts[['source', 'target', 'count']])

# Combine transitions
all_transitions = pd.concat(transitions)

import plotly.graph_objects as go
nodes = pd.unique(all_transitions[['source', 'target']].values.ravel())
node_indices = {node: i for i, node in enumerate(nodes)}

# Map nodes to indices
all_transitions['source_idx'] = all_transitions['source'].map(node_indices)
all_transitions['target_idx'] = all_transitions['target'].map(node_indices)

# Sankey data
sankey_data = {
    'node': {
        'label': nodes
    },
    'link': {
        'source': all_transitions['source_idx'].tolist(),
        'target': all_transitions['target_idx'].tolist(),
        'value': all_transitions['count'].tolist()
    }
}

# Plot Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        #label=sankey_data['node']['label']
    ),
    link=dict(
        source=sankey_data['link']['source'],
        target=sankey_data['link']['target'],
        value=sankey_data['link']['value']
    )
)])

fig.update_layout(title_text="Sankey Diagram of Panel Data", font_size=10)
fig.show()

### path dependency ###
import seaborn as sns
target = 9
d_sub = d_cl[d_cl['clch-2015']==target]
d_sub = d_sub.astype(int)
d_sub['baseline'] = d_sub['clch-2014'] # baseline year

df_long = d_sub.melt(id_vars=["baseline"], 
                  value_vars=[col for col in d_sub.columns if col.startswith("clch-")],
                  var_name="year", 
                  value_name="value")

# Extract the year from the "year" column (remove the "clch-" prefix)
df_long["year"] = df_long["year"].str.replace("clch-", "", regex=False)

fig, ax = plt.subplots(figsize=(5, 3))
sns.lineplot(x="year", y="value", hue="baseline", data=df_long, legend=False)
plt.suptitle('Path Dependency')
plt.tight_layout()
plt.savefig('fig/path_dependency.png')

### quantify path dependenecy ###
# mutual information
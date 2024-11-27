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

# try on a subset; 
target = 9
d_sub = d_cl[d_cl['clch-2015']==target]
counts = d_sub['clch-2014'].value_counts().reset_index()
result = d_sub.groupby('clch-2014')[['clch-2016', 'clch-2017', 'clch-2018']].mean().reset_index()
result_melt = result.melt(id_vars='clch-2014', var_name='year', value_name='mean')
result_merge = pd.merge(result_melt, counts, on = 'clch-2014', how = 'inner')

# try to reformat;
baseline_year = result_merge[['clch-2014', 'count']].drop_duplicates()
baseline_year['year'] = 'clch-2014'
baseline_year['mean'] = baseline_year['clch-2014']

# merge again
result_merge = pd.concat([result_merge, baseline_year])
result_merge['year'] = result_merge['year'].apply(lambda x: x.split('-')[1])
result_merge['year'] = result_merge['year'].astype(int)
result_merge = result_merge.rename(columns={'clch-2014': 'group'})
result_merge['group'] = result_merge['group'].astype(int)

# add 2015
missing_year = result_merge[['group', 'count']].drop_duplicates()
missing_year['year'] = 2015
missing_year['mean'] = target
result_merge = pd.concat([result_merge, missing_year])

# plot this;
import seaborn as sns 
import matplotlib.ticker as ticker

sns.set(style="whitegrid")
plt.figure(figsize=(12, 6))
sns.lineplot(x='year', y='mean', hue='group', data=result_merge)
plt.title(f"Transition from {target} in 2015")

# Ensure the x-axis displays integers only
plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(1))  # Set ticks at every year (integer)
plt.gca().xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))  # Format ticks as integers

plt.savefig('fig/path_dependency.png')

# is there a way to quantify this? 
## ding ding ##
from sklearn.feature_selection import mutual_info_regression
from sklearn.preprocessing import StandardScaler

# Standardize the data (optional)
scaler = StandardScaler()
X_conditional = scaler.fit_transform(d_cl[['clch-2015']])
X_all = scaler.fit_transform(d_cl[['clch-2015', 'clch-2014']])
Y = d_cl['clch-2016']

# Mutual information
mi_conditional = mutual_info_regression(X_conditional, Y)
mi_all = mutual_info_regression(X_all, Y)

print(f"Mutual Information (with 2015 only): {mi_conditional}")
print(f"Mutual Information (with 2015 and 2014): {mi_all}")

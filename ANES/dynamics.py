import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import pickle 

# read stuff 
df = pd.read_csv('anes_data.csv')
df = df.dropna()

with open('pos.pkl', 'rb') as handle:
    pos = pickle.load(handle)
with open('new_pos.pkl', 'rb') as handle:
    new_pos = pickle.load(handle)

# Calculate pairwise distances
def calculate_distances(pos, new_pos): 
    data = []
    # loop over all pairs of nodes
    for node_x, node_y in combinations(pos.keys(), 2): 
        euclid_distance = np.linalg.norm(np.array(pos[node_x]) - np.array(pos[node_y]))
        x_distance = abs(new_pos[node_x][0] - new_pos[node_y][0])

        # overall variable
        variable = node_x.split('2016')[0]
        item_1 = node_x.split('_')[1]
        item_2 = node_y.split('_')[1]
        
        # Append results to the list
        data.append([variable, item_1, item_2, euclid_distance, x_distance])
        
        # Maybe there is a better way to organize this
        data.append([variable, item_2, item_1, euclid_distance, x_distance])

    # add self-loops
    for node in pos.keys():
        variable = node.split('2016')[0]
        item = node.split('_')[1]
        
        # by definition distance is 0
        data.append([variable, item, item, 0, 0])

    # gather data 
    distance_df = pd.DataFrame(data, columns=['variable', 'item_2016', 'item_2020', 'euclid_dist_2016', 'x_dist_2016'])
    return distance_df


# these are basically the same
# is that also what they are arguing?
distance_df = calculate_distances(pos, new_pos)
distance_df # good

# get actual transitions 
abort_counts = df[['abort2016', 'abort2020']].value_counts().to_frame().reset_index()
abort_counts['variable'] = 'abort'
abort_counts = abort_counts.rename(columns={
    'abort2016': 'item_2016',
    'abort2020': 'item_2020',
    'count': 'n_transition'
})

merge = pd.merge(distance_df, abort_counts, on=['variable', 'item_2016', 'item_2020'], how='inner')
merge.sort_values(['item_2016', 'n_transition'], ascending=[True, False])

# calculate base rates 
def get_baserate(df):
    melt = df.melt(var_name="variable", value_name="item")
    melt = melt.groupby(["variable", "item"]).size().reset_index(name="count")
    melt['year'] = melt['variable'].str.extract(r'(\d{4})')
    melt['variable'] = melt['variable'].str.extract(r'([a-zA-Z]+)')
    return melt

baserate = get_baserate(df)

##### ----------------- SANKEY DIAGRAM ---------------------- #####
import plotly.graph_objects as go

variable = 'abort'
items = ['choice', 'need', 'exceptions', 'never']
labels = [f"{item}_2016" for item in items] + [f"{item}_2020" for item in items]
colors = ["#636EFA", "#EF553B", "#00CC96", "#AB63FA"]  # One color per item
node_colors = colors + colors  # Duplicate colors for Wave 1 and Wave 2

# Map source and target to indices in the labels list
source = merge['item_2016'].map(lambda x: labels.index(f"{x}_2016")).tolist()
target = merge['item_2020'].map(lambda x: labels.index(f"{x}_2020")).tolist()
value = merge['n_transition'].tolist()

# Base rates
br_2016 = baserate[(baserate['variable'] == variable) & (baserate['year'] == '2016')].sort_values('item')
br_2016 = br_2016.set_index('item')['count'].to_dict()
br_2020 = baserate[(baserate['variable'] == variable) & (baserate['year'] == '2020')].sort_values('item')
br_2020 = br_2020.set_index('item')['count'].to_dict()

# Node thickness to account for base rates
node_thickness = [br_2016[item] for item in items] + [br_2020[item] for item in items]

# Create the Sankey diagram
fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=labels,
        color=node_colors,
    ),
    link=dict(
        source=source,  # Source indices
        target=target,  # Target indices
        value=value,    # Transition counts (flows)
    )
))

# Add title and display the plot
fig.update_layout(title_text="Sankey Diagram with Base Rates", font_size=10)
fig.show()

#### ----------------- network plot ---------------------- #####
variable = 'abort' # still just abort

# total number of observations
base_2016 = baserate[(baserate['variable'] == variable) & (baserate['year'] == '2016')].sort_values('item')
base_2016 = base_2016.rename(columns={
    'count': 'n_2016'
})
base_2016 = base_2016.drop(columns=['year'])
base_2016 = base_2016.rename(columns={"item": "item_2016"})

merge_abort = pd.merge(base_2016, merge, on=['variable', 'item_2016'], how='inner')
merge_abort['pct_transition'] = merge_abort['n_transition'] / merge_abort['n_2016']

# add edges 
G = nx.from_pandas_edgelist(
    merge_abort, 
    'item_2016', 
    'item_2020', 
    edge_attr=['n_transition', 'pct_transition'],
    create_using=nx.DiGraph)

# add nodes
base_2016 = baserate[(baserate['variable'] == variable) & (baserate['year'] == '2016')].sort_values('item')
dict_2016 = base_2016.set_index('item')['count'].to_dict()
nx.set_node_attributes(G, dict_2016, name="count_2016")

# get a subset of the positions 
pos_subset = {k: new_pos[k] for k in new_pos.keys() if variable in k} 
pos_subset = {k.split('_')[1]: v for k, v in pos_subset.items()}

# edge labels
edge_width = []
edge_labels = {}
for x, y, attr in G.edges(data = True): 
    weight = attr['pct_transition']
    edge_width.append(weight)
    edge_labels[(x, y)] = round(weight, 2)

# node labels
node_labels = {}
for i in G.nodes(): 
    node_labels[i] = i

# initialize
x = nx.draw_networkx_edge_labels(
    G, 
    pos_subset, 
    edge_labels = [])

# make it cool
node_width = [G.nodes[n]['count_2016'] for n in G.nodes()]
node_width = [x*2 for x in node_width]

plt.axis('off')
nx.draw_networkx_nodes(
    G, 
    pos_subset,
    node_size = node_width, #1500,
    linewidths = 2,
    edgecolors = 'k',
    node_color = 'white'
    )
nx.draw_networkx_edges(
    G,
    pos_subset,
    width = [x*5 for x in edge_width],
    connectionstyle = "arc3,rad=0.2",
    node_size = [x*2 for x in node_width] #2000,
)
nx.draw_networkx_labels(
    G,
    pos_subset,
    node_labels,
    font_size = 9,
)
plt.show(); 

'''
Okay, really hard to show properly with self-loops.
But we can see it indirectly by less out-edges. 
i.e., "choice" has ~80% self-loop so only ~20% out-edges.
'''

#### ----------------- metrics ---------------------- #####
'''
Hypotheses / Frameworks: 
Some "stability" might be captured simply in base rates.
These are a little tricky, because we could just have sampling bias.
However, some positions might just be more stable. 
One thing to check is just whether the stability scales with percent.
(i.e., percent there in 2016 vs. percent self-transition).

Another thing that might be happening is that transitions happen
relative to distances in the landscape; this could basically be a 
"random fluctuations" model. This would imply that if you are close to
other options you would have a higher chance of transitioning 
(both specifically to these, and also in general vs. staying).
'''

# hypothesis 1: proportional to base rate # 
variable = 'abort' # still just abort

# total number of observations
base_2016 = baserate[(baserate['variable'] == variable) & (baserate['year'] == '2016')].sort_values('item')
base_2016 = base_2016.rename(columns={
    'count': 'n_2016'
})
base_2016 = base_2016.drop(columns=['year'])

# self-transitions
self_transitions = merge[merge['item_2016'] == merge['item_2020']]
self_transitions = self_transitions[['variable', 'item_2016', 'n_transition']]
self_transitions = self_transitions.rename(
    columns = {"item_2016": "item"} 
)

merge_abort = pd.merge(base_2016, self_transitions, on=['variable', 'item'], how='inner')
merge_abort['prop_self'] = merge_abort['n_transition'] / merge_abort['n_2016']

# plot this 
plt.figure(figsize=(10, 5))
plt.scatter(merge_abort['n_2016'], merge_abort['prop_self'])
plt.xlabel('Base Rate in 2016')
plt.ylabel('Proportion of Self-Transitions')
plt.title('')
plt.show()

# try to do this in a smarter way # 

'''
NOTES: 
We really need a THIRD wave because what would be really interesting is the following.
We are getting quite a lot of movement here; many positions >50% change from 2016 to 2020.
However, it is not clear whether we are capturing fluctuations, or lasting movement.
If we had (at least) a third wave, we could see something here maybe.
'''
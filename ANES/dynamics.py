import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations
import pickle 
import matplotlib.colors as mcolors

# ----------------- DATA ---------------------- #
df = pd.read_csv('anes_data.csv')
df = df.dropna()

with open('pos.pkl', 'rb') as handle:
    pos = pickle.load(handle)
with open('new_pos.pkl', 'rb') as handle:
    new_pos = pickle.load(handle)

# ----------------- FUNCTIONS ---------------------- #
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

def get_transitions(df, variable): 
    transitions = df[[f'{variable}2016', f'{variable}2020']].value_counts().to_frame().reset_index()
    transitions['variable'] = variable
    transitions = transitions.rename(columns={
        f'{variable}2016': 'item_2016',
        f'{variable}2020': 'item_2020',
        'count': 'n_transition'
    })
    return transitions

# calculate base rates 
def get_baserate(df):
    melt = df.melt(var_name="variable", value_name="item")
    melt = melt.groupby(["variable", "item"]).size().reset_index(name="count")
    melt['year'] = melt['variable'].str.extract(r'(\d{4})')
    melt['variable'] = melt['variable'].str.extract(r'([a-zA-Z]+)')
    return melt

# -------- calculate distances -------- #
distance_df = calculate_distances(pos, new_pos)

# -------- calculate transitions -------- #
transition_abort = get_transitions(df, 'abort')
transition_gay = get_transitions(df, 'gay')
transition_imm = get_transitions(df, 'imm')
transition_temp = get_transitions(df, 'temp')

transition_df = pd.concat([
    transition_abort,
    transition_gay,
    transition_imm,
    transition_temp
])

# -------- merge dataframes -------- #
merged_df = pd.merge(distance_df, transition_df, on=['variable', 'item_2016', 'item_2020'], how='inner')

# -------- calculate baserate -------- #
baserate = get_baserate(df)

##### ----------------- SANKEY DIAGRAM ---------------------- #####

import plotly.graph_objects as go
import plotly.io as pio

# important to not that we do not need to provide the base rate here
# the transitions implicitly capture this. 
def sankey_diagram(
    df_transitions: pd.DataFrame, 
    variable: str, 
    items=[], # Optional order of items
    save_path=None  # Optional save path
    ): 
    
    df_subset = df_transitions[df_transitions['variable']==variable]
    
    # if not provided specifically obtain 
    if not items: 
        items = df_subset['item_2016'].unique().tolist()
    
    labels = [f"{item}_2016" for item in items] + [f"{item}_2020" for item in items]
    
    # get colors (can be improved)
    n_items = len(items)
    tab_colors = [mcolors.to_hex(color) for color in mcolors.TABLEAU_COLORS]
    node_colors = tab_colors[:n_items]
    node_colors = node_colors + node_colors
    
    # map source and target to indices in the labels list
    source = df_subset['item_2016'].map(lambda x: labels.index(f"{x}_2016")).tolist()
    target = df_subset['item_2020'].map(lambda x: labels.index(f"{x}_2020")).tolist()
    value = df_subset['n_transition'].tolist()
    
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
    fig.update_layout(title_text=f"Sankey Diagram for {variable}", font_size=10)
    fig.show()
    
    # Save the figure if a save path is provided
    if save_path:
        pio.write_image(fig, save_path, format="png")
        print(f"Sankey diagram saved as {save_path}")

# generally these all drift slightly left it seems. 
sankey_diagram(
    df_transitions = merged_df, 
    variable = 'abort',
    items = ['choice', 'need', 'exceptions', 'never'],
    save_path = 'fig/sankey_abort.png') # middle unstable

sankey_diagram(
    df_transitions = merged_df, 
    variable = 'gay',
    items = ['marry', 'union', 'no'],
    save_path = 'fig/sankey_gay.png') # middle unstable

# something with ordering that does not work here
# the list thing is not really doing anything.
sankey_diagram(
    df_transitions = merged_df, 
    variable = 'imm',
    items = ['citizen', 'stay', 'restrict', 'deport'],
    save_path = 'fig/sankey_imm.png') # deport unstable

sankey_diagram(
    df_transitions = merged_df, 
    variable = 'temp',
    items = ['more', 'right', 'less'],
    save_path = 'fig/sankey_temp.png') # all unstable (but clear direction)

#### ----------------- network plot ---------------------- #####

# okay so now make this nice.
def network_plot(df_baserate: pd.DataFrame,
                 df_transitions: pd.DataFrame,
                 variable: str,
                 pos: dict,
                 save_path=None):

    # baserate 2016
    base_2016 = df_baserate[(df_baserate['variable']==variable) & (df_baserate['year']=='2016')].sort_values('item')
    base_2016 = base_2016.rename(columns={
        'count': 'n_2016'
    })
    base_2016 = base_2016.drop(columns=['year'])
    base_2016 = base_2016.rename(columns={"item": "item_2016"})
    
    # merge with transitions
    df_merged = pd.merge(base_2016, df_transitions, on=['variable', 'item_2016'], how='inner')
    df_merged['pct_transition'] = df_merged['n_transition'] / df_merged['n_2016']
    
    # add edges
    G = nx.from_pandas_edgelist(
        df_merged, 
        'item_2016', 
        'item_2020', 
        edge_attr=['n_transition', 'pct_transition'],
        create_using=nx.DiGraph)
    
    # add nodes
    dict_2016 = base_2016.set_index('item_2016')['n_2016'].to_dict()
    nx.set_node_attributes(G, dict_2016, name="count_2016")
    
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
    
    # fix position
    pos = {k: pos[k] for k in pos.keys() if variable in k} 
    pos = {k.split('_')[1]: v for k, v in pos.items()}

    # initialize
    x = nx.draw_networkx_edge_labels(
        G, 
        pos, 
        edge_labels = [])
    
    # make it cool
    node_width = [G.nodes[n]['count_2016'] for n in G.nodes()]
    node_width = [x*2 for x in node_width]
    
    plt.axis('off')
    nx.draw_networkx_nodes(
        G, 
        pos,
        node_size = node_width, #1500,
        linewidths = 2,
        edgecolors = 'k',
        node_color = 'white'
        )
    nx.draw_networkx_edges(
        G,
        pos,
        width = [x*5 for x in edge_width],
        connectionstyle = "arc3,rad=0.2",
        node_size = [x*2 for x in node_width] #2000,
    )
    nx.draw_networkx_labels(
        G,
        pos,
        node_labels,
        font_size = 9,
    )
    if save_path: 
        plt.savefig(save_path)
    else: 
        plt.show();
    plt.close()
    
network_plot(
    df_baserate = baserate,
    df_transitions = merged_df,
    variable = 'abort',
    pos = new_pos,
    save_path = 'fig/network_abort.png'
)

# interesting that union goes much more to marry
# than to "no" even though it is closer to "no".
# "marry" is really stable.
network_plot(
    df_baserate = baserate,
    df_transitions = merged_df,
    variable = 'gay',
    pos = new_pos,
    save_path = 'fig/network_gay.png'
)

# again the liberal position is the stable attractor.
network_plot(
    df_baserate = baserate,
    df_transitions = merged_df,
    variable = 'imm',
    pos = new_pos,
    save_path = 'fig/network_imm.png'
)

# main transition through moderate towards "more".
# well not really "through" because we only have 
# 2 observations (but directionality). 
network_plot(
    df_baserate = baserate,
    df_transitions = merged_df,
    variable = 'temp',
    pos = new_pos,
    save_path = 'fig/network_temp.png'
)


'''
Really hard to show properly with self-loops.
But we can see it indirectly by less out-edges. 
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

# hypotheses: 
## 1. random transitions 
## 2. random transitions by base-rate 
## 3. non-random transitions by base-rate
## 4. non-random transitions by distance 
## 5. non-random transitions by distance + base-rate

# 1. transition by base rate # 
# but this is really tricky unless we have a balanced sample.
# do we have a balanced sample?
# we really should, but seems really liberal skewed. 

# hypothesis 1: proportional to base rate # 
import seaborn as sns 

# total number of observations
base_2016 = baserate[baserate['year'] == '2016']
base_2016 = base_2016.rename(columns={'count': 'n_2016'})

# self-transitions
self_transitions = merged_df[merged_df['item_2016'] == merged_df['item_2020']]
self_transitions = self_transitions[['variable', 'item_2016', 'n_transition']]
self_transitions = self_transitions.rename(
    columns = {"item_2016": "item"} 
)

baserate_model = pd.merge(base_2016, self_transitions, on=['variable', 'item'], how='inner')
baserate_model['prop_self'] = baserate_model['n_transition'] / baserate_model['n_2016']

# Create the scatter plot with seaborn
plt.figure(figsize=(6, 4))
sns.scatterplot(
    data=baserate_model,
    x='n_2016',
    y='prop_self',
    hue='variable',  # Color points by the 'class' column
    palette='tab10'  # Use a predefined colormap (optional)
)

# Add labels and title
plt.xlabel('Base Rate in 2016')
plt.ylabel('Proportion of Self-Transitions')
plt.title('Scatter Plot Colored by Class')

# Show the plot
plt.legend(loc='upper left')
plt.tight_layout()
plt.savefig('fig/baserate_model.png')
plt.close()

'''
Does seem to be some signal here.
Definitely not perfect as well.
'''


# transition by distance # 
#variable = 'gay'
#df = merged_df[merged_df['variable'] == variable]
#base_temp = baserate[baserate['variable'] == variable]
base_temp = baserate[baserate['year'] == '2016']
base_temp = base_temp.rename(columns={'count': 'n_2016',
                                      'item': 'item_2016'})
base_temp = base_temp.drop(columns=['year'])
dfx = pd.merge(base_temp, merged_df, on=['variable', 'item_2016'], how='inner')
dfx['p_transition'] = dfx['n_transition'] / dfx['n_2016']

colors = {
    'abort': 'tab:blue',
    'gay': 'tab:orange',
    'imm': 'tab:green',
    'temp': 'tab:red'
} 

variable_item_combinations = dfx.groupby(['variable', 'item_2016']).size().reset_index(name='count')
variable_item_combinations = variable_item_combinations.to_dict(orient='records')
import matplotlib.pyplot as plt

# Keep track of variables already added to the legend
added_to_legend = set()

for d in variable_item_combinations:
    # Extract dictionary elements
    variable = d.get('variable')
    item = d.get('item_2016')
    
    # Filter and sort the data
    df_subset = dfx[(dfx['variable'] == variable) & (dfx['item_2016'] == item)]
    df_subset = df_subset.sort_values('euclid_dist_2016')
    color = colors[variable]
    
    # Scatter plot
    plt.scatter(df_subset['euclid_dist_2016'], df_subset['p_transition'], color=color)

    # Line plot
    plt.plot(df_subset['euclid_dist_2016'], df_subset['p_transition'], color=color)
    
    # Add variable to the legend only once
    if variable not in added_to_legend:
        plt.scatter([], [], label=variable, color=color)  # Add an invisible scatter point for the legend
        added_to_legend.add(variable)

# Add labels and legend
plt.xlabel('Distance (network) in 2016')
plt.ylabel('p(transition)')
plt.legend(title='Variables')
plt.savefig('fig/distance_transition.png')
    
'''
NB: 
1. cannot use correlations directly because no correlation for items within variables
2. questions with fewer levels will have lower mean and obscure plot (can be normalized)
'''

# transition by distance - normalizing for size # 
# is this gravity?
dfx

# could also be a kind of gravity model maybe?

'''
NOTES: 
We really need a THIRD wave because what would be really interesting is the following.
We are getting quite a lot of movement here; many positions >50% change from 2016 to 2020.
However, it is not clear whether we are capturing fluctuations, or lasting movement.
If we had (at least) a third wave, we could see something here maybe.
'''
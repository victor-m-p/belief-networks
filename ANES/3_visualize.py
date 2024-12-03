import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations, product 
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import plotly.io as pio

# ----------------- DATA ---------------------- #

df = pd.read_csv('data/anes_data.csv')
pos = pd.read_csv('data/anes_pos_resin.csv')

# ----------------- calculate distances ---------------------- #
pos['index'] = pos.index
distance_data = []
for node_x, node_y in product(pos['index'], repeat=2):
    node_x_val = pos.loc[node_x]['xvalue']
    node_y_val = pos.loc[node_y]['xvalue']
    x_distance = abs(node_x_val - node_y_val)
    distance_data.append([node_x, node_y, x_distance])
    
# naming here is just to facilitate merges 
df_distance = pd.DataFrame(distance_data, columns=['index', 'idx', 'abs_x_dist'])
pos_tmp = pos[['question', 'answer', 'index']]
df_distance = df_distance.merge(pos_tmp, on = 'index', how='inner')
pos_tmp = pos_tmp.rename(columns={'index': 'idx'})
df_distance = df_distance.merge(pos_tmp, on=['idx', 'question'], how='inner')
df_distance = df_distance.rename(columns={
    'answer_x': 'answer',
    'answer_y': 'lag_answer'
})
df_distance = df_distance.drop(columns={'index', 'idx'})

# ----------------- calculate transitions ---------------------- #
df_transitions = df.sort_values(by=['ID', 'question', 'year'])
df_transitions['lag_answer'] = df_transitions.groupby(['ID', 'question'])['answer'].shift(1)
df_transitions['lag_year'] = df_transitions.groupby(['ID', 'question'])['year'].shift(1)
df_transitions = df_transitions.dropna(subset=['lag_answer', 'lag_year']).reset_index(drop=True)
df_transitions['lag_year'] = df_transitions['lag_year'].astype(int)
df_transitions = df_transitions.groupby(['question', 'answer', 'lag_answer']).size().reset_index(name='n_transitions')

# -------- merge dataframes -------- #
merged_df = pd.merge(df_distance, df_transitions, on=['question', 'answer', 'lag_answer'], how='inner')

# -------- calculate baserate -------- #
df_baserate = df[df['year']==2016]
df_baserate = df_baserate.groupby(['question', 'answer']).size().reset_index(name='count')

##### ----------------- SANKEY DIAGRAM ---------------------- #####

# important to not that we do not need to provide the base rate here
# the transitions implicitly capture this. 
def sankey_diagram(
    df_transitions: pd.DataFrame, 
    variable: str, 
    items=[], # Optional order of items
    save_path=None  # Optional save path
    ): 
    
    df_subset = df_transitions[df_transitions['question']==variable]
    
    # if not provided specifically obtain 
    if not items: 
        items = df_subset['answer'].unique().tolist()
    
    labels = [f"lag_{item}" for item in items] + [f"{item}" for item in items]
    
    # get colors (can be improved)
    n_items = len(items)
    tab_colors = [mcolors.to_hex(color) for color in mcolors.TABLEAU_COLORS]
    node_colors = tab_colors[:n_items]
    node_colors = node_colors + node_colors
    
    # map source and target to indices in the labels list
    source = df_subset['lag_answer'].map(lambda x: labels.index(f"lag_{x}")).tolist()
    target = df_subset['answer'].map(lambda x: labels.index(f"{x}")).tolist()
    value = df_subset['n_transitions'].tolist()
    
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
    items = ['do more', 'right', 'do less'],
    save_path = 'fig/sankey_temp.png') # all unstable (but clear direction)

# really does not work well; come back and fix this. 
sankey_diagram(
    df_transitions = merged_df,
    variable = 'econ',
    items = ['better', 'same', 'worse'],
    save_path = 'fig/sankey_econ.png'
)

#### ----------------- network plot ---------------------- #####

def network_plot(df_baserate: pd.DataFrame,
                 df_transitions: pd.DataFrame,
                 variable: str,
                 pos: dict,
                 save_path=None):

    # subset 
    df_transitions = df_transitions[df_transitions['question']==variable]
    df_baserate = df_baserate[df_baserate['question']==variable]
    df_baserate = df_baserate.rename(columns={'answer': 'lag_answer'})
    pos = pos[pos['question']==variable]

    # get pct transitions
    df_merged = df_transitions.merge(df_baserate, on = ['question', 'lag_answer'], how = 'inner')
    df_merged['pct_transitions'] = (df_merged['n_transitions'] / df_merged['count'])*100

    # remove self-loops
    df_merged = df_merged[df_merged['answer'] != df_merged['lag_answer']]

    # initialize 
    G = nx.from_pandas_edgelist(
        df_merged, 
        'lag_answer', 
        'answer', 
        edge_attr=['pct_transitions'],
        create_using=nx.DiGraph)

    # add node weight
    node_attr = df_baserate.set_index('lag_answer')['count'].to_dict()
    nx.set_node_attributes(G, node_attr, name='count')

    # add edge weight
    edge_width = []
    edge_labels = {}
    for x, y, attr in G.edges(data=True): 
        weight = attr['pct_transitions']
        edge_width.append(weight)
        edge_labels[(x, y)] = round(weight, 2)

    # node labels 
    node_labels = {i: i for i in G.nodes()}

    # positions 
    pos = {a: (x, y) for a, x, y in zip(pos['answer'], pos['xvalue'], pos['yvalue'])}

    # make it cool
    node_width = [G.nodes[n]['count'] for n in G.nodes()]
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
        width = [x/20 for x in edge_width],
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

# now do the network plots ... # 
questions = df_baserate['question'].unique()
for q in questions: 
    network_plot(
        df_baserate = df_baserate,
        df_transitions = df_transitions,
        variable = q,
        pos = pos,
        save_path = f'fig/network_{q}.png'
    )


# below metrics are not so important I think # 

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
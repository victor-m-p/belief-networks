import pandas as pd 

def is_numeric_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

# data
d = pd.read_csv('data/data_project_1044868_2025_02_11.csv', sep=';')

# just start with one person 
d = d[d['lfdn'] == 22].reset_index()
focal_topic = 'animal products'

consumption_coding = {
    1: f'Only eat {focal_topic}',
    2: f'Daily {focal_topic}',
    3: f'Limited {focal_topic}',
    4: 'Vegeratian',
    5: 'Vegan',
}

# Initialize master node/edge containers
nodes = {}
edges = []

# 1) Focal node
nodes['focal'] = {
    'type': 'belief',
    'level': 0,
    'domain': 'consumption of animal products',
    'likert': d['v_1269'][0],
    'likert_code': consumption_coding[d['v_1269'][0]],
    'brainstorm': d['v_722'][0],
    'production': d['v_1348'][0],
    'impact': d['v_1349'][0],
    'consumption': d['v_723'][0],
}

# We'll store a dict that maps "con_1" -> "b_1", "pro_1" -> "b_6", etc.
n_beliefs = 10

belief_free_pro_idx = [f"v_{x+1001}" for x in range(int(n_beliefs/2))]
belief_free_con_idx = [f"v_{x+1012}" for x in range(int(n_beliefs/2))]
belief_free_idx = belief_free_pro_idx + belief_free_con_idx

belief_importance_pro_abs_idx = [f"v_{x+1017}" for x in range(int(n_beliefs/2))]
belief_importance_con_abs_idx = [f"v_{x+1072}" for x in range(int(n_beliefs/2))]
belief_importance_abs_idx = belief_importance_pro_abs_idx + belief_importance_con_abs_idx

belief_importance_pro_rel_idx = [f"v_{x+1022}" for x in range(int(n_beliefs/2))]
belief_importance_con_rel_idx = [f"v_{x+1077}" for x in range(int(n_beliefs/2))]
belief_importance_rel_idx = belief_importance_pro_rel_idx + belief_importance_con_rel_idx

belief_attention_idx = [f"v_{x+1338}" for x in range(n_beliefs)]

# Now let's build the first-level beliefs properly
first_level_ids = []  # We'll keep track of which IDs we create, in order.

node_counter = 0
for i in range(n_beliefs):
    node_counter += 1
    # direction is 'con' if i < 5, else 'pro'
    direction = "con" if i < 5 else "pro"
    
    # Check if there's a valid string for the free text
    free_val = d[belief_free_idx[i]][0]
    if isinstance(free_val, str) and not is_numeric_string(free_val):
        b_id = f"b_{node_counter}"   # "b_1", "b_2", etc.
        
        # Build the node
        nodes[b_id] = {
            "type": "belief",
            "level": 1,
            "direction": direction,
            "belief_text": free_val,
            "abs_importance": d[belief_importance_abs_idx[i]][0],
            "rel_importance": d[belief_importance_rel_idx[i]][0],
            "attention": d[belief_attention_idx[i]][0],
        }
        
        # Keep track of it (for edges or later reference)
        first_level_ids.append(b_id)

# Now create edges from the focal node to each first-level belief
for b_id in first_level_ids:
    edges.append({
        "source": "focal",
        "target": b_id,
        "type": "focal_to_belief"
    })

        
### secondary beliefs ### 
secondary_order = ['v_717', 'v_718', 'v_719']
secondary_beliefs = [f'{x+11}' for x in range(n_beliefs)]
secondary_labels = [f'b_{x+1}' for x in range(n_beliefs)]

secondary_belief_dict = {}
for i, label in zip(secondary_beliefs, secondary_labels): 
    temporary_list = []
    for j in secondary_order: 
        if isinstance(d[f'{j}_{i}'][0], str) and not is_numeric_string(d[f'{j}_{i}'][0]): 
            temporary_list.append(d[f'{j}_{i}'][0])
    if temporary_list:
        secondary_belief_dict[label] = temporary_list

# add secondary beliefs to nodes
# add secondary beliefs to edges
for parent_b_id, sec_belief_list in secondary_belief_dict.items():
    for i, sec_text in enumerate(sec_belief_list, start=1):
        # Construct a new node ID like "b_1_1", "b_1_2", etc.
        new_b_id = f"{parent_b_id}_{i}"
        
        # Create the node
        nodes[new_b_id] = {
            "type": "belief",
            "level": 2,               # or "second_level"
            "belief_text": sec_text,
            "parent": parent_b_id
        }

        # Create an edge from the parent (first-level) belief to this new second-level node
        edges.append({
            "source": new_b_id,
            "target": parent_b_id,
            "type": "personal_belief_connection"
        })


### social contacts ### 
n_social_max = 8
social_labels = [(f"v_{x+901}", f"v_{x+927}", f"v_{x+1285}", f"s_{x+1}") for x in range(n_social_max)]
social_nodes = {}
for col_name, col_importance, col_focal, node_type in social_labels: 
    if isinstance(d[col_name][0], str) and not is_numeric_string(d[col_name][0]): 
        social_nodes[node_type] = {
            "name": d[col_name][0],
            "rating": d[col_importance][0],
            "focal": d[col_focal][0]} 
        nodes[node_type] = {
            "type": "social_belief",
            "level": 0,
            "value": d[col_focal][0],
            "social_name": d[col_name][0],
            "social_rating": d[col_importance][0],
        }
        edges.append({
            "source": node_type,
            "target": "focal",
            "type": "social_to_focal",
        })

### social --> other ### 
# must be a smarter way to do this 
potential_beliefs = [f"b_{x+1}" for x in range(10)]
actual_beliefs = [x for x in nodes.keys() if nodes[x]['level'] == 1]
social_belief_idx = [f"v_{x+1358}" for x in range(n_beliefs)]
indices = [potential_beliefs.index(b) for b in actual_beliefs]
social_belief_idx = [social_belief_idx[x] for x in indices]

n_social = len(social_nodes)
social_contact_idx = [x+1 for x in range(n_social_max)]

# social_beliefs = {}
social_i = 0
for person in range(n_social): 
    social_i += 1
    belief_list = []
    for belief_idx, belief_link in zip(social_belief_idx, actual_beliefs): 
        social_belief_string = f"{belief_idx}_{person+1}"
        social_belief = d[social_belief_string][0]
        nodes[f"s_{person+1}_{social_i}"] = {
            "type": "social_belief",
            "level": 1,
            "belief_text": social_belief,
            "social_contact": social_nodes[f"s_{person+1}"]['name'],
            "social_rating": social_nodes[f"s_{person+1}"]['rating'],
            "focal": social_nodes[f"s_{person+1}"]['focal']
        }
        edges.append({
            "source": f"s_{person}_{social_i}",
            "target": belief_link,
            "type": "social_belief_connection"
        })
        
# quick plot # 
import networkx as nx
import matplotlib.pyplot as plt

G_personal = nx.Graph()

# Add only personal-belief nodes to G_personal
for node_id, data in nodes.items():
    if data.get("type") == "belief":
        G_personal.add_node(node_id, **data)

# Add edges only if both ends are personal-belief nodes
for e in edges:
    src = e["source"]
    tgt = e["target"]
    if src in G_personal and tgt in G_personal:
        G_personal.add_edge(src, tgt, **e)
        
pos_personal = nx.spring_layout(G_personal)

plt.figure(figsize=(8, 6))
nx.draw_networkx(
    G_personal,
    pos=pos_personal,
    with_labels=True,
    node_size=500,
    node_color="skyblue"
)
plt.axis("off")
plt.show()

### try to plot social ###

# store attributes
nx.set_node_attributes(G_personal, pos_personal, "pos")

# build full graph 
G_full = nx.Graph()

# Add all nodes from the master dictionary
for node_id, data in nodes.items():
    G_full.add_node(node_id, **data)

# Add all edges
for e in edges:
    G_full.add_edge(e["source"], e["target"], **e)

pos_full = {}

# Copy the known positions for personal nodes from pos_personal
for node_id in G_personal.nodes:
    pos_full[node_id] = pos_personal[node_id]

social_nodes_list = []
for node_id, data in nodes.items():
    if data.get("type") == "social_belief":
        social_nodes_list.append(node_id)



# Different styles for personal vs. social
personal_nodelist = [n for n, d in G_full.nodes(data=True) if d.get("type") == "belief"]
social_nodelist = [n for n, d in G_full.nodes(data=True) if d.get("type") in ("social_belief", "social_contact")]

# Draw personal nodes
nx.draw_networkx_nodes(
    G_full, pos_full,
    nodelist=personal_nodelist,
    node_size=600,
    node_color="lightblue",
    label="Personal"
)

# Draw social nodes
nx.draw_networkx_nodes(
    G_full, pos_full,
    nodelist=social_nodelist,
    node_size=300,
    node_color="pink",
    label="Social"
)

# Draw edges
nx.draw_networkx_edges(G_full, pos_full, width=1.0)

# Draw labels
nx.draw_networkx_labels(G_full, pos_full, font_size=8)

plt.axis("off")
plt.title("Full Network: Personal + Social")
plt.legend()
plt.show()




### mapping things ### 
rows = []

for node_name, attrs in belief_nodes.items():
    direction = attrs["direction"]  # e.g. "con" or "pro"
    # e.g. if node_name == "b_2", then index_part == "2"
    index_part = node_name.split("_")[1]
    
    # second-level dict key, e.g. "con_2" or "pro_2"
    second_level_key = f"{direction}_{index_part}"
    
    if second_level_key in secondary_belief_dict:
        # For each text in that second-level list
        for i, text in enumerate(secondary_belief_dict[second_level_key], start=1):
            second_level_node_name = f"{second_level_key}_{i}"
            
            # Collect a row for the DataFrame
            rows.append([
                node_name,              # "b_2"
                second_level_node_name, # "con_2_1", "con_2_2", etc.
                text                    # "belief a", etc.
            ])

df_second_level = pd.DataFrame(
    rows, 
    columns=["first_level_node", "second_level_node", "second_level_text"]
)

# network viz # 
import networkx as nx 
import matplotlib.pyplot as plt 
G = nx.Graph()

# Focal node
focal_node = "focal"
G.add_node(focal_node)

# Add first-level belief nodes and connect them to focal
for node_name, attrs in belief_nodes.items():
    G.add_node(node_name, **attrs)  # store their attributes
    G.add_edge(focal_node, node_name, direction=attrs["direction"])

# Add second-level nodes
# We'll connect them to their respective first-level nodes.
for row in df_second_level.itertuples(index=False):
    first_level = row.first_level_node
    second_level = row.second_level_node
    text = row.second_level_text

    # Add the second-level node with the text as a node attribute
    # Also mark it as "second_level" so we can style it differently if we want
    G.add_node(second_level, text=text, node_type="second_level")

    # Add an edge from the first-level node to this second-level node
    # We can store a custom 'direction' or anything else we want
    G.add_edge(first_level, second_level, direction="secondary")

##############################################
# 4) Draw / visualize
##############################################
pos = nx.spring_layout(G, seed=42)  # fix a seed for repeatable layouts

# Separate edges by direction (pro, con, secondary)
pro_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "pro"]
con_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "con"]
sec_edges = [(u, v) for (u, v) in G.edges() if G[u][v].get("direction") == "secondary"]

# Draw edges in different colors
nx.draw_networkx_edges(G, pos, edgelist=pro_edges, edge_color="tab:red", width=2)
nx.draw_networkx_edges(G, pos, edgelist=con_edges, edge_color="tab:blue", width=2)
nx.draw_networkx_edges(G, pos, edgelist=sec_edges, edge_color="black", style="dotted")

# We can size the focal node and the first-level nodes differently
focal_node_list = [focal_node]
first_level_nodes = [n for n in belief_nodes.keys()]  # 'con_1', 'con_2', ...
second_level_nodes = [n for n, d in G.nodes(data=True) if d.get("node_type") == "second_level"]

# Node sizes for first-level beliefs (scale abs_importance by some factor)
first_level_sizes = [belief_nodes[n]["abs_importance"] * 10 for n in first_level_nodes]

# Draw focal node (single node)
nx.draw_networkx_nodes(G, pos, nodelist=focal_node_list,
                       node_size=600, node_color="yellow")

# Draw first-level nodes
nx.draw_networkx_nodes(G, pos, nodelist=first_level_nodes,
                       node_size=first_level_sizes, node_color="lightgray")

# Draw second-level nodes (smaller, a different color)
nx.draw_networkx_nodes(G, pos, nodelist=second_level_nodes,
                       node_size=200, node_color="lightblue")

# Add labels to all nodes
nx.draw_networkx_labels(G, pos, font_size=8, font_color="black")

plt.axis("off")
plt.show()






### predefined stuff ### 

# predefined questions (omg; also in this crazy format.)
predefined_questions_mapping = {
    0: "Strongly disagree",
    1: "Somewhat disagree",
    2: "Neutral / Not Sure", # "Neither agree nor disagree",
    3: "Somewhat agree",
    4: "Strongly agree",
}
n_answer_options = len(predefined_questions_mapping)

predefined_questions = [
    "I try to reduce my consumption of animal products",
    "I try to reduce my overall carbon footprint",
    "I try to reduce flying", # maybe waste: a bit covered by above
    "I believe in anthropogenic climate change",
    "Animals have feelings", # are sentient? 
    "Animal products are a necessary part of a healthy diet",
    "Animal products taste good", # this is tricky: like could be "some"
    "Most production animals have a good life",
    "Behavioral changes are effective at addressing climate change", # why not animal welfare?
    "Policy changes are effective at addressing climate change",
    "I support a tax on meat specifically",
    "I support a tax on animal products generally"   
]

predefined_idx = [
    # one question per row here: 
    "v_1198", "v_1199", "v_1222", "v_1234", "v_1246",
    "v_1200", "v_1201", "v_1223", "v_1235", "v_1247", 
    "v_1202", "v_1203", "v_1224", "v_1236", "v_1248",
    "v_1204", "v_1205", "v_1225", "v_1237", "v_1249",
    "v_1206", "v_1207", "v_1226", "v_1238", "v_1250",
    "v_1208", "v_1209", "v_1227", "v_1239", "v_1251",
    "v_1212", "v_1213", "v_1229", "v_1241", "v_1253",
    "v_1216", "v_1217", "v_1231", "v_1243", "v_1255",
    "v_1218", "v_1219", "v_1232", "v_1244", "v_1256",
    "v_1220", "v_1221", "v_1233", "v_1245", "v_1257",
    "v_1259", "v_1260", "v_1261", "v_1262", "v_1263",
    "v_1264", "v_1265", "v_1266", "v_1267", "v_1268",
]

predefined_dict = {}
i=-1
for question in predefined_questions: 
    for key, val in predefined_questions_mapping.items(): 
        i+=1
        idx = predefined_idx[i] 
        if d[idx][0]: 
            predefined_dict[question] = {
                "answer_code": key,
                "answer_text": val 
            } 

### political views + demographics ### 
# we need to add some mapping here for clarity eventually 
demographic_cols = [
    'own_pol', # politics
    'down_ind', # beliefs + behaviors point in same direction
    'down_con', # experience no conflict (beliefs + behaviors)
    'temp_dis', # temperature (distraction)
    'temp_dbt', # temperature (attention)
    'gender', # gender
    'age', # age
    'educ' # education
]
df_demographics = d[demographic_cols].melt(var_name="variable", value_name="value")

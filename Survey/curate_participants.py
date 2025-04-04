import pandas as pd 
import numpy as np 
import json

coupling_codes = {
    1: "con",
    2: "con",
    3: "con",
    4: "neut",
    5: "pro",
    6: "pro",
    7: "pro",
}

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        # Add other type conversions if needed
        return super().default(obj)

def likert_conversion(x, y, n):
    linspace = np.linspace(x, y, n)
    return {i: val for i, val in enumerate(linspace, 1)}

likert_scale_7 = likert_conversion(-1, 1, 7)
likert_forwards = likert_conversion(0, 1, 7)
likert_backwards = likert_conversion(1, 0, 7)

def is_numeric_string(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

# data [16, 17, 18, 19, 22, 26, 27]
participant_id = 27

d = pd.read_csv('data/data_project_1046442_2025_02_21.csv', sep=';')
d = d[d['lfdn'] == participant_id].reset_index()
d

# Initialize personal node/edge containers
personal_nodes = {}
personal_edges = []

# 1) Focal node
coupling_focal = d['v_1460'][0]
personal_nodes['b_focal'] = {
    'type': 'personal_belief',
    'level': 0,
    'value': coupling_focal,
    'direction': coupling_codes[coupling_focal],
    'value_num': likert_scale_7.get(coupling_focal),
    'importance': d['v_1615'][0],
    'importance_scaled': d['v_1615'][0] * 0.01,
    'label': d['v_722'][0],
}

n_beliefs = 10

# personal_nodes 
belief_free_pro_idx = [f"v_{x+1012}" for x in range(int(n_beliefs/2))]
belief_free_con_idx = [f"v_{x+1001}" for x in range(int(n_beliefs/2))]
belief_free_idx = belief_free_pro_idx + belief_free_con_idx

# node values
belief_val_pro = [f"v_{x+1461}" for x in range(int(n_beliefs/2))]
belief_val_con = [f"v_{x+1622}" for x in range(int(n_beliefs/2))]
belief_val_idx = belief_val_pro + belief_val_con

# couplings to focal 
belief_coupling_pro = [f"v_{x+1466}" for x in range(int(n_beliefs/2))]
belief_coupling_con = [f"v_{x+1627}" for x in range(int(n_beliefs/2))]
belief_coupling_idx = belief_coupling_pro + belief_coupling_con

# keep track of which beliefs exist
b_num = []
node_counter = 0
for i in range(n_beliefs):
    # direction is 'con' if i < 5, else 'pro'
    direction = "pro" if i < 5 else "con"
    
    # Check if there's a valid string for the free text
    free_val = d[belief_free_idx[i]][0]
    if isinstance(free_val, str) and not is_numeric_string(free_val):
        b_num.append(i)
        b_id = f"b_{node_counter}"   # "b_1", "b_2", etc.
        
        # add node
        importance = d[belief_val_idx[i]][0]
        personal_nodes[b_id] = {
            "type": "personal_belief",
            "level": 1,
            "value": 1 if direction == 'pro' else -1, 
            "direction": direction,
            "value_num": 1, # all beliefs are positive
            "label": free_val,
            "importance": importance,
            "importance_scaled": importance * 0.01,
        }
        
        # add edge
        coupling = d[belief_coupling_idx[i]][0]
        value_num = 1 if direction == "pro" else -1
        personal_edges.append({
            "source": b_id,
            "target": "b_focal",
            "direction": direction,
            "value_num": value_num,
            "type": "belief_coupling",
            "coupling": coupling * value_num, # flip importance given direction
            "coupling_scaled": coupling * value_num * 0.01, # same
        })
        
    node_counter += 1

# belief couplings 
# each of these is a list (I believe)
fix_mapping = {
    0: 5,
    1: 6,
    2: 7,
    3: 8,
    4: 9,
    5: 0,
    6: 1,
    7: 2,
    8: 3,
    9: 4,
}

for n_source in range(n_beliefs):
    for n_target in range(n_beliefs): 
        source_label = n_source + 1814
        target_label = n_target + 11
        coupling_column = f"v_{source_label}_{target_label}"
        if d[coupling_column][0] >= 0: 
            coupling_value = d[coupling_column][0]
            source_raw = fix_mapping[n_source]
            target_raw = fix_mapping[n_target]
            value_num = 1 if coupling_codes[coupling_value] == "pro" else -1
            personal_edges.append({
                "source": f"b_{source_raw}", 
                "target": f"b_{target_raw}", 
                "direction": coupling_codes[coupling_value],
                "value_num": value_num,
                "type": "belief_coupling",
                "coupling": coupling_value,
                "coupling_scaled": likert_scale_7[coupling_value],
            })

### social contacts ### 
n_social_max = 3
social_labels = [(f"v_{x+901}", f"v_{x+927}", f"v_{x+1674}", f"s_{x}") for x in range(n_social_max)]
social_nodes = {}
social_edges = []
for col_name, col_importance, col_focal, node_type in social_labels: 
    if isinstance(d[col_name][0], str) and not is_numeric_string(d[col_name][0]): 
        value = d[col_focal][0]
        importance = d[col_importance][0]
        social_nodes[node_type] = {
            "type": "social_belief",
            "level": 0,
            "label": d[col_name][0],
            "value": value,
            "value_num": likert_scale_7[value],
            "importance": importance,
            "importance_scaled": importance * 0.01
            }
        social_edges.append({
            "source": node_type,
            "target": "b_focal",
            "type": "social_coupling",
            "coupling": importance, #d[col_focal][0]
            "coupling_scaled": importance * 0.01
        })

### social --> other ### 
# first do couplings to CON
social_con = [f'v_{x+1684}' for x in range(5)]
social_pro = [f'v_{x+1694}' for x in range(5)]
social_beliefs = social_con + social_pro 
for person in range(n_social_max): 
    belief_list = []
    for num, belief_idx in enumerate(social_beliefs): 
        social_belief_string = f"{belief_idx}_{person+1}"
        social_belief = d[social_belief_string][0]
        if social_belief >= 0:
            # quick hack but do better way 
            multiplier = 1 if num >= 5 else -1 
            
            importance = social_nodes[f"s_{person}"]["importance"]
            social_nodes[f"s_{person}_{num}"] = {
                "type": "social_belief",
                "level": 1,
                "value": social_belief,
                "value_num": likert_scale_7[social_belief] * multiplier,
                "label": social_nodes[f"s_{person}"]['label'],
                "importance": importance,
                "importance_scaled": importance * 0.01,
                #"focal": social_nodes[f"s_{person}"]['focal']
            }
            social_edges.append({
                "source": f"s_{person}_{num}",
                "target": f"b_{fix_mapping[num]}",
                "type": "social_coupling",
                "coupling": importance, 
                "coupling_scaled": importance * 0.01
            })

### curate other items ###
# CMV 
cmv = {}
cmv['b_focal'] = {
    'past_five': d['v_1482'][0],
    'past_five_num': likert_scale_7[d['v_1482'][0]],
    'next_five': d['v_1489'][0],
    'next_five_num': likert_scale_7[d['v_1489'][0]],
}

cmv_pro_idx = [f"v_{x+1664}" for x in range(5)]
cmv_con_idx = [f"v_{x+1653}" for x in range(5)]
cmv_idx = cmv_pro_idx + cmv_con_idx
for num, ele in enumerate(cmv_idx): 
    rating = d[ele][0]
    if rating >= 0: 
        cmv[f'b_{num}'] = {
            'next_five': rating,
            'next_five_num': likert_scale_7[rating],
        }

# gather free text 
free_text = {}
free_text['cmv_focal'] = d['v_1632'][0]
free_text['cmv_other'] = d['v_1663'][0]
for key, val in personal_nodes.items():
    free_text[key] = val['label']
free_text['social'] = d['v_1738'][0]

# gather social perception
social_perception = {} 
social_perception['consumption_close'] = {
    'never': d['v_1634'][0] * 0.01,
    'limited': d['v_1635'][0] * 0.01,
    'daily': d['v_1636'][0] * 0.01,
}
social_perception['consumption_USA'] = {
    'never': d['v_1637'][0] * 0.01,
    'limited': d['v_1638'][0] * 0.01,
    'daily': d['v_1639'][0] * 0.01,
}

# meta-variables (attention, dissonance, etc.)
metavar = {
    'attention_pers': d['v_1613'][0],
    'attention_pers_num': likert_forwards[d['v_1613'][0]],
    'attention_soc': d['v_1614'][0],
    'attention_soc_num': likert_forwards[d['v_1614'][0]],
    'dissonance_pers': d['down_con'][0],
    'dissonance_pers_num': likert_backwards[d['down_con'][0]],
    'dissonance_soc': d['down_ind'][0],
    'dissonance_soc_num': likert_backwards[d['down_ind'][0]],
    'temp_distracted': d['temp_dis'][0],
    'temp_distracted_num': likert_forwards[d['temp_dis'][0]],
    'temp_attention': d['temp_dbt'][0],
    'temp_attention_num': likert_forwards[d['temp_dbt'][0]],
}

# demographics
gender = {
    1: 'Man',
    2: 'Woman',
    3: 'Other'
}
demographics = {
    'politics': d['own_pol'][0],
    'politics_num': likert_scale_7[d['own_pol'][0]],
    'gender': gender[d['gender'][0]],
    'age': d['age'][0],
    'education': d['educ'][0], # 1 = high school, 6 = graduate
    'state': d['v_1737'][0], # need a coding dict for this
    'zip': d['v_1419'][0],
}

# development and validation of the motivations to eat meat inventory
memi = {
    'v_1699': {
        'item': 1,
        'text': 'It goes against nature to eat only plants',
        'category': 'Natural',
        'likert': d['v_1699'][0],
        'value': likert_scale_7[d['v_1699'][0]],
    },
    'v_1700': {
        'item': 2,
        'text': 'Our bodies need the protein',
        'category': 'Necessary',
        'likert': d['v_1700'][0],
        'value': likert_scale_7[d['v_1700'][0]],
    },
    'v_1701': {
        'item': 3,
        'text': 'I want to fit in',
        'category': 'Normal',
        'likert': d['v_1701'][0],
        'value': likert_scale_7[d['v_1701'][0]],
    },
    'v_1702': {
        'item': 4,
        'text': 'It is delicious',
        'category': 'Nice',
        'likert': d['v_1702'][0],
        'value': likert_scale_7[d['v_1702'][0]],
    },
    'v_1703': {
        'item': 5,
        'text': 'It makes people strong and vigorous',
        'category': 'Necessary',
        'likert': d['v_1703'][0],
        'value': likert_scale_7[d['v_1703'][0]],
    },
    'v_1704': {
        'item': 6,
        'text': "I don't want other people to be uncomfortable",
        'category': 'Normal',
        'likert': d['v_1704'][0],
        'value': likert_scale_7[d['v_1704'][0]],
    },
    'v_1705': {
        'item': 7,
        'text': 'It is in all of the best tasting food',
        'category': 'Nice',
        'likert': d['v_1705'][0],
        'value': likert_scale_7[d['v_1705'][0]],
    },
    'v_1706': {
        'item': 8,
        'text': 'It could be unnatural not to eat meat',
        'category': 'Natural',
        'likert': d['v_1706'][0],
        'value': likert_scale_7[d['v_1706'][0]],
    },
    'v_1707': {
        'item': 9,
        'text': 'It is necessary for good health',
        'category': 'Necessary',
        'likert': d['v_1707'][0],
        'value': likert_scale_7[d['v_1707'][0]],
    },
    'v_1708': {
        'item': 10,
        'text': 'It is just one of the things people do',
        'category': 'Normal',
        'likert': d['v_1708'][0],
        'value': likert_scale_7[d['v_1708'][0]],
    },
    'v_1709': {
        'item': 11,
        'text': 'It gives me pleasure',
        'category': 'Nice',
        'likert': d['v_1709'][0],
        'value': likert_scale_7[d['v_1709'][0]],
    },
    'v_1710': {
        'item': 12,
        'text': 'I want to be sure I get all of the vitamins and minerals I need',
        'category': 'Necessary',
        'likert': d['v_1710'][0],
        'value': likert_scale_7[d['v_1710'][0]],
    },
    'v_1711': {
        'item': 13,
        'text': 'Everybody does it',
        'category': 'Normal',
        'likert': d['v_1711'][0],
        'value': likert_scale_7[d['v_1711'][0]],
    },
    'v_1712': {
        'item': 14,
        'text': 'It has good flavor',
        'category': 'Nice',
        'likert': d['v_1712'][0],
        'value': likert_scale_7[d['v_1712'][0]],
    },
    'v_1713': {
        'item': 15,
        'text': 'It gives me strength and endurance',
        'category': 'Necessary',
        'likert': d['v_1713'][0],
        'value': likert_scale_7[d['v_1713'][0]],
    },
    'v_1714': {
        'item': 16,
        'text': "I don't want to stand out",
        'category': 'Normal',
        'likert': d['v_1714'][0],
        'value': likert_scale_7[d['v_1714'][0]],
    },
    'v_1715': {
        'item': 17,
        'text': "Meals without it don't taste good",
        'category': 'Nice',
        'likert': d['v_1715'][0],
        'value': likert_scale_7[d['v_1715'][0]],
    },
    'v_1716': {
        'item': 18,
        'text': 'It is human nature to eat meat',
        'category': 'Natural',
        'likert': d['v_1716'][0],
        'value': likert_scale_7[d['v_1716'][0]],
    },
    'v_1717': {
        'item': 19,
        'text': 'Eating meat is part of our biology',
        'category': 'Natural',
        'likert': d['v_1717'][0],
        'value': likert_scale_7[d['v_1717'][0]],
    },
}

# Health, environmental, and animal rights motives for vegetarian eating
vemi = {
    'v_1718': {
        'item': 1,
        'text': 'I want to be healthy',
        'category': 'H',
        'likert': d['v_1718'][0],
        'value': likert_scale_7[d['v_1718'][0]],
    },
    'v_1719': {
        'item': 2,
        'text': 'Plant-based diets are better for the environment',
        'category': 'E',
        'likert': d['v_1719'][0],
        'value': likert_scale_7[d['v_1719'][0]],
    },
    'v_1720': {
        'item': 3,
        'text': 'Animals do not have to suffer',
        'category': 'A',
        'likert': d['v_1720'][0],
        'value': likert_scale_7[d['v_1720'][0]],
    },
    'v_1721': {
        'item': 4,
        'text': "Animals' rights are respected",
        'category': 'A',
        'likert': d['v_1721'][0],
        'value': likert_scale_7[d['v_1721'][0]],
    },
    'v_1722': {
        'item': 5,
        'text': 'I want to live a long time',
        'category': 'H',
        'likert': d['v_1722'][0],
        'value': likert_scale_7[d['v_1722'][0]],
    },
    'v_1723': {
        'item': 6,
        'text': 'Plant-based diets are more sustainable',
        'category': 'E',
        'likert': d['v_1723'][0],
        'value': likert_scale_7[d['v_1723'][0]],
    },
    'v_1724': {
        'item': 7,
        'text': 'I care about my body',
        'category': 'H',
        'likert': d['v_1724'][0],
        'value': likert_scale_7[d['v_1724'][0]],
    },
    'v_1725': {
        'item': 8,
        'text': 'Eating meat is bad for the planet',
        'category': 'E',
        'likert': d['v_1725'][0],
        'value': likert_scale_7[d['v_1725'][0]],
    },
    'v_1726': {
        'item': 9,
        'text': 'Animal rights are important to me',
        'category': 'A',
        'likert': d['v_1726'][0],
        'value': likert_scale_7[d['v_1726'][0]],
    },
    'v_1727': {
        'item': 10,
        'text': 'Plant-based diets are environmentally-friendly',
        'category': 'E',
        'likert': d['v_1727'][0],
        'value': likert_scale_7[d['v_1727'][0]],
    },
    'v_1728': {
        'item': 11,
        'text': 'It does not seem right to exploit animals',
        'category': 'A',
        'likert': d['v_1728'][0],
        'value': likert_scale_7[d['v_1728'][0]],
    },
    'v_1729': {
        'item': 12,
        'text': 'Plants have less of an impact on the environment than animal products',
        'category': 'E',
        'likert': d['v_1729'][0],
        'value': likert_scale_7[d['v_1729'][0]],
    },
    'v_1730': {
        'item': 13,
        'text': 'I am concerned about animal rights',
        'category': 'A',
        'likert': d['v_1730'][0],
        'value': likert_scale_7[d['v_1730'][0]],
    },
    'v_1731': {
        'item': 14,
        'text': 'My health is important to me',
        'category': 'H',
        'likert': d['v_1731'][0],
        'value': likert_scale_7[d['v_1731'][0]],
    },
    'v_1732': {
        'item': 15,
        'text': "I don't want animals to suffer",
        'category': 'A',
        'likert': d['v_1732'][0],
        'value': likert_scale_7[d['v_1732'][0]],
    },    
}

#### crazy meta dictionary? ####
meta_dict = {
    'participant_id': participant_id,
    'personal_nodes': personal_nodes,
    'personal_edges': personal_edges,
    'social_nodes': social_nodes,
    'social_edges': social_edges,
    'cmv': cmv,
    'free_text': free_text,
    'social_perception': social_perception,
    'metavar': metavar,
    'demographics': demographics,
    'memi': memi,
    'vemi': vemi,
}

# save meta_dict
with open(f'data/human_clean/metadict_{participant_id}.json', 'w') as f:
    f.write(json.dumps(meta_dict, cls=NumpyEncoder))

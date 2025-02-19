import pandas as pd 
import json
import numpy as np 

def calc_H_pers(metadict): 
        personal_nodes = metadict['personal_nodes']
        personal_edges = metadict['personal_edges']

        # first take out the edges
        personal_edges_df = pd.DataFrame(personal_edges)
        personal_edges_df = personal_edges_df[personal_edges_df['source'] != personal_edges_df['target']]

        # 1. Pre-aggregate edges by taking the mean strength for each pair (A,B)
        p_edges_agg = (
            personal_edges_df
            .groupby(['source', 'target'], as_index=False)
            .agg({'coupling_scaled': 'mean'})
        )

        ### do the personal dissonance ###
        H_pers = 0
        for num, row in p_edges_agg.iterrows():
                # extract params 
                source = row['source']
                target = row['target']
                wij = row['coupling_scaled']

                xi = personal_nodes[source]['importance_scaled'] 
                bi = personal_nodes[source]['value_num']
                xj = personal_nodes[target]['importance_scaled']
                bj = personal_nodes[target]['value_num']

                # sum 
                H_pers += wij * xi * bi * xj * bj

        # then it should be negative 
        H_pers = -H_pers

        # then apply the attention parameter
        attention_pers = metadict['metavar']['attention_pers_num']
        H_pers_att = H_pers * attention_pers

        return H_pers, H_pers_att

def calc_H_soc(metadict): 
        social_edges = metadict['social_edges']
        social_nodes = metadict['social_nodes']
        personal_nodes = metadict['personal_nodes']
        
        H_soc = 0
        for list_ele in social_edges: 

                source = list_ele['source']
                target = list_ele['target']
                pik = list_ele['coupling_scaled']

                bi = personal_nodes[target]['value_num']
                sik = social_nodes[source]['value_num'] 

                H_soc += pik * bi * sik

        # negative 
        H_soc = -H_soc

        # divide by 3 because n=3 contacts
        # this I am not sure about.
        H_soc = H_soc / 3

        # then apply attention parameter
        H_soc_att = H_soc * metadict['metavar']['attention_soc_num']

        return H_soc, H_soc_att

# load data
participant_ids = [16, 17, 18, 19]

def load_data(participant_id): 
        
        with open(f'data/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        return metadict

likert_mapping = {
        1: -1.0,
        2: -0.6666666666666667,
        3: -0.33333333333333337,
        4: 0.0,
        5: 0.33333333333333326,
        6: 0.6666666666666667,
        7: 1.0
        }

results = []
for p_id in participant_ids: 
        metadict = load_data(p_id)
        key_true = metadict['personal_nodes']['b_focal']['value']
        for key, val in likert_mapping.items(): 
                metadict_copy = metadict.copy()
                metadict_copy['personal_nodes']['b_focal']['value_num'] = val
                H_pers, H_pers_att = calc_H_pers(metadict_copy)
                H_soc, H_soc_att = calc_H_soc(metadict_copy)
                D_total = H_pers + H_soc
                D_total_att = H_pers_att + H_soc_att
                results.append((p_id, key_true, key, val, H_pers, H_pers_att, H_soc, H_soc_att, D_total, D_total_att))

df_results = pd.DataFrame(
        results, 
        columns=['participant_id', 
                 'key_true', 
                 'key', 
                 'value_num', 
                 'H_pers', 
                 'H_pers_att', 
                 'H_soc', 
                 'H_soc_att', 
                 'D_total', 
                 'D_total_att']
        )

# plot the curves # 
# also work back what is actually high and low dissonance
# is there really anything constraining this to be linear and boring?
import seaborn as sns 
import matplotlib.pyplot as plt

sns.lineplot(
        data=df_results, 
        x='value_num', 
        y='D_total', 
        hue='participant_id'
        ) 

sns.lineplot(
        data=df_results, 
        x='value_num', 
        y='D_total_att', 
        hue='participant_id'
        )

'''
Basically, prediction for everyone is: 
1. They *should* eat less meat.
2. There must be an external field. 
-- e.g., price, convenience, habit, etc. 
-- that we are currently not capturing.
3. Could we have gotten something else?
-- yes the social component allows this, right?
-- i.e., if all friends are really mixed.
-- or maybe it does not actually...

Outstanding questions: 
1. how do we scale things? 
-- e.g., social vs. personal.
-- we have some limitations (e.g., 3 contacts, 10 beliefs).
2. how do we get non-linearity? 
-- is the model just garbage? 

Do a manual calculation of this. 
'''

# although actually I might have done this wrong
# try with the other approach 
participant_ids = [16, 17, 18, 19]

def load_data_2(participant_id): 
        
        with open(f'data/metadict_test_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        return metadict

results_2 = []
for p_id in participant_ids:
        metadict = load_data_2(p_id)
        key_true = metadict['personal_nodes']['b_focal']['value']
        for key, val in likert_mapping.items(): 
                metadict_copy = metadict.copy()
                metadict_copy['personal_nodes']['b_focal']['value_num'] = val
                H_pers, H_pers_att = calc_H_pers(metadict_copy)
                H_soc, H_soc_att = calc_H_soc(metadict_copy)
                D_total = H_pers + H_soc
                D_total_att = H_pers_att + H_soc_att
                results_2.append((p_id, key_true, key, val, H_pers, H_pers_att, H_soc, H_soc_att, D_total, D_total_att))

df_2 = pd.DataFrame(
        results_2,
        columns=['participant_id',
                        'key_true',
                        'key',
                        'value_num',
                        'H_pers',
                        'H_pers_att',
                        'H_soc',
                        'H_soc_att',
                        'D_total',
                        'D_total_att']
        )

# quick plot 
sns.lineplot(
        data=df_2,
        x='value_num',
        y='D_total',
        hue='participant_id'
        )

sns.lineplot(
        data=df_2,
        x='value_num',
        y='D_total_att',
        hue='participant_id'
        )

# look at CMV and felt dissonance # 

# do the calculation only for the focal
# i.e., friends + beliefs towards this 
personal_nodes = metadict['personal_nodes']
personal_edges = metadict['personal_edges']

# first take out the edges
personal_edges_df = pd.DataFrame(personal_edges)
personal_edges_df = personal_edges_df[personal_edges_df['source'] != personal_edges_df['target']]

# 1. Pre-aggregate edges by taking the mean strength for each pair (A,B)
p_edges_agg = (
        personal_edges_df
        .groupby(['source', 'target'], as_index=False)
        .agg({'coupling_scaled': 'mean'})
)
personal_edges_df[personal_edges_df['target']=='b_focal']

p_edges_agg = p_edges_agg[(p_edges_agg['source'] == 'b_focal') | (p_edges_agg['target'] == 'b_focal')]
p_edges_agg


def calc_H_pers(metadict): 
        personal_nodes = metadict['personal_nodes']
        personal_edges = metadict['personal_edges']

        # first take out the edges
        personal_edges_df = pd.DataFrame(personal_edges)
        personal_edges_df = personal_edges_df[personal_edges_df['source'] != personal_edges_df['target']]

        # 1. Pre-aggregate edges by taking the mean strength for each pair (A,B)
        p_edges_agg = (
            personal_edges_df
            .groupby(['source', 'target'], as_index=False)
            .agg({'coupling_scaled': 'mean'})
        )

        ### do the personal dissonance ###
        H_pers = 0
        for num, row in p_edges_agg.iterrows():
                # extract params 
                source = row['source']
                target = row['target']
                wij = row['coupling_scaled']

                xi = personal_nodes[source]['importance_scaled'] 
                bi = personal_nodes[source]['value_num']
                xj = personal_nodes[target]['importance_scaled']
                bj = personal_nodes[target]['value_num']

                # sum 
                H_pers += wij * xi * bi * xj * bj

        # then it should be negative 
        H_pers = -H_pers

        # then apply the attention parameter
        attention_pers = metadict['metavar']['attention_pers_num']
        H_pers_att = H_pers * attention_pers

        return H_pers, H_pers_att
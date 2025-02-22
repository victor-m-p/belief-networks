import pandas as pd 
import json
import numpy as np 
import seaborn as sns 
import matplotlib.pyplot as plt

likert_mapping = {
        1: -1.0,
        2: -0.6666666666666667,
        3: -0.33333333333333337,
        4: 0.0,
        5: 0.33333333333333326,
        6: 0.6666666666666667,
        7: 1.0
        }

def agg_func_social(pik, bi, sik, aggfunc='mult'):
        # standard Potts type
        if aggfunc=='mult': 
                return pik * bi * sik 
        # absoulte distance 
        # this can only give dissonance now (not consonance)
        if aggfunc=='abs': 
                return pik * np.abs(bi - sik)

def calc_H_pers(metadict, filter=None): 
        personal_nodes = metadict['personal_nodes']
        personal_edges = metadict['personal_edges']

        # first take out the edges
        personal_edges_df = pd.DataFrame(personal_edges)
        personal_edges_df = personal_edges_df[personal_edges_df['source'] != personal_edges_df['target']]

        if filter is not None: 
                personal_edges_df = personal_edges_df[personal_edges_df['target'] == filter]

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

def calc_H_soc(metadict, filter = None, aggfunc = 'mult'): 
        social_edges = metadict['social_edges']
        social_nodes = metadict['social_nodes']
        personal_nodes = metadict['personal_nodes']
        
        H_soc = 0
        for list_ele in social_edges: 

                source = list_ele['source']
                target = list_ele['target']
                
                if filter is None: 
                        pik = list_ele['coupling_scaled'] 
                        bi = personal_nodes[target]['value_num']
                        sik = social_nodes[source]['value_num'] 

                        energy = agg_func_social(pik, bi, sik, aggfunc)
                        H_soc += energy
                        
                elif target == filter: 
                
                        pik = list_ele['coupling_scaled'] 
                        bi = personal_nodes[target]['value_num']
                        sik = social_nodes[source]['value_num'] 

                        energy = agg_func_social(pik, bi, sik, aggfunc)
                        H_soc += energy
                
        # negative 
        if aggfunc == 'mult': 
                H_soc = -H_soc

        # divide by 3 because n=3 contacts
        # this I am not sure about.
        H_soc = H_soc / 3

        # then apply attention parameter
        H_soc_att = H_soc * metadict['metavar']['attention_soc_num']

        return H_soc, H_soc_att

# load data
def load_data(participant_id, data_type='human'): 
        
        if data_type=='human':
                with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                        metadict = json.loads(f.read())
        elif data_type=='gpt':
                with open(f'data/gpt_clean/metadict_{participant_id}.json') as f:
                        metadict = json.loads(f.read())

        return metadict

# calculate:
# consider whether we are double-counting personal edges here.
def calculate_total(participant_ids, data_type):
        results = []
        for p_id in participant_ids:
                metadict = load_data(p_id, data_type)
                key_true = metadict['personal_nodes']['b_focal']['value']
                for key, val in likert_mapping.items(): 
                        metadict_copy = metadict.copy()
                        metadict_copy['personal_nodes']['b_focal']['value_num'] = val
                        H_pers, H_pers_att = calc_H_pers(metadict_copy)
                        H_soc, H_soc_att = calc_H_soc(metadict_copy)
                        H_soc_abs, H_soc_abs_att = calc_H_soc(metadict_copy, aggfunc='abs')
                        D_total = H_pers + H_soc
                        D_total_att = H_pers_att + H_soc_att
                        D_total_abs = H_pers + H_soc_abs
                        D_total_abs_att = H_pers_att + H_soc_abs_att
                        results.append((
                                p_id, 
                                data_type,
                                key_true, 
                                key, 
                                val, 
                                H_pers, 
                                H_pers_att, 
                                H_soc, 
                                H_soc_att, 
                                H_soc_abs, 
                                H_soc_abs_att,
                                D_total,
                                D_total_att,
                                D_total_abs,
                                D_total_abs_att
                                ))

        results = pd.DataFrame(
                results,
                columns=[
                        'participant_id',
                        'data_type',
                        'key_true',
                        'key',
                        'value_num',
                        'H_pers',
                        'H_pers_att',
                        'H_soc',
                        'H_soc_att',
                        'H_soc_abs',
                        'H_soc_abs_att',
                        'D_total',
                        'D_total_att',
                        'D_total_abs',
                        'D_total_abs_att'
                        ]
        )
        return results

participant_ids = [16, 17, 18, 19, 22, 26, 27]
results_human = calculate_total(participant_ids, 'human')
results_gpt = calculate_total(participant_ids, 'gpt')

results_human_true = results_human[results_human['key_true'] == results_human['key']]
results_gpt_true = results_gpt[results_gpt['key_true'] == results_gpt['key']]

# plot personal vs social
# what if we make a huge plot? 
def plot_simple(
        nrows, 
        ncols, 
        figsize,
        elements, 
        results, 
        results_actual,
        outname=False):
    # Create a grid of subplots
    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize)
    
    # Flatten the array of Axes objects for easy iteration
    ax = ax.flatten()
    
    for i, ele in enumerate(elements):
        # --- Line plot ---
        sns.lineplot(
            data=results,
            x='value_num',
            y=ele,
            hue='participant_id',
            ax=ax[i],
            legend=True  # We'll keep legend on for the lineplot
        )
        
        # --- Scatter plot (no legend) ---
        sns.scatterplot(
            data=results_actual,
            x='value_num',
            y=ele,
            hue='participant_id',
            ax=ax[i],
            legend=False
        )

        # --- Titles and labels ---
        ax[i].set_title(f"{ele}")
        ax[i].set_xlabel("Value Num")
        ax[i].set_ylabel(ele)

        # If you have more elements than subplots, guard against index errors
        if i >= len(ax) - 1:
            break

    # Now handle the legends so that only the first subplot shows it
    # or make a single figure-level legend if you prefer
    handles, labels = ax[0].get_legend_handles_labels()
    ax[0].legend(handles, labels, title='participant_id')

    # Remove legend from subplots 1 through end
    for i in range(1, len(elements)):
        leg = ax[i].get_legend()
        if leg is not None:
            leg.remove()

    plt.tight_layout()
    
    if outname:
        plt.savefig(f"fig/mod_{outname}.png")
        plt.close()
    else: 
        plt.show()

# results human H
plot_simple(
        nrows=3,
        ncols=2,
        figsize=(6, 8),
        elements=['H_pers', 'H_pers_att', 'H_soc', 'H_soc_att', 'H_soc_abs', 'H_soc_abs_att'],
        results=results_human,
        results_actual=results_human_true,
        outname='H_overall_human'
)
# results gpt H
plot_simple(
        nrows=3,
        ncols=2,
        figsize=(6, 8),
        elements=['H_pers', 'H_pers_att', 'H_soc', 'H_soc_att', 'H_soc_abs', 'H_soc_abs_att'],
        results=results_gpt,
        results_actual=results_gpt_true,
        outname='H_overall_gpt'
)
# results human H
plot_simple(
        nrows=2,
        ncols=2,
        figsize=(6, 6),
        elements=['D_total', 'D_total_att', 'D_total_abs', 'D_total_abs_att'],
        results=results_human,
        results_actual=results_human_true,
        outname='D_overall_human'
)
# results gpt H
plot_simple(
        nrows=2,
        ncols=2,
        figsize=(6, 6),
        elements=['D_total', 'D_total_att', 'D_total_abs', 'D_total_abs_att'],
        results=results_gpt,
        results_actual=results_gpt_true,
        outname='D_overall_gpt'
)

# okay calculation for focal
# something is going wrong here. 
results_focal = []
for p_id in participant_ids:
        metadict = load_data(p_id)
        key_true = metadict['personal_nodes']['b_focal']['value']
        for key, val in likert_mapping.items(): 
                metadict_copy = metadict.copy()
                metadict_copy['personal_nodes']['b_focal']['value_num'] = val
                H_pers, H_pers_att = calc_H_pers(metadict_copy, filter='b_focal')
                H_soc, H_soc_att = calc_H_soc(metadict_copy, filter='b_focal')
                H_soc_abs, H_soc_abs_att = calc_H_soc(metadict_copy, filter='b_focal', aggfunc='abs')
                D_total = H_pers + H_soc
                D_total_att = H_pers_att + H_soc_att
                D_total_abs = H_pers + H_soc_abs 
                D_total_abs_att = H_pers_att + H_soc_abs_att
                results_focal.append((
                        p_id, 
                        key_true, 
                        key, 
                        val, 
                        H_pers, 
                        H_pers_att, 
                        H_soc, 
                        H_soc_att, 
                        H_soc_abs, 
                        H_soc_abs_att,
                        D_total,
                        D_total_att,
                        D_total_abs,
                        D_total_abs_att
                        ))
                
df_focal = pd.DataFrame(
        results_focal,
        columns=['participant_id',
                        'key_true',
                        'key',
                        'value_num',
                        'H_pers',
                        'H_pers_att',
                        'H_soc',
                        'H_soc_att',
                        'H_soc_abs',
                        'H_soc_abs_att',
                        'D_total',
                        'D_total_att',
                        'D_total_abs',
                        'D_total_abs_att']
        )
df_focal_actual = df_focal[df_focal['key_true'] == df_focal['key']]

plot_simple(
        nrows=3,
        ncols=2,
        figsize=(6, 8),
        elements=['H_pers', 'H_pers_att', 'H_soc', 'H_soc_att', 'H_soc_abs', 'H_soc_abs_att'],
        results=df_focal,
        results_actual=df_focal_actual,
        outname='H_focal'
)
plot_simple(
        nrows=2,
        ncols=2,
        figsize=(6, 6),
        elements=['D_total', 'D_total_att', 'D_total_abs', 'D_total_abs_att'],
        results=df_focal,
        results_actual=df_focal_actual,
        outname='D_focal'
)


# Look at felt dissonance # 
cmv_collected = []
dissonance_collected = []
for p_id in participant_ids: 
        metadict = load_data_2(p_id)
        cmv = pd.DataFrame.from_dict(metadict['cmv'], orient='index')
        cmv['participant_id'] = p_id
        cmv_collected.append(cmv)
        
        dissonance_pers = metadict['metavar']['dissonance_pers_num']
        dissonance_soc = metadict['metavar']['dissonance_soc_num']
        dissonance_collected.append((p_id, dissonance_pers, dissonance_soc))
cmv_df = pd.concat(cmv_collected)
dissonance_df = pd.DataFrame(
        dissonance_collected,
        columns=['participant_id',
                 'd_pers',
                 'd_soc'])

# plot personal dissonance # 
cmv_subset = cmv_df[['participant_id', 'past_five_num', 'next_five_num']]
cmv_subset = cmv_subset.dropna()

focal_actual_D = df_focal_actual[['participant_id', 'D_total_abs', 'D_total_abs_att']]
results_actual_D = results_actual[['participant_id', 'D_total_abs', 'D_total_abs_att']]

cmv_focal = cmv_subset.merge(focal_actual_D, on = 'participant_id', how = 'inner')
cmv_overall = cmv_subset.merge(results_actual_D, on = 'participant_id', how = 'inner')

# for FOCAL only
# (potential) Dissonance & Change (not so impressive)
fig, ax = plt.subplots(2, 2, figsize=(6, 4))
ax = ax.flatten()
sns.scatterplot(
        data=cmv_focal,
        x='past_five_num',
        y='D_total_abs',
        hue='participant_id',
        ax=ax[0]
)
sns.scatterplot(
        data=cmv_focal,
        x='next_five_num',
        y='D_total_abs',
        hue='participant_id',
        legend=False,
        ax=ax[1]
)
sns.scatterplot(
        data=cmv_focal,
        x='past_five_num',
        y='D_total_abs_att',
        hue='participant_id',
        legend=False,
        ax=ax[2]
)
sns.scatterplot(
        data=cmv_focal,
        x='next_five_num',
        y='D_total_abs_att',
        hue='participant_id',
        legend=False,
        ax=ax[3]
)
plt.tight_layout()
plt.savefig('fig/cmv_focal.png')
plt.close()

# against overall #
fig, ax = plt.subplots(2, 2, figsize=(6, 4))
ax = ax.flatten()
sns.scatterplot(
        data=cmv_overall,
        x='past_five_num',
        y='D_total_abs',
        hue='participant_id',
        ax=ax[0]
)
sns.scatterplot(
        data=cmv_overall,
        x='next_five_num',
        y='D_total_abs',
        hue='participant_id',
        legend=False,
        ax=ax[1]
)
sns.scatterplot(
        data=cmv_overall,
        x='past_five_num',
        y='D_total_abs_att',
        hue='participant_id',
        legend=False,
        ax=ax[2]
)
sns.scatterplot(
        data=cmv_overall,
        x='next_five_num',
        y='D_total_abs_att',
        hue='participant_id',
        legend=False,
        ax=ax[3]
)
plt.tight_layout()
plt.savefig('fig/cmv_overall.png')
plt.close()

# how about just potential dissonance vs felt dissonance?
# not really a strong thing here right now.
# also just so crazy limited data. 
dissonance_df 

# think about what we could do though. 
# we can basically calculate the curve for each person [FOR EACH BELIEF]

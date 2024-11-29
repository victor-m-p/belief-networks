'''
todo;
clean up document. 
'''

import numpy as np 
import pandas as pd 
import pickle 
import re
import matplotlib.pyplot as plt

df = pd.read_csv('data/anes_data.csv')
df = df.dropna()

with open('data/new_pos.pkl', 'rb') as handle:
    pos = pickle.load(handle)

# calculate individual average x axis positions
df['ID'] = df.index
melted_df = pd.melt(df, id_vars=['ID'], var_name='question_year', value_name='answer')
melted_df['question'] = melted_df['question_year'].str.extract(r'([a-zA-Z]+)')
melted_df['year'] = melted_df['question_year'].str.extract(r'(\d{4})')
melted_df = melted_df.drop(columns=['question_year'])
melted_df = melted_df[['ID', 'question', 'year', 'answer']]

# calculate individual 
position_list = []
for key, val in pos.items(): 
    # question, year, answer information
    question = re.search(r'([a-zA-Z]+)', key).group(0)
    year = re.search(r'(\d{4})', key).group(0)
    answer = re.search(r'_(.*)', key).group(1)
    
    # x axis value 
    xvalue = val[0]
    information = (question, year, answer, xvalue)
    position_list.append(information)

position_df = pd.DataFrame(position_list, columns=['question', 'year', 'answer', 'xvalue'])

# since position here (2016) is used for 2020 we need to duplicate
position_extra = position_df.copy()
position_extra['year'] = '2020'
position_df = pd.concat([position_df, position_extra])

# now we merge (here; still okay)
complete_df = melted_df.merge(position_df, on=['question', 'year', 'answer'], how='inner')

# we can do this with sorting and lagging instead
df_2016 = complete_df[complete_df['year']=='2016']
df_2020 = complete_df[complete_df['year']=='2020']
df_2016 = df_2016.rename(columns={
    'answer': 'answer_lag',
    'xvalue': 'xvalue_lag'
})
df_2016 = df_2016.drop(columns=['year'])
df_2020 = df_2020.drop(columns=['year'])

lagged_df = df_2016.merge(df_2020, on = ['ID', 'question'], how = 'inner')

'''
First hypothesis;
distance ~ |xvalue_lag| + (1+ID)
'''

lagged_df['xvalue_lag_abs'] = lagged_df['xvalue_lag'].abs()
lagged_df['xvalue_delta'] = abs(lagged_df['xvalue'] - lagged_df['xvalue_lag'])

# plot idea for first model;
import seaborn as sns 
fig, ax = plt.subplots()

sns.lineplot(
    data=lagged_df,
    x='xvalue_lag_abs', 
    y='xvalue_delta', 
    hue='question'
    )

# Add jitter to the x and/or y values
lagged_df['xvalue_lag_abs_jittered'] = lagged_df['xvalue_lag_abs'] + np.random.uniform(-0.02, 0.02, len(lagged_df))
lagged_df['xvalue_delta_jittered'] = lagged_df['xvalue_delta'] + np.random.uniform(-0.02, 0.02, len(lagged_df))

# Plot with jittered values
sns.scatterplot(
    data=lagged_df,
    x='xvalue_lag_abs_jittered',
    y='xvalue_delta_jittered',
    hue='question',
    alpha=0.1,
    legend=False
)

plt.xlabel(r'$|X_{t1}|, \forall X$', fontsize=12)
plt.ylabel(r'$|X_{t1} - X_{t2}|, \forall X$', fontsize=12)
plt.show();

# now we can also do the average 
# like; how far do you move thing. 
average_values = complete_df.groupby(['ID', 'year'])['xvalue'].mean().reset_index(name='avg_x')
average_2016 = average_values[average_values['year']=='2016']
average_2020 = average_values[average_values['year']=='2020']
average_2016 = average_2016.rename(columns={
    'avg_x': 'x_2016'})
average_2020 = average_2020.rename(columns={
    'avg_x': 'x_2020'
})
average_2016 = average_2016.drop(columns='year')
average_2020 = average_2020.drop(columns='year')
average_values = average_2016.merge(average_2020, on = 'ID', how = 'inner')
average_values['absolute_dist'] = abs(average_values['x_2016']-average_values['x_2020'])
average_values['absolute_2016'] = abs(average_values['x_2016'])

# Plot with jittered values
fig, ax = plt.subplots(figsize=(5, 3))
sns.regplot(
    data=average_values,
    x='absolute_2016', 
    y='absolute_dist', 
    scatter_kws={'alpha': 0.1},
    x_jitter=0.01,
    y_jitter=0.01
    )
plt.xlabel('|avg(X t1)|')
plt.ylabel('|avg(X t1)-avg(X t2)|')
plt.show();

# by distance from your locus to opinions # 
lagged_df = lagged_df.merge(average_2016, on = 'ID', how = 'inner')
lagged_df['d_abs'] = abs(lagged_df['xvalue_lag']-lagged_df['x_2016'])

sns.regplot(
    data=lagged_df,
    x='d_abs',
    y='xvalue_delta',
    scatter_kws={'alpha': 0.1},
    x_jitter=0.01,
    y_jitter=0.01
)

# absolute movement by SD of beliefs 
data_2016 = complete_df[complete_df['year']=='2016']
data_2016 = data_2016.groupby(['ID'])['xvalue'].std().reset_index(name='std')
lagged_df = lagged_df.merge(data_2016, on = 'ID', how = 'inner')

centroid_2020 = complete_df[complete_df['year']=='2020']
centroid_2020 = centroid_2020.groupby(['ID'])['xvalue'].mean().reset_index(name='centroid_2020')
lagged_df = lagged_df.merge(centroid_2020, on = 'ID', how = 'inner')

lagged_df['centroid_delta'] = abs(lagged_df['centroid_2020']-lagged_df['x_2016'])
lagged_unique = lagged_df[['ID', 'std', 'centroid_delta']].drop_duplicates()

fig, ax = plt.subplots(figsize=(6, 4))
sns.regplot(
    data=lagged_df,
    x = 'std', 
    y = 'centroid_delta',
    scatter_kws = {'alpha': 0.1},
    x_jitter = 0.01, 
    y_jitter = 0.01,
)
plt.ylabel(r"$abs(avg(X_{t1})-avg(X_{t2}))$")
plt.xlabel(r'$std(X_{t1})$')
plt.show();
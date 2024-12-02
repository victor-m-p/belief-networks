'''
todo;
clean up document. 
'''

import numpy as np 
import pandas as pd 
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
pd.options.mode.chained_assignment = None  # default='warn'
from matplotlib import rcParams
# Set global scaling for text, axes, and legend
rcParams['font.size'] = 14  # Base font size
rcParams['axes.titlesize'] = 20  # Title font size
rcParams['axes.labelsize'] = 16  # X and Y axis labels
rcParams['legend.fontsize'] = 14  # Legend font size
rcParams['xtick.labelsize'] = 12  # X-axis tick size
rcParams['ytick.labelsize'] = 12  # Y-axis tick size


df = pd.read_csv('data/anes_data.csv')
pos = pd.read_csv('data/anes_pos.csv')

# since position here (2016) is used for 2020 we need to duplicate
pos2020 = pos.copy()
pos2020['year'] = 2020
position_df = pd.concat([pos, pos2020])

# now we merge (here; still okay)
complete_df = df.merge(position_df, on=['question', 'year', 'answer'], how='inner')

# generate the lagged data
# important to include all of the grouping columns here
complete_df = complete_df.sort_values(by=['ID', 'question', 'year'])

# adding lagged columns
lagged_df = complete_df.copy()
lagged_df['answer_lag'] = lagged_df.groupby(['ID', 'question'])['answer'].shift(1)
lagged_df['xvalue_lag'] = lagged_df.groupby(['ID', 'question'])['xvalue'].shift(1)

# now drop raws where lagged values are nan
lagged_df = lagged_df.dropna(subset=['answer_lag', 'xvalue_lag']).reset_index(drop=True)

# now compute all of the metrics that we need.
# \delta x_{a_i} \sim |x_{a_i}| 
lagged_df['xvalue_lag_abs'] = lagged_df['xvalue_lag'].abs()
lagged_df['xvalue_delta_abs'] = abs(lagged_df['xvalue'] - lagged_df['xvalue_lag'])

# average values 
# \delta x_{p_i} \sim |x_{p_i}|
average_values = complete_df.groupby(['ID', 'year'])['xvalue'].mean().reset_index(name='avg_x')
average_pivot = average_values.pivot(index='ID', columns='year', values='avg_x').reset_index()
average_pivot['abs_x_baseline'] = average_pivot[2016].abs()
average_pivot['abs_x_distance'] = abs(average_pivot[2016]-average_pivot[2020])
average_pivot = average_pivot.rename(columns = {2016: 'average_x_2016',
                                                2020: 'average_x_2020'})

# average values by distance from centroid
# here we can merge the two;
# \delta x_{a_i} ~ dist(x_{p_i}, x_{a_i})
merged_df = lagged_df.merge(average_pivot, on='ID', how='inner')
merged_df['centroid_distance'] = abs(merged_df['average_x_2016']-merged_df['xvalue_lag'])

# average values by SD of beliefs
# is it that each belief is more likely to change, or that the aggregate (individual) is more likely to change? 
data_2016 = complete_df[complete_df['year']==2016]
xvalue_2016 = data_2016.groupby(['ID'])['xvalue'].std().reset_index(name='xvalue_lag_std')
merged_df = merged_df.merge(xvalue_2016, on='ID', how='inner')

#### plot model 1 ####
def plot_question(df, col_x, col_y, title, xlab, ylab, save=None): 
    lm = sns.lmplot(
        data = df,
        x = col_x,
        y = col_y,
        hue = 'question',
        aspect = 1.5,
        height = 5,
        x_jitter = 0.015,
        y_jitter = 0.015,
        scatter_kws = {'alpha': 0.02},
        legend = False
    )
    color_pop = 'gray'
    ax = lm.ax
    sns.regplot(
        data = df,
        x = col_x,
        y = col_y,
        scatter = False,
        color = color_pop,
        ax = ax
    )
    legend_handles = []
    unique_questions = df['question'].unique()
    palette = sns.color_palette()
    for question, color in zip(unique_questions, palette):
        legend_handles.append(mlines.Line2D([], [], color=color, marker='o', linestyle='None', label=question))
    legend_handles.append(mlines.Line2D([], [], color=color_pop, label='Population'))
    ax.legend(handles=legend_handles, title='Question')
    ax.set_title(title)
    plt.ylabel(ylab)
    plt.xlabel(xlab)
    plt.tight_layout()
    if save: 
        plt.savefig(save)
        plt.close()
    else: 
        plt.show();

# |\Delta x_{a, i}| \sim f(|x_{a, i}(t-1)|)
plot_question(
    df = merged_df,
    col_x = 'xvalue_lag_abs',
    col_y = 'xvalue_delta_abs',
    title = r'$|\Delta x_{a, i}| \sim f(|x_{a, i}(t-1)|)$',
    xlab = r'$|x_{a, i}(t-1)|$',
    ylab = r'$|\Delta x_{a,i}|$',
    save = 'figres/m1.png'
)

#### plot model 2 ####
# |\Delta x_{i} \sim |x_{i}(t-1)|
def plot_individual(df, col_x, col_y, title, xlab, ylab, save=None): 
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.regplot(
        data = df,
        x = col_x,
        y = col_y,
        scatter_kws = {'alpha': 0.1},
        x_jitter = 0.015,
        y_jitter = 0.015
    )
    ax.set_title(title, fontsize=20)
    plt.ylabel(ylab, fontsize=14)
    plt.xlabel(xlab, fontsize=14)
    plt.tight_layout()
    if save: 
        plt.savefig(save)
        plt.close()
    else: 
        plt.show();

plot_individual(
    df = merged_df[['ID', 'abs_x_baseline', 'abs_x_distance']].drop_duplicates(),
    col_x = 'abs_x_baseline',
    col_y = 'abs_x_distance',
    title = r'$|\Delta x_{i}| \sim |x_{i}(t-1)|$',
    xlab = r'$|x_{i}(t-1)|$',
    ylab = r'$|\Delta x_{i}|$',
    save = 'figres/m2.png'
)

# plot model 3 
# Delta x ~ distance of x to centroid 
# here it actually looks like we have signal
# it makes sense that there would not be a strong signal for econ.
plot_question(
    df = merged_df,
    col_x = 'centroid_distance',
    col_y = 'xvalue_delta_abs',
    title = r'$|\Delta x_{a, i}| \sim |dist(x_{p, i}, x_{a, i})|_{t-1}$',
    xlab = r'$|dist(x_{p, i}, x_{a, i})|_{t-1}$',
    ylab = r'$|\Delta x_{a, i}|$',
    save = 'figres/m3.png'
)

# plot model 4 
# Delta individual ~ SD of beliefs
plot_individual(
    df = merged_df[['ID', 'xvalue_lag_std', 'xvalue_delta_abs']].drop_duplicates(),
    col_x = 'xvalue_lag_std',
    col_y = 'xvalue_delta_abs',
    title = r'$|\Delta x_{a, i}| \sim |std(x_{a, i})|$',
    xlab = r'$|std(x_{a, i})|$',
    ylab = r'$|\Delta x_{a, i}|$',
    save = 'figres/m4.png'
)


merged_df
data_2016 = data_2016.groupby(['ID'])['xvalue'].std().reset_index(name='std')
lagged_df = lagged_df.merge(data_2016, on = 'ID', how = 'inner')

centroid_2020 = complete_df[complete_df['year']==2020]
centroid_2020 = centroid_2020.groupby(['ID'])['xvalue'].mean().reset_index(name='centroid_2020')
lagged_df = lagged_df.merge(centroid_2020, on = 'ID', how = 'inner')

lagged_df['centroid_delta'] = abs(lagged_df['centroid_2020']-lagged_df['x_2016'])
lagged_unique = lagged_df[['ID', 'std', 'centroid_delta']].drop_duplicates()


lagged_df['xvalue_lag_abs'] = lagged_df['xvalue_lag'].abs()
lagged_df['xvalue_delta'] = abs(lagged_df['xvalue'] - lagged_df['xvalue_lag'])

# plot idea for first model;
import seaborn as sns 
fig, ax = plt.subplots()

sns.lineplot(
    data=lagged_df,
    x='xvalue_lag_abs', 
    y='xvalue_delta_abs', 
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
plt.tight_layout()
plt.savefig('figres/m1.png')
plt.close()

# now we can also do the average 
# like; how far do you move thing. 
average_values = complete_df.groupby(['ID', 'year'])['xvalue'].mean().reset_index(name='avg_x')
average_2016 = average_values[average_values['year']==2016]
average_2020 = average_values[average_values['year']==2020]
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
plt.tight_layout()
plt.savefig('figres/m2.png')
plt.close()

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
plt.tight_layout()
plt.savefig('figres/m3.png')
plt.close()

# absolute movement by SD of beliefs 
data_2016 = complete_df[complete_df['year']==2016]
data_2016 = data_2016.groupby(['ID'])['xvalue'].std().reset_index(name='std')
lagged_df = lagged_df.merge(data_2016, on = 'ID', how = 'inner')

centroid_2020 = complete_df[complete_df['year']==2020]
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
plt.tight_layout()
plt.savefig('figres/m4.png')
plt.close()
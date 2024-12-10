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
pos = pd.read_csv('data/anes_pos_resin.csv')

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
merged_df['centroid_'] = merged_df['average_x_2016']-merged_df['xvalue_lag']

# average values by SD of beliefs
# is it that each belief is more likely to change, or that the aggregate (individual) is more likely to change? 
data_2016 = complete_df[complete_df['year']==2016]
xvalue_2016 = data_2016.groupby(['ID'])['xvalue'].std().reset_index(name='xvalue_lag_std')
merged_df = merged_df.merge(xvalue_2016, on='ID', how='inner')

# save this data
merged_df.to_csv('data/anes_merged.csv', index=False)

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
    ax.legend(
        handles=legend_handles,
        title='Question',
        bbox_to_anchor=(1.05, 1),  # Move legend outside the plot (to the right)
        loc='upper left',          # Position at the upper-left corner of the bounding box
        borderaxespad=0            # Adjust padding
    )
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
    #save = 'figres/m1.png'
)

'''
Movement of individual question
'''

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
    #save = 'figres/m2.png'
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
    save = 'figres/m3_p2.png'
)

# plot model 4 
# Delta individual ~ SD of beliefs
plot_individual(
    df = merged_df[['ID', 'xvalue_lag_std', 'abs_x_distance']].drop_duplicates(),
    col_x = 'xvalue_lag_std',
    col_y = 'abs_x_distance',
    title = r'$|\Delta x_{a, i}| \sim |std(x_{a, i})|$',
    xlab = r'$|std(x_{p, i})|$',
    ylab = r'$|\Delta x_{p, i}|$',
    #save = 'figres/m4.png'
)

# fig 5.
# basically the same as fig 2, but with the average delta.
# so instead of ideological movement; stability.
fig2_tweak = merged_df[['ID', 'abs_x_baseline', 'xvalue_delta_abs']]
average_delta = fig2_tweak.groupby('ID')['xvalue_delta_abs'].mean().reset_index(name='average_delta')
fig2_tweak = fig2_tweak[['ID', 'abs_x_baseline']].drop_duplicates()
fig2_tweak = fig2_tweak.merge(average_delta, on='ID', how='inner')
plot_individual(
    df = fig2_tweak,
    col_x = 'abs_x_baseline',
    col_y = 'average_delta',
    title = r'$avg(|\Delta x_{a, i}|) \sim |x_{p, i}(t-1)|$',
    xlab = r'$|x_{p, i}(t-1)|$',
    ylab = r'$avg(|\Delta x_{a, i}|)$',
    #save = 'figres/m5.png'
)

fig4_tweak = merged_df[['ID', 'xvalue_lag_std', 'xvalue_delta_abs']]
average_delta = fig4_tweak.groupby('ID')['xvalue_delta_abs'].mean().reset_index(name='average_delta')
fig4_tweak = fig4_tweak[['ID', 'xvalue_lag_std']].drop_duplicates()
fig4_tweak = fig4_tweak.merge(average_delta, on='ID', how='inner')
plot_individual(
    df = fig4_tweak,
    col_x = 'xvalue_lag_std',
    col_y = 'average_delta',
    title = r'$avg(|\Delta x_{a, i}|) \sim |std(x_{a, i})|$',
    xlab = r'$|std(x_{a, i})|$',
    ylab = r'$avg(|\Delta x_{a, i}|)$',
    #save = 'figres/m6.png'
)

plot_question(
    df = merged_df,
    col_x = 'centroid_',
    col_y = 'xvalue_delta_abs',
    title = r'$|\Delta x_{a, i}| \sim |dist(x_{p, i}, x_{a, i})|_{t-1}$',
    xlab = r'$|dist(x_{p, i}, x_{a, i})|_{t-1}$',
    ylab = r'$|\Delta x_{a, i}|$',
    #save = 'figres/m3.png'
)

from numpy.polynomial.polynomial import Polynomial

# now do it for each one;
unique_question = merged_df['question'].unique()
degree = 2
colors = plt.cm.get_cmap("tab10", len(unique_question))  # Use a categorical colormap
fig, ax = plt.subplots(figsize=(7, 4))
for i, q in enumerate(unique_question): 
    df_sub = merged_df[merged_df['question'] == q]

    x = df_sub['centroid_']
    y = df_sub['xvalue_delta_abs']
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)

    # Predict values
    x_fit = np.linspace(min(x), max(x), 200)  # High resolution for a smooth curve
    y_fit = polynomial(x_fit)

    # Plot data points and fit line (label only on the line to avoid duplication)
    plt.scatter(x, y, alpha=0.02, color=colors(i))  # Scatter plot without label
    plt.plot(x_fit, y_fit, color=colors(i), label=f"{q}")  # Polynomial fit with label

# Add legend
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Questions")
plt.xlabel("Centroid")
plt.ylabel("Delta Abs")
plt.title("Polynomial Fit by Question")
plt.tight_layout()
plt.show();

# Even more naturally
# We can do both not ABS. 
merged_df['xvalue_delta'] = merged_df['xvalue']-merged_df['xvalue_lag']
plot_question(
    df = merged_df,
    col_x = 'centroid_',
    col_y = 'xvalue_delta',
    title = 'Belief Change by Centroid Distance',
    xlab = r'$x_{p, i, (t-1)}-x_{a, i, (t-1)}$',
    ylab = r'$x_{a, i, (t)}-x_{a, i, (t-1)}$',
    save = 'figres/directional.png'
)

# Probably we would have to test 
# This against a baseline, e.g. 
# How do opinions move just against
# Where the were before 
plot_question(
    df = merged_df,
    col_x = 'xvalue',
    col_y = 'xvalue_delta',
    title = 'Baseline',
    xlab = r'x(t-1)',
    ylab = r'x(t)-x(t-1)',
    save = 'figres/baseline.png'
)

unique_question = merged_df['question'].unique()
degree = 2
for q in unique_question: 
    df_sub = merged_df[merged_df['question'] == q]

    x = df_sub['centroid_']
    y = df_sub['xvalue_delta']
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)

    # Predict values
    x_fit = np.linspace(min(x), max(x), 200)  # High resolution for a smooth curve
    y_fit = polynomial(x_fit)

    # Plot
    plt.scatter(x, y, alpha=0.5) #, label="Data")
    plt.plot(x_fit, y_fit) #, label=f"Polynomial Fit (degree {degree})")
    #plt.legend()
    #plt.show()
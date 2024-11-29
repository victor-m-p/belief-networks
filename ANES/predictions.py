import numpy as np 
import pandas as pd 
import pickle 
import re

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

# now we merge
complete_df = melted_df.merge(position_df, on=['question', 'year', 'answer'], how='inner')

# create lag-lead format
sorted_df = complete_df.sort_values(by=["ID", "question", "year"]).reset_index(drop=True)

# Create lagged columns
sorted_df["year_lag"] = sorted_df.groupby(["ID", "question"])["year"].shift(1)
sorted_df["answer_lag"] = sorted_df.groupby(["ID", "question"])["answer"].shift(1)
sorted_df["xvalue_lag"] = sorted_df.groupby(["ID", "question"])["xvalue"].shift(1)

# Drop rows where lagged values are missing
sorted_df = sorted_df.dropna(subset=["year_lag", "answer_lag", "xvalue_lag"])

# Reset index for cleanliness
sorted_df = sorted_df.reset_index(drop=True)

'''
First hypothesis;
distance ~ |xvalue_lag| + (1+ID)
'''

sorted_df['xvalue_lag_abs'] = sorted_df['xvalue_lag'].abs()
sorted_df['xvalue_delta'] = abs(sorted_df['xvalue'] - sorted_df['xvalue_lag'])

# plot idea for first model;
import seaborn as sns 
sns.lineplot(
    data=sorted_df,
    x='xvalue_lag_abs', 
    y='xvalue_delta', 
    hue='question'
    )
sns.scatterplot(
    data=sorted_df,
    x='xvalue_lag_abs',
    y='xvalue_delta',
    hue='question'
)

# wait; what?
# there should only be 4 values here ...
sorted_df[sorted_df['question']=='imm'][['question', 'answer', 'xvalue_lag']].drop_duplicates()

# fit first model # 
df['ID_encoded'] = pd.Categorical(df['ID']).codes

# PyMC model
import pymc as pm 
import bambi as bmb
import arviz as az

# how do we specify priors here?
# also this is much slower than brms
# Define the priors
priors = {
    "Intercept": bmb.Prior("Normal", mu=0, sigma=10),  # Prior for the intercept
    "xvalue_lag_abs": bmb.Prior("Normal", mu=0, sigma=5),  # Prior for the fixed effect
    "1|ID": bmb.Prior("HalfNormal", sigma=2)  # Prior for the random effect SD
}

model = bmb.Model("xvalue_delta ~ xvalue_lag_abs + (1|ID)", sorted_df, family="gaussian")

# Fit the model
trace = model.fit(draws=2000, tune=1000)
az.summary(trace, var_names=['sigma', 'Intercept', 'xvalue_lag_abs'])
az.plot_trace(trace, var_names=['sigma', 'Intercept', 'xvalue_lag_abs']);


with pm.Model() as model:
    # Priors for fixed effects
    beta = pm.Normal("beta", mu=0, sigma=10)  # Fixed effect for xvalue_lag_abs
    intercept = pm.Normal("intercept", mu=0, sigma=10)  # Fixed intercept

    # Random intercepts for IDs
    sd_ID = pm.Exponential("sd_ID", 1)  # Standard deviation for ID random effects
    random_intercept_ID = pm.Normal("random_intercept_ID", mu=0, sigma=sd_ID, shape=len(df['ID_encoded'].unique()))
    
    # Linear model
    mu = (
        intercept +
        random_intercept_ID[df["ID_encoded"]] +
        beta * df["xvalue_lag_abs"]
    )

    # Likelihood
    sigma = pm.Exponential("sigma", 1)  # Error standard deviation
    likelihood = pm.Normal("xvalue_diff", mu=mu, sigma=sigma, observed=df["xvalue_diff"])
    
    # Sampling
    trace = pm.sample(2000, tune=1000, return_inferencedata=True)



# find average xvalue for each individual in 2016 and 2020
average_x = complete_df.groupby(['ID', 'year'])['xvalue'].mean().reset_index(name='xavg')
complete_df = complete_df.merge(average_x, on = ['ID', 'year'], how = 'inner')



# fit models  


# okay look at the average thing first # 
agg_df = complete_df.groupby(['ID', 'year']).agg({'xvalue': 'mean'}).reset_index()
import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np

# load GESIS data
data = pd.read_stata("data/data/stata/ZA5665_a1_v54-0-0.dta", convert_categoricals=False)

# begin to find variables; 
# climate change.
clch_waves= ["bczd035a", "cczd032a", "dczd032a", "eczd032a",  "fczd032a", "hczd031a", "ibzd031a", "jbzd031a", "kbzd030a"]
d_cl = data[clch_waves]

# accepted questions 
non_nan = [x+1 for x in range(11)]
d_cl = d_cl.map(lambda x: x if x in non_nan else np.nan)

# the scale changed 
# so only take the ones that have 11 as max.
max_val = d_cl.max().reset_index(name='max') # has to be 11 I guess.
valid_cols = max_val[max_val['max']==11]['index'].tolist()
d_cl = d_cl[valid_cols]

# remove the ones that have 7 as max 
d_cl.isna().sum() # should always grow; and does.
d_cl = d_cl.dropna()

# 1: climate change not serious at all
# 11: extremely serious 
dates = []
for col in d_cl.columns:
    id = col[:2]
    data[id+'zp205a'] = pd.to_datetime(data[id+'zp205a'], errors='coerce')
    valid_dates = data[id+'zp205a'].dropna()
    mean_date = valid_dates.mean().strftime('%Y')
    dates.append(mean_date)
colnames = ['clch-'+date for date in dates]

d_cl = d_cl.rename(columns=dict(zip(d_cl.columns, colnames)))


# interested in politics;
pol_waves = ['bbzc001a', 'cbzc001a', 'dbzc001a', 'dfbo057a', 'ebzc001a', 'ecbo080a', 'efbo051a', 'f12c009a', 'fbzc001a', 'fcbo107a', 'gbzc001a']
d_pol = data[pol_waves]
nan_responses = [-11, -22, -33, -77, -99, -111]
d_pol

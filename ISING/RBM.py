import pandas as pd 
import numpy as np 
import itertools
from sklearn.neural_network import BernoulliRBM

# try to fit RBM to Ising data 
data = pd.read_csv('sim_data/nodes_5_obs_1000_normal.csv')
X = data.to_numpy()

# setup 
n_visible = 5
n_hidden = 2

model = BernoulliRBM(
    n_components=n_hidden,
    n_iter = 100,
    learning_rate = 0.1,
    batch_size = 10)
model.fit(X)

# 
model.components_ # are these the couplings? 
model.intercept_hidden_ # okay so both tend to be inactive? 
model.intercept_visible_ # bias: so how likely is the node in absence of latent

# calculate p 
W = model.components_ # couplings 
b = model.intercept_visible_ # bias for visible units
c = model.intercept_hidden_ # bias for hidden units 

# list of all possible states
visible_states = list(itertools.product([0, 1], repeat=n_visible))
hidden_states = list(itertools.product([0, 1], repeat=n_hidden))

unnormalized_p = []  # Will store sum_h exp(-E(v,h)) for each visible state v

# ennumerate 
for v in visible_states:
    v_arr = np.array(v)
    sum_over_h = 0.0
    for h in hidden_states:
        h_arr = np.array(h)
        
        # Compute energy E(v,h)
        vh_interaction = v_arr @ W.T @ h_arr
        E_vh = -(vh_interaction + v_arr @ b + h_arr @ c)
        
        # Probability factor: exp(-E(v,h))
        prob_factor = np.exp(-E_vh)
        sum_over_h += prob_factor
    
    unnormalized_p.append(sum_over_h)

# Partition function Z is sum over all v and h
Z = sum(unnormalized_p)

# Probability of each visible state
P_v = [val / Z for val in unnormalized_p] # okay does sum to 1. 

# create dataframe from this 
df_states = pd.DataFrame(visible_states, columns=[f'Q{n+1}' for n in range(n_visible)])
df_states['p'] = P_v

# check this against observed frequencies 
df_obs = data.groupby([f'Q{n+1}' for n in range(n_visible)]).size().reset_index(name='count')
df_merged = df_states.merge(df_obs, on = [f'Q{n+1}' for n in range(n_visible)], how = 'inner')
df_merged.sort_values('p', ascending = False) # not terrible honestly. 

# what is a good metric of performance? 
df_merged['freq'] = df_merged['count'] / df_merged['count'].sum()

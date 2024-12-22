import numpy as np
import pandas as pd 
from fun import *
import networkx as nx
import seaborn as sns 
from configuration import Configuration

# load data 2016
fields_2016, couplings_2016 = load_mpf_params(
    n_nodes=6,
    path="mpf/anes_2016.txt_params.dat"
)

# probabilities
configs = bin_states(6)
configs[configs < 0] = 0
p_2016 = p_dist(fields_2016, couplings_2016)

# get all basins 
Conf2016 = Configuration(
    identifier = 0, # does not matter here 
    states = configs, 
    probabilities = p_2016
)

basin_2016 = Conf2016.find_all_basins()

# check maxima for 2016
basin_2016[0] # local maxima (all conservative)
basin_2016[6] # conservative +imm (less hard-line) +tax (favor)
basin_2016[63] # local maxima (all liberal)

# do 2020 as well 
fields_2020, couplings_2020 = load_mpf_params(
    n_nodes = 6,
    path = 'mpf/anes_2020.txt_params.dat'
)
p_2020 = p_dist(fields_2020, couplings_2020)

Conf2020 = Configuration(
    identifier = 0, # does not matter here
    states = configs,
    probabilities = p_2020
)

basin_2020 = Conf2020.find_all_basins()

# for 2020 we have only 2 basins (strict conservative + liberal)
# there might be something interesting if we had longer-time data
# where we can look at this over time. 

# okay plot this for 2016 if we can  
anes_2016 = pd.read_csv('mpf/anes_2016_wide.csv')

# connect hamming neighbors

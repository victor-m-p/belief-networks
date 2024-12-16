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

ConfObj = Configuration(
    identifier = 0,
    states = configs, 
    probabilities = p_2016
)

# actual data 
anes_2016 = pd.read_csv('mpf/anes_2016_wide.csv')

local_maxima, basin_map = ConfObj.find_all_local_maxima()
local_maxima # 0, 4, 6, 47, 63 
configs[0] # pure conservative
configs[4] # conservative +imm
configs[2]

basin_map

#### look a bit at individual transitions ####
# e.g., how many 0-bit flips, how many 1-bit flips, etc. 
# stability ~ how probably the state is 


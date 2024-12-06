import numpy as np 
import json 
import os
from fun import *
import matplotlib.pyplot as plt 

# basic setup  
folder_path = 'sim_data'
n_nodes = 5
n_couplings = n_nodes * (n_nodes - 1) // 2
n_obs = 1000
states = bin_states(n_nodes)

# --- load ground truth --- # 
def load_params(path): 
    with open(path, 'r') as f:
        data = json.load(f)
        
    p = np.array(data["probabilities"])
    fields = np.array(data["local_fields"])
    couplings = np.array(data["pairwise_couplings"])
    
    return p, fields, couplings

path_ising = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_ising.json')
path_normal = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_normal.json')

ising_p, ising_fields, ising_couplings = load_params(path_ising)
normal_p, normal_fields, normal_couplings = load_params(path_normal)

# ---- load mpf data ---- #

mpf_ising = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_ising.txt_params.dat')
mpf_normal = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_normal.txt_params.dat')

mpf_ising_p, mpf_ising_fields, mpf_ising_couplings = load_mpf_params(mpf_ising)
mpf_normal_p, mpf_normal_fields, mpf_normal_couplings = load_mpf_params(mpf_normal)

# plot mpf # 
plot_params(normal_fields, normal_couplings, mpf_normal_fields, mpf_normal_couplings)
# definitely we are missing some of the shrinkage (lasso)
plot_params(ising_fields, ising_couplings, mpf_ising_fields, mpf_ising_couplings)
# still, the probabilities are excellent, so maybe this is just underdetermined
# need to figure out exactly how we penalize 
plot_probabilities(normal_p, mpf_normal_p)
plot_probabilities(ising_p, mpf_ising_p)

# now do IsingFit
def load_ifit_params(path): 
    with open(path, 'r') as f:
        ifit_data = f.readline().strip()
        
    ifit_params = np.array(ifit_data.split(), dtype=float)
    ifit_couplings = ifit_params[:n_couplings]
    ifit_fields = ifit_params[n_couplings:]
    ifit_p = p_dist(ifit_fields, ifit_couplings) # okay getting an error here..?
    
    return ifit_p, ifit_fields, ifit_couplings

ifit_ising = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_ising_IsingFit.dat')
ifit_normal = os.path.join(folder_path, f'nodes_{n_nodes}_obs_{n_obs}_normal_IsingFit.dat')

ifit_ising_p, ifit_ising_fields, ifit_ising_couplings = load_ifit_params(ifit_ising)
ifit_normal_p, ifit_normal_fields, ifit_normal_couplings = load_ifit_params(ifit_normal)

plot_params(normal_fields, normal_couplings, ifit_normal_fields, ifit_normal_couplings)
plot_params(ising_fields, ising_couplings, ifit_ising_fields, ifit_ising_couplings)
plot_probabilities(normal_p, ifit_normal_p)
plot_probabilities(ising_p, ifit_ising_p)
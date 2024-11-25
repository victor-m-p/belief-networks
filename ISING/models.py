import numpy as np 
import pandas as pd 

'''
Simple version.
Fully connected belief network (only personal)
'''

'''
Key questions
1. How do we build it? (remember this as hard problem)
2. Can I just choose values? (no, right because the total probability must be 1)
'''

# personal beliefs 
n_nodes = 3 
n_couplings = int(n_nodes * (n_nodes - 1) / 2)
personal_beliefs = np.random.uniform(-1, 1, n_nodes) # likert or continuous?  

# social beliefs 


# not clear to me what the scale should be here,
# local fields and pairwise couplings relative to 
# B_{pers}. 
local_fields = np.random.uniform(-1, 1, n_nodes)

# okay question is how to actually store these
# this is a bit redundant but could be nice 
def create_symmetric_matrix(size, values): 
    matrix = np.eye(size)
    index = 0
    for i in range(size): 
        for j in range(i+1, size): 
            matrix[i, j] = values[index]
            matrix[j, i] = values[index]
            index += 1
    return matrix

pairwise_couplings = np.random.uniform(-1, 1, n_couplings)
pairwise_couplings = create_symmetric_matrix(n_nodes, pairwise_couplings)

social_beliefs = np.random.uniform(-1, 1, n_social)
social_couplings = np.random.uniform(-1, 1, n_social)

# okay so for the i that we care about,
# we need to know all the j connected 
# beliefs. for now we will just do fully connected
def H_pers(local_fields: np.ndarray, pairwise_couplings: np.ndarray, personal_beliefs: np.ndarray) -> float:
    H_pers = 0
    for i in range(n_nodes): 
        H_pers += -local_fields[i] * personal_beliefs[i] 
        for j in range(n_nodes): 
            H_pers += -pairwise_couplings[i, j] * personal_beliefs[i] * personal_beliefs[j]
    return H_pers

# okay now we get a value at least. 
def D_pers(b_pers, h_pers, b_soc, h_soc): 
    return b_pers * h_pers + b_soc * h_soc

# consider whether we could do this as a crazy class instead. 
def H_soc(perception: np.ndarray, personal_beliefs: np.ndarray, social_couplings: np.ndarray) -> float:
    H_soc = 0
    for i in range(n_nodes): 
        H_soc += -perception[i] * personal_beliefs[i]
        for j in range(n_nodes): 
            H_soc += -social_couplings[i, j] * personal_beliefs[i] * personal_beliefs[j]
    return H_soc

# TODO: 
# agree on terminology (e.g. $p_ik$ in H_soc)
from ISING.fun import *

# setup  
n_nodes = 3
n_couplings = n_nodes * (n_nodes - 1) // 2 

# okay so maybe we can just choose here 
local_fields = np.random.normal(0, 1, n_nodes)
couplings = np.random.normal(0, 1, n_couplings)

# okay now we need to go forward
p = p_dist(local_fields, couplings) # forward pass 
states = bin_states(n_nodes)

# small experiment 
# okay so create this artificial example 
h = np.array([0, 0, 0, 0]) # A, B, C
J = np.array([1, 1, 0, -1, 0, 0]) # (AB, AC, AD, )
p = p_dist(h, J)
states = bin_states(4) # yes so this gives us Peter's idea. 
p # yes so this gives us Peter. 
states

# now we flip one.
h_new = np.array([0, 0, 0])
J_new = np.array([1, 1, -1]) # Wait, still balanced?
p_new = p_dist(h_new, J_new) # yes so this gives us Peter.
states = bin_states(3)
p_new
states

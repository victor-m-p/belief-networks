from fun import *

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
h = np.array([0.5, 0, -0.5]) # A, B, C
J = np.array([0.5, 0.5, 0.5]) # (AB, AC, BC)
p = p_dist(h, J)
states = bin_states(3) # yes so this gives us Peter's idea. 
p # yes so this gives us Peter. 

# now we flip one.
h_new = np.array([-0.5, 0, -0.5])
J_new = np.array([-0.5, -0.5, 0.5]) # Wait, still balanced?
p_new = p_dist(h, J) # yes so this gives us Peter.
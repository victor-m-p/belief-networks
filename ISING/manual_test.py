from fun import *
n_nodes = 3
states = bin_states(n_nodes)
h = np.array([-0.8, 0, -0.8])
J = np.array([0, 1.6, 0])
p = p_dist(h, J) # we disagree about p
np.round(p, 3)

'''
000: 0.473
001: 0.004
010: 0.473
011: 0.004
100: 0.004
101: 0.019
110: 0.004
111: 0.019
'''

h = np.array([0, 0, 0])
J = np.array([0, 1.6, 0])
p = p_dist(h, J) # we disagree about p
p # also not quite what they have though but close. 
import pandas as pd 
import numpy as np
from fun import *

def generate_allowed_states(group_sizes):
    # Generate all valid rows for each group
    group_states = []
    for size in group_sizes:
        # Create all combinations where exactly one element is 1
        group = []
        for i in range(size):
            state = np.full(size, -1)
            state[i] = 1
            group.append(state)
        group_states.append(group)

    # Generate all possible combinations using the Cartesian product
    all_combinations = itertools.product(*group_states)

    # Combine the groups for each combination
    allowed_rows = []
    for combination in all_combinations:
        allowed_rows.append(np.concatenate(combination))

    # Convert to NumPy array
    return np.array(allowed_rows)

# load params 
path = 'ANES/anes_2016.txt_params.dat'
n_nodes = 7
fields, couplings = load_mpf_params(7, path)
p = p_dist(fields, couplings)
states = bin_states(7)
allowed_states = generate_allowed_states([3, 4])

# also load the data
anes_2016 = pd.read_csv('ANES/anes_2016.csv')

# focus on p for now
colnames = anes_2016.columns.tolist()
colnames = colnames[:-1] # remove weight
df_p = pd.DataFrame(p, columns=['p'])
df_c = pd.DataFrame(states, columns=colnames)
df_pc = pd.concat([df_p, df_c], axis=1)
df_pc['p'] = df_pc['p'].round(3)

# check whether the states are valid
# now instead we have to check whether each row is in the allowed states
df_pc['valid'] = valid_rows

# now we sort it 
df_pc = df_pc.sort_values('p', ascending=False)
df_valid = df_pc[df_pc['valid'] == True]
df_valid['p'].sum() # 88.2% of the probability mass 

''' the most favored states
gay marry, imm stay: >50% 
gay union, imm stay: 8.6%
gay marry, imm cit: 4.3%
gay marry, imm restrict: 4.3%
gay no, imm stay: 4.3%
gay marry, imm dep: 3.7%
gay no, imm dep: 1.5%
'''

df_valid['p_reweight'] = df_valid['p'] / df_valid['p'].sum()

''' reweighting this we get: 
65.4% <- why is the top one so high? 
9.75%
4.88%
4.88%
4.88%
4.2%
1.7%
...
'''

# check the actual top frequencies
anes_2016 = anes_2016.drop(columns='weight')
anes_2016 = anes_2016.groupby(colnames).size().reset_index(name='count')
anes_2016['p'] = anes_2016['count'] / anes_2016['count'].sum()
anes_2016.sort_values('p', ascending=False)

''' frequencies: 
gay marry, imm stay: 37.4%
gay union, imm stay: 13.2%
gay marry, imm cit: 9.12%
gay no, imm stay: 7.8%
gay marry, imm rest: 7.5%
gay marry, imm dep: 6.3%
'''

# plot p observed vs actual frequency
# (maybe just for the real states)
# (could also include the others just lower alpha)
# need to be able to enumerate the possible states


# also, actually can we do some prediction now?
# like we have a measure of p
# and we can make a distance measure
# 1) number of flips
# 2) distance of flips (like hamming)

# okay, calculate distance
# way 1: n changed beliefs
# way 2: total distance
# --> but then we are back to treating them as equally far
# --> that might be really weird 
# --> question is whether that now is "in" the model somehow
# --> i.e. in the $p$ 
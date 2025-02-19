import pandas as pd 
import json

# load data
participant_id = 18
with open(f'data/personal_nodes_{participant_id}.json') as f:
        personal_nodes = json.loads(f.read())


''' personal beliefs
H_pers = -sum h_i b_i -sum J_ij b_i b_j

question is: 
1. what is h_i in our model? 
2. what is J_ij in our model? 

like we ask how important each belief is. 
but I think that it is a little difficult
whether this gives us 

a) the importance of the belief in general
b) the strength of coupling to focal 

Seems equally plausible to interpret in either way.
I am not sure that we are plausibly separating these two. 

also we have attention. 
attention should probably be [0, 1] and
attached to the node like: 

H_pers = -sum h_i ab_i -sum J_ij a_bi a_bj
'''



hi = 1 # we do not know right now

H_pers = 0 

''' social beliefs
H_soc = -sum p_ik b_i s_ik

Question is whether we can approximate p_ik 
by just the overall importance of the person (k).
I think we can, so we have this, basically. 

This is again really hard for us. 
We do not actually have what we need here.
I have basically assumed that friends *must* agree with you.
This is not a good assumption.

'''

# gather all 

H_soc = 0
nodes['s_1_1']
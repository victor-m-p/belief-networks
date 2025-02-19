import pandas as pd 
import json
import numpy as np 

# load data
participant_id = 17
with open(f'data/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())

# sum over edges
# here I first average the couplings.
personal_nodes = metadict['personal_nodes']
personal_edges = metadict['personal_edges']
social_nodes = metadict['social_nodes']

### first just do the most stupid model ### 
personal_energy = [val['importance_scaled'] * val['value_num'] for key, val in personal_nodes.items() if val['type'] == 'personal_belief' and val['level'] == 1]
personal_energy = sum(personal_energy)

social_energy = [val['importance_scaled'] * val['value_num'] for key, val in social_nodes.items() if val['type'] == 'social_belief' and val['level'] == 0]
social_energy = sum(social_energy)

# outcomes
behavior_outcome = personal_nodes['b_focal']['value_num']

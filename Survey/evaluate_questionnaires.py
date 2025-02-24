import numpy as np 
import pandas as pd 
import json

# gather data in appropriate format # 
participant_id = 16
with open(f'data/human_clean/metadict_{participant_id}.json') as f:
    metadict = json.loads(f.read())
    

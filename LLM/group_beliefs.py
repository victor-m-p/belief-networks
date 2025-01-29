from openai import OpenAI
import os 
from dotenv import load_dotenv
import json 
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from fun import load_and_clean, replacements, 
import pandas as pd 
import itertools

# structure the data
# load data 
inpath = 'data_output'
takers = os.listdir(inpath)
taker = takers[0]

def collect_beliefs(inpath, taker, replacements): 
    with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)
        id = data['id']
        nodes = load_and_clean(data['answer_1'], replacements)
        nodes = [y for x, y, z, w in nodes]
    return id, nodes 

belief_dict = {}
for taker in takers: 
    id, belief_nodes = collect_beliefs(inpath, taker, replacements)
    belief_dict[id] = belief_nodes

# okay now see how well we can group these # 
# collect this just as a list now: 
belief_list = list(belief_dict.values())
belief_list = list(itertools.chain.from_iterable(belief_list))

# prompt 
p0 = """ 

"""

# this also needs to be split up: 
# like "nationalism" (then anti is the direction).


# now next step is formulating these into individual beliefs # 

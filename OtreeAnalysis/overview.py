import pandas as pd 
import numpy as np 
import json 
import os 
import textwrap

# meta variables
session = '2025-06-24'

# load data
with open(f'data_clean/prolific/data_{session}.json', 'r') as f:
    data = json.load(f)

# participant keys 
keys = [key for key, _ in data.items()]
p = data[keys[0]] # first participant

# demographics 
ages = [data[key]['demographics']['age'] for key in keys]
genders = [data[key]['demographics']['gender'] for key in keys]
edu = [data[key]['demographics']['education'] for key in keys]
pol = [data[key]['demographics']['politics'] for key in keys]
state = [data[key]['demographics']['state'] for key in keys]
zipcode = [data[key]['demographics']['zipcode'] for key in keys]

# prompts
# problem: saved without line breaks.
for key in keys: 
    with open(f"data_clean/prompts/{session}_{key}.txt", "w") as f:
        f.write(data[key]['LLM']['prompt'])
    
# for now save answers then
# what should we do for questions?
for key in keys:
    a1 = textwrap.fill(data[key]['answers']['answer1'], width=40)
    a2 = textwrap.fill(data[key]['answers']['answer2'], width=40)
    a3 = textwrap.fill(data[key]['answers']['answer3'], width=40)
    a4 = textwrap.fill(data[key]['answers']['answer4'], width=40)
    
    answers = [a1, a2, a3, a4]
    answer_string = "\n\n".join(answers)

    with open(f'data_clean/answers/{session}_{key}.txt', "w") as f:
        f.write(answer_string)

# meat scale (analyze later, looks good) 
data[keys[0]]['meat_scale']
data[keys[1]]['meat_scale']

# meat social (analyze later, looks good)
data[keys[0]]['meat_social']
data[keys[1]]['meat_social']

### RATINGS ###
## NODES 
# very different from these two people with n=7, n=16
# should we have a cutoff (e.g., maximum n=15)
len(data[keys[0]]['nodes']['generated']) # n=7
len(data[keys[1]]['nodes']['generated']) # n=16

ratings0 = [int(i['rating']) for i in data[keys[0]]['nodes']['ratings']]
ratings1 = [int(i['rating']) for i in data[keys[1]]['nodes']['ratings']]
averages = [
    np.average(ratings0),
    np.average(ratings1)
] # check that node 4 is not included.

## NETWORK 
# both VERY WELL
# scale up to 5?
data[keys[0]]['network_rating']
data[keys[1]]['network_rating']

# super good reflections from second person
data[keys[0]]['network_reflection']
data[keys[1]]['network_reflection'] # LLM?

### ATTENTION ### 
'''
Makes sense, the one with more nodes,
and more mixed about the space has higher
attention to both parts of the network.

I wanted to use this more to scale the two
parts, but also there should be some correlation
between reported attention and constraint / number nodes.
'''
data[keys[0]]['attention']
data[keys[1]]['attention']
import numpy as np
import pandas as pd 
import networkx as nx 
import json 
import os 
import re 
import ast 

inpath='data_output'
taker='vmp.json'
with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)
        
couplings = data['answer_3']

cleaned_string = re.sub(r"\s+", " ", couplings).strip()
cleaned_string

lst = ast.literal_eval(cleaned_string)
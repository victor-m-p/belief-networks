import numpy as np 
import pandas as pd 
import pickle

with open("raw/df_ddo_including_only_truebeliefs_nodup(N192307).p", "rb") as f:
    data = pickle.load(f)


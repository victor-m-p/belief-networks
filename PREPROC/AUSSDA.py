import numpy as np 
import pandas as pd 

# read data from AUSSDA.
aussda = pd.read_stata('../AUTNES/data/10055_da_en_v3_0.dta')

# read data from GESIS
gesis = pd.read_stata('../AUTNES/gesis/ZA5859_en_v2-0-1.dta')

# check how many columns overlap between these?
aussda_colnames = set(aussda.columns)
gesis_colnames = set(gesis.columns)
overlap = aussda_colnames.intersection(gesis_colnames)
len(overlap) # n=66 which is not a lot (are there more that have e.g., changed name?)

# let us first do identification
aussda['resp_id'].nunique() # 4011.

# seems like none of these questions are in all waves. 
# 1) pre-election and post-election survey (W1: 2013, W2: 2013)
# 2) Inter-election (W3: 2015) 

# recode columns
columns_rename = {
    # Most important issue (no/yes)
    "w2_q2": "w2_q5",
    "w3_q3": "w3_q5",
    # Most important issue (text)
    "w2_q2txt": "w2_q5txt",
    "w3_q3txt": "w3_q5txt",
    # Most important issue (coding)
    "w2_q2x1": "w2_q5x1",
    "w3_q3x1": "w3_q5x1",
    # Party best able to handle most important issue
    "w2_q3": "w2_q6",
    "w3_q4": "w3_q6",
}

# select columns we want to work wth
columns_single = [
    'resp_id', # although should be coded "admr"
    'date', # date of interview
    'intnr', # interview number
    'i1', # R command german (0: bad, 10: good) 
    'i2', # R answer well (1: yes, 5: no)--and in-betweens
    'w1_q1', # austrian citizenship
    'w1_q2', # number (there is also month if we care)
    'w1_q4', # gender 
    'w2_q7', # turnout 2013 election (could code to 0/1)
    'w3_q14', # voted in 2013 election 
]

# wave questions 
wave_questions = [
    'q5x1',
    'q6',
    
    ]

n_waves = 3
columns_multiple = [f'w{i}_{item}' for item in wave_questions for i  in range(1, n_waves+1)]

# other cool columns for later
other_cols = [
    'w1_q5', # most important issue stated
    'w1_q5txt', # most important issue stated (text)
    'w1_q5x1', # most overall coding (there is more resolution possible)
    'w1_q6', # party best able to handle most imp. issue
]

aussda['w1_q6']

gesis['resp_id'].nunique() # omg.
gesis.columns

# so the problem is that 
aussda['resp_id'].nunique() # 4011. 
test_id = aussda[aussda['za_nr']]
aussda['w2_month'].unique()
gesis['za_nr'].unique()
aussda[]
aussda['w2_month']
aussda['week']


gesis['w1_q5']
gesis['w2_q2']
gesis['w3_q3']
gesis['w1_q5x1']

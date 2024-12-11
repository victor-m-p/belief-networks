import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np

# year mapping 
year_mapping = {
    'a': 2013,
    'b': 2014,
    'c': 2015,
    'd': 2016,
    'e': 2017,
    'f': 2018,
    'g': 2019,
    'h': 2020,
    'i': 2021,
    'j': 2022,
    'k': 2023
}

def colnames(d, var, year_mapping): 
    d = d.rename(columns={col: f"{var}-{year_mapping[col[0]]}" for col in d.columns})
    return d 

def clean_waves(data, cols, var, mapping): 
    d = data[cols]
    d = colnames(d, var, mapping)
    d = d.map(lambda x: x if x > 0 else np.nan)
    return d

# load GESIS data
data = pd.read_stata("data/data/stata/ZA5665_a1_v54-0-0.dta", convert_categoricals=False)

# begin to find variables; 
# climate change.
clch_waves= ["bczd035a", "cczd032a", "dczd032a", "eczd032a",  "fczd032a", "hczd031a", "ibzd031a", "jbzd031a", "kbzd030a"]

d_cl = clean_waves(data, clch_waves, 'climate' year_mapping)

# the scale changed 
# so only take the ones that have 11 as max.
max_val = d_cl.max().reset_index(name='max') # has to be 11 I guess.
valid_cols = max_val[max_val['max']==11]['index'].tolist()
d_cl = d_cl[valid_cols]

# remove the ones that have 7 as max 
d_cl.isna().sum() # should always grow; and does.
d_cl = d_cl.dropna()

# interested in politics "overall attention"
# okay here you have multiple waves within one year
pol_waves = ['a12c009a', 'bbzc001a', 'cbzc001a', 'd12c010a', 'dbzc001a', 'dfbo057a', 'ebzc001a', 'ecbo080a', 'efbo051a', 'f12c009a', 'fbzc001a', 'fcbo107a', 'gbzc001a']
d_pol = clean_waves(data, pol_waves, year_mapping)
d_pol.isna().sum()

# remove cases where the pattern breaks 
# should always be more nan in newer waves 
# something weird about the ones that have numbers 
# as the second thing ...?

## ---- trust in Bundestag ---- ##
# actually, because this is in these waves, maybe we can do the embedding thing with this? 
# if we just take all variables that are in all waves? 


# bundestag, political parties, politicians, etc. 
trust_bundestag = [
    'bbzc078a',
    'cbzc049a',
    'dbzc049a',
    'ebzc049a',
    'fbzc053a',
    'gbzc053a',
    'hbzc032a',
    'iazc057a',
    'jazc057a',
    'kazc057a'
]
x = clean_waves(data, trust_bundes, 'tbunde', year_mapping)
x.isna().sum() 

trust_politicians = [
    'bbzc083a',
    'cbzc054a',
    'dbzc054a', 
    'ebzc054a',
    'fbzc058a',
    'gbzc058a',
    'hbzc037a',
    'iazc062a',
    'jazc062a',
    'kazc062a'
]

trust_police = [
    'bbzc082a',
    'cbzc053a',
    'dbzc053a',
    'ebzc053a',
    'fbzc057a',
    'gbzc057a',
    'hbzc036a',
    'iazc061a',
    'jazc061a',
    'kazc061a'
]

trust_media = [
    'bbzc084a',
    'cbzc055a',
    'dbzc055a',
    'ebzc055a',
    'fbzc059a',
    'gbzc059a',
    'hbzc038a',
    'iazc063a',
    'jazc063a',
    'kazc063a'
]

general_trust = [
    'bbzc088a',
    'cbzc059a',
    'dbzc059a',
    'ebzc059a',
    'fbzc052a',
    'gbzc052a',
    'hbzc031a',
    'iazc056a',
    'jazc056a',
    'kazc056a'
]

# humans have a right to modify environment
modenv = [
    'bczd006a',
    'cczd003a',
    'dczd003a',
    'eczd003a',
    'fczd003a',
    'gczd003a',
    'hczd002a',
    'ibzd002a',
    'jbzd002a',
    'kbzd002a'
]

# when humans interfere with nature, bad things happen
badint = [
    'bczd007a',
    'cczd004a',
    'dczd004a',
    'eczd004a',
    'fczd004a',
    'gczd004a',
    'hczd003a',
    'ibzd003a',
    'jbzd003a',
    'kbzd003a',
]

# human ingenuity will ensure that earth stays habitable
ingenuity = [
    'bczd008a',
    'cczd005a',
    'dczd005a',
    'eczd005a',
    'fczd005a',
    'gczd005a',
    'hczd004a',
    'ibzd004a',
    'jbzd004a',
    'kbzd004a'
]

# humans are severely abusing the environment
envabuse = [
    'bczd009a',
    'cczd006a',
    'dczd006a',
    'eczd006a',
    'fczd006a',
    'gczd006a',
    'hczd005a',
    'ibzd005a',
    'jbzd005a',
    'kbzd005a'
]

# many more of these, just taking a few ... 
plantanimalrights = [
    'bczd011a',
    'cczd008a',
    'dczd008a',
    'eczd008a',
    'fczd008a',
    'gczd008a',
    'hczd007a',
    'ibzd007a',
    'jbzd007a',
    'kbzd007a'
]

envcrisisexag = [
    'bczd014a',
    'cczd011a',
    'dczd011a',
    'eczd011a',
    'fczd011a',
    'gczd011a',
    'hczd010a',
    'ibzd010a',
    'jbzd010a',
    'kbzd010a'
]

envcatastrophe = [
    'bczd019a',
    'cczd016a',
    'dczd016a',
    'eczd016a',
    'fczd016a',
    'gczd016a',
    'hczd015a',
    'ibzd015a',
    'jbzd015a',
    'kbzd015a'
]

# willingness to pay higher prices for env 
envprices = [
    'bczd020a',
    'cczd017a',
    'dczd017a',
    'eczd017a',
    'fczd017a',
    'gczd017a',
    'hczd016a',
    'ibzd016a',
    'jbzd016a',
    'kbzd016a'
]

# willingness to pay higher taxes for env
envtaxes = [
    'bczd021a',
    'cczd018a',
    'dczd018a',
    'eczd018a',
    'fczd018a',
    'gczd018a',
    'hczd017a',
    'ibzd017a',
    'jbzd017a',
    'kbzd017a'
]

# willingness to lower standard of living for env
envlivstand = [
    'bczd022a',
    'cczd019a',
    'dczd019a',
    'eczd019a',
    'fczd019a',
    'gczd019a',
    'hczd018a',
    'ibzd018a',
    'jbzd018a',
    'kbzd018a'
]

# made it to page 1113 

## ----- Wichtigstes Problem in Deutschland ------ ##
'''
Basically useless, we only have 2 waves (2013, 2016)
and in 2016 we have all nan (most -11; not invited)
'''

importance_waves = [
    'a12c004a', # wichtigstes (2013)
    'd12c004a', # wichtigstes (2016)
    ]
d_importance = clean_waves(data, importance_waves, 'importance', year_mapping)
d_importance.isna().sum() 

# Immigration opinions

# Norms of citizenship
'''
1-7 on importance of solidarity. 
More civic duty questions (the "related" ones). 
'''

solidarity_waves = [ # there are also some within-waves
    'bbzc071a',
    'cbzc042a',
    'dbzc042a',
    'ebzc042a',
    'fbzc045a',
    'gbzc045a',
]
d_solidarity = clean_waves(data, solidarity_waves, 'solidarity', year_mapping)
d_solidarity.isna().sum()

# many of these questions are pretty weird
'''
1: very acceptable
5: not acceptable 
(same in all waves)
'''
envtax_waves = [
    'bczd021a',
    'cczd018a',
    'dczd018a',
    'eczd018a',
    'fczd018a',
    'gczd018a',
    'hczd017a',
    'jbzd017a',
    'kbzd017a'
]
d_envtax = clean_waves(data, envtax_waves, 'envtax', year_mapping)
d_envtax.isna().sum()

# Does look like several of these are in the same 
# Two years though, so maybe we could do something still.

# Demographics 
# a11d054a (gender)
# a11d056a (year of birth)
# a11d089b (employment situation)
# a11d096a (income) 

# other potentials:
# bazb002a (happiness)
# how important do you consider: 
## own family (bazb007a)
## work (bazb008a)
## freizeit (bazb009a)
## friends (bazb010a)
## ...
# bazb019a (depression)

# something action, e.g. 
# bbzc002a (contacted politician)
# bbzc006a (boycottet products, or bought specific ones)
# bbzc008a (discussed politics with friends)--attention?

# choice of party
# bbzc020a (election next Sunday, what would you vote?)

'''
1: CDU/CSU
2: SPD
3: FDP
4: Die Linke
5: Die Grünen
6: AfD
7: Other 
97: Cannot vote
98: Don't know 
'''

# bbzc022a (frequency political news, 1-7)
# bbzc031a (used internet to express my opinion) + bbzc032a (discuss politics)
# more of this as well ....

# bbzc045a (church going)
# bbzc046a (art, music, culture)
# bbzc047a (social movement)
# bbzc048a (political party)
# ... 
# bbzc064a (how important is politics in your life?); also religion, etc. 
# bbzc068a (easy to form political opinions)
# bbzc077a (subject own opinions to critical examination)



# ....
# need to log information if the LLM fails
import pandas as pd 
df = pd.read_csv('prolific/PageTimes-2025-06-24.csv')
df.groupby('page_name').size()

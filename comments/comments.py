import numpy as np 
import pandas as pd 

df = pd.read_parquet('2012-06-01.parquet')
df.sort_values('_id')
df['_id'].nunique() # 112 (same as rows, so no users with >1 comment?)
df['clean_title'].nunique() # 111 (okay so _id must be user.)

'''
Okay so here we mostly have embedding, sentiment, topics.
'''

# topic overview
topics = pd.read_csv('thehill.csv')
topics.drop(columns=['Unnamed: 0'], inplace=True)
topics # 258 topics 

# what, but I do not have commentor ID here?
pd.set_option('display.max_colwidth', None)
comments = pd.read_csv('raw_comment_sample_thehill_20120601.csv')
comments

# is article ID in "comments" the same as "_id" in "df"?
# otherwise, we cannot really link anything.
# but seems like it should not be possible, because
# we have one article in "df" with two different IDs. 
# so presumably that is the comment ID?
comments['article_id'].nunique() # 77
df['_id'].nunique() # 112 
df['_id'] = df['_id'].astype(int)
merged = df.merge(comments, left_on='_id', right_on='article_id', how='inner')
merged['_id'].nunique() # 77 (hmmm okay...?)

# okay find an interesting article with some traction

merged.groupby('clean_title').size().reset_index(name='count').sort_values('count').tail(15)
merged_case = merged[merged['clean_title'].str.contains('Romney worth between')]
merged_case[['clean_title', 'comment']].head(10)

'''
So already really clear what the narratives are: 
Romney is rich (the fact)
The key things we are then discussing (to evaluate Romney) is what this means. 
- selfmade? (implicitly: we do not respect inherited money)
- good businessman? (and does that translate to good president?)
- rich old white ceo (implicitly: out of touch)
- obama is also rich (shifting attention). 
'''
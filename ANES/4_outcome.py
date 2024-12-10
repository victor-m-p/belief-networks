# now we have voting as well so what can we do with it?
# would be really interesting to look at what makes people not vote
# or what does make people vote 
# i.e., going from no vote --> vote, or from vote --> no vote 

# would be interesting to look into
# p(republican) ~ x 
# p(republican) ~ sd(x)
# p(shift) ~ sd(x)

'''
Things that would be interesting: 
1. what make people vote or not vote (or transition)
--> hypothesis: belief network does not match existing parties. 
2. what makes people vote for other parties
--> hypothesis: belief network does not match existing parties. 
... 
'''

# ahh---there would be some clean-up here to make it work
# would be great to have a column that is 
# democrat, republican, other, did not vote 
import pandas as pd 
df_beliefs = pd.read_csv('data/anes_merged.csv')
df_voting = pd.read_csv('data/anes_complete.csv')
df_voting = df_voting[df_voting['type']=='vote']

# set up first simple model
# x axis (average x 2016)
# y axis (x value lag std)
# color ()
df_vote_who = df_voting[df_voting['question']=='who'][['ID', 'answer', 'year']].drop_duplicates()
df_p1_b = df_beliefs[['ID', 'average_x_2016', 'average_x_2020']].drop_duplicates()
df_p1_v = df_vote_who[df_vote_who['year']==2016]
df_p1_merge = df_p1_b.merge(df_p1_v, on = 'ID', how = 'inner')

import seaborn as sns 
import matplotlib.pyplot as plt 

# 2016 plot 
fig, ax = plt.subplots(figsize=(7, 4))
sns.scatterplot(
    data=df_p1_merge,
    x='average_x_2016',
    y='average_x_2020',
    hue='answer',
    alpha=0.6,  # Set the alpha for transparency
    ax=ax
)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Answer') 
plt.xlabel('avg(x) 2016')
plt.ylabel('avg(x) 2020')
plt.suptitle('voting 2016')
plt.tight_layout()
plt.savefig('figres/voting_2016.png')

# 2020 plot
df_p2_v = df_vote_who[df_vote_who['year']==2020]
df_p2_merge = df_p1_b.merge(df_p2_v, on = 'ID', how = 'inner')
fig, ax = plt.subplots(figsize = (7, 4))
sns.scatterplot(
    data=df_p2_merge,
    x='average_x_2016',
    y='average_x_2020',
    hue='answer',
    alpha=0.6,  # Set the alpha for transparency
    ax=ax
)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Answer') 
plt.xlabel('avg(x) 2016')
plt.ylabel('avg(x) 2020')
plt.suptitle('voting 2020')
plt.tight_layout()
plt.savefig('figres/voting_2020.png')

# look only at the ones that shift
df_wide = df_vote_who.pivot(index='ID', columns='year', values='answer').reset_index()
df_wide.columns = ['ID', 'vote_2016', 'vote_2020']
df_wide['transition'] = df_wide['vote_2016'] != df_wide['vote_2020']
df_wide_t = df_wide[df_wide['transition']==True]
df_wide_t = df_wide_t.dropna()
df_wide_t['transition_type'] = df_wide_t['vote_2016'] + ' --> ' + df_wide_t['vote_2020']
df_p3_merge = df_wide_t.merge(df_p1_b, on = 'ID', how = 'inner')

# what might be interesting is is whether people vote at all 
# okay basic prediction has to be: 
# if you are consistently republican or democrat
# then you will vote for them
# otherwise either "other" or "not vote".
fig, ax = plt.subplots(figsize = (7, 4))
sns.scatterplot(
    data=df_p3_merge,
    x='average_x_2016',
    y='average_x_2020',
    hue='transition_type',
    alpha=1,  # Set the alpha for transparency
    ax=ax
)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title='Answer') 
plt.xlabel('avg(x) 2016')
plt.ylabel('avg(x) 2020')
plt.suptitle('voting transitions')
plt.tight_layout()
plt.show()

# just sanity check some of these
# 1) who is this republican with democrat beliefs?
rep_2020 = df_p2_merge[(df_p2_merge['average_x_2016']>0.6) &
                (df_p2_merge['average_x_2020']>0.6) &
                (df_p2_merge['answer']=='Republican')]
rep_2016 = df_p1_merge[(df_p1_merge['average_x_2016']>0.6) &
                       (df_p1_merge['average_x_2020']>0.6) & 
                       (df_p1_merge['answer']=='Republican')]
df_voting[df_voting['ID']==1813] # weak preference
df_voting[df_voting['ID']==2515] # weak preference
df_voting[df_voting['ID']==2669] # weak preference

'''
Yep, IDs: 1813, 2515, 2669 are just weird. 
'''

# 2) who are these republicans voting other? 
rep_2020_o = df_p2_merge[(df_p2_merge['average_x_2016']<-0.4) &
                (df_p2_merge['average_x_2020']<-0.4) &
                (df_p2_merge['answer']=='Other')]
rep_2016_o = df_p1_merge[(df_p1_merge['average_x_2016']<-0.4) &
                       (df_p1_merge['average_x_2020']<-0.4) & 
                       (df_p1_merge['answer']=='Other')]
df_voting[df_voting['ID']==1043] # weak preference
df_voting[df_voting['ID']==1048] # weak preference
df_voting[df_voting['ID']==1985] # weak preference

'''
Interesting, these really should be consistent republicans.
All have weak preference. 
'''
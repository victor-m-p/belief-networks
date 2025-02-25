import numpy as np 
import pandas as pd 
import json

# gather data in appropriate format # 
participant_id = 16
with open(f'data/human_clean/metadict_{participant_id}.json') as f:
    metadict = json.loads(f.read())

metadict['vemi']

def collect_human_data(participant_id, questionnaire):
    # load data
    with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())

    # extract data
    vemi_data = []
    for key, val in metadict[questionnaire].items():
        vemi_data.append((
            participant_id,
            questionnaire,
            'Human',
            key,
            val['text'],
            val['category'],
            val['likert']
        )
        )

    return pd.DataFrame(
        vemi_data, 
        columns=[
            'participant_id', 
            'questionnaire', 
            'source', 
            'question_key', 
            'text', 
            'category', 
            'likert_human'
            ]
        )

### gather HUMAN data ###
participant_ids = [16, 17, 18, 19, 22, 26, 27]
df_list = []
for p_id in participant_ids: 
    memi = collect_human_data(p_id, 'memi')
    vemi = collect_human_data(p_id, 'vemi')
    df_list.append(memi)
    df_list.append(vemi)

human_answers = pd.concat(df_list)

### gather HUMAN+LLM data ### 
with open('data/gpt_questionnaires/memi_questionnaire.json') as f:
    memi_llm = json.loads(f.read())

with open('data/gpt_questionnaires/vemi_questionnaire.json') as f:
    vemi_llm = json.loads(f.read())

def collect_llm_data(questionnaire, questionnaire_name):
    
    llm_data = []
    for p_id, val in questionnaire.items():
        n = len(val['question_key'])
        key = val['question_key']
        text = val['question_text']
        likert = val['question_rating']
        p_rep = [p_id] * n
        llm_data.append(
            (
            p_rep,
            key,
            text,
            likert
            )
        )
    llm_df = pd.DataFrame(
        llm_data, 
        columns=[
            'participant_id', 
            'question_key', 
            'text', 
            'likert_llm'
            ]
        )
    llm_df = llm_df.explode(['participant_id', 'question_key', 'text', 'likert_llm']).reset_index(drop=True)
    llm_df['questionnaire'] = questionnaire_name
    llm_df['source'] = 'LLM'
    return llm_df                 

# gather LLM data
memi_llm = collect_llm_data(memi_llm, 'memi')
vemi_llm = collect_llm_data(vemi_llm, 'vemi')
llm_answers = pd.concat([memi_llm, vemi_llm])

# merge
llm_answers = llm_answers.drop(columns=['text', 'source'])
human_answers = human_answers.drop(columns=['text', 'source'])

# complaining about types
llm_answers['participant_id'] = llm_answers['participant_id'].astype(int)
human_answers['participant_id'] = human_answers['participant_id'].astype(int)

complete_answers = llm_answers.merge(human_answers, on=['participant_id', 'questionnaire', 'question_key'], how='inner')

# split into vemi and memi
vemi_complete = complete_answers[complete_answers['questionnaire'] == 'vemi']
memi_complete = complete_answers[complete_answers['questionnaire'] == 'memi']

### now quantify performance ### 
## MSE OVERALL ## 
vemi_complete
from sklearn.metrics import mean_squared_error, mean_absolute_error

vemi_overall_mse = mean_squared_error(vemi_complete['likert_human'], vemi_complete['likert_llm'])
vemi_overall_mse # 1.476: so on average slightly more than 1 off (not great not terrible)

memi_overall_mse = mean_squared_error(memi_complete['likert_human'], memi_complete['likert_llm'])
memi_overall_mse # 3.38: this is pretty bad actually. 

# one thing that happens is that it is higher on average
memi_complete['likert_llm'].mean() # 4.07
memi_complete['likert_human'].mean() # 3.3 

# this is much closer for vemi
vemi_complete['likert_llm'].mean() # 6.0
vemi_complete['likert_human'].mean() # 5.8 

## MSE BY ID ## 
vemi_by_id = (
    vemi_complete.groupby('participant_id')[['likert_human', 'likert_llm']]
      .apply(lambda g: mean_squared_error(g['likert_human'], g['likert_llm']))
) # so much better for some (check whether these also have more text)
vemi_id_df = pd.DataFrame(vemi_by_id).reset_index()
vemi_id_df = vemi_id_df.rename(columns={0: 'mse'})

## MSE BY ID AND TYPE ##
vemi_by_id_and_type = (
    vemi_complete.groupby(['participant_id', 'category'])[['likert_human', 'likert_llm']]
    .apply(lambda g: mean_squared_error(g['likert_human'], g['likert_llm']))
)
vemi_id_df_type = pd.DataFrame(vemi_by_id_and_type).reset_index()
vemi_id_df_type = vemi_id_df_type.rename(columns={0: 'mse'})

## get length of text from each participant ## 
participant_ids = [16, 17, 18, 19, 22, 26, 27]

def get_words_char(participant_id):
    with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())
    total_words = sum(len(value.split()) for value in metadict['free_text'].values())
    total_characters = sum(len(value) for value in metadict['free_text'].values())
    return total_words, total_characters

len_text = {}
for p_id in participant_ids:
    words, char = get_words_char(p_id)
    len_text[p_id] = (words, char)
    
len_text_df = pd.DataFrame(len_text).T.reset_index()
len_text_df = len_text_df.rename(columns={'index': 'participant_id', 0: 'words', 1: 'characters'})

### quantify num words ### 
len_text_df['words'].mean() # 360.29 words 
len_text_df['words'].std() # 130.35 words [229.94; 490.64]

### make plots ### 
vemi_id_df_text = vemi_id_df.merge(len_text_df, on='participant_id')
import seaborn as sns 
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
sns.scatterplot(data=vemi_id_df_text, x='words', y='mse', ax=ax)
ax.set_xlabel('Number of words')
ax.set_ylabel('MSE')
plt.show();

### plot by category ###
vemi_id_cat_text = vemi_id_df_type.merge(len_text_df, on='participant_id')

fig, ax = plt.subplots(figsize=(5, 4))
sns.regplot(
    data=vemi_id_cat_text,
    x='words',
    y='mse',
    ax=ax  
)
sns.scatterplot(
    data=vemi_id_cat_text, 
    x='words', 
    y='mse', 
    hue='category',  
    ax=ax
)
ax.set_xlabel('Number of words')
ax.set_ylabel('MSE')
plt.tight_layout()
plt.savefig('fig/vemi_mse_words.png')
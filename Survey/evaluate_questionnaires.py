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
            'likert'
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
        text = val['text']
        likert = val['likert']
        p_rep = [p_id] * n
        llm_data.append(
            p_rep,
            questionnaire_name,
            'LLM',
            key,
            text,
        )
                

# how do we quantify this? # 
## difference by question
## difference by category
## is this just MSE or something like that? 
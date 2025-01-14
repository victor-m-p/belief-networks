'''
VMP 2025-09-01
'''

from openai import OpenAI
import os 
from dotenv import load_dotenv
import json 
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
from fun import load_and_clean, replacements
import pandas as pd 

# setup
outpath='data_output_seq'
inpath='data_input'
model='gpt-4o-mini' # gpt-4o being the flagship
num_generations=10 
num_runs=10  
temperature=0.8
frequency=0.0
presence=0.0

load_dotenv(".env")
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

@retry(wait=wait_random_exponential(min=1, max=200), stop=stop_after_attempt(10))
def ask_as_persona(persona_background, questions, model, temperature=0.7, max_tokens=5000): 
    messages = [{
        'role': 'system',
        'content': persona_background
    }]
    responses = []
    for question in questions: 
        # add users question to message list
        messages.append({
            'role': 'user',
            'content': question
        })
        # get model response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # extract message
        assistant_content = response.choices[0].message.content
        responses.append(assistant_content)
        # append messages
        messages.append({
            'role': 'assistant',
            'content': assistant_content
        })
    return responses # , messages 

# consider name, age, gender, country (demographics)
def create_persona_messages(item_1_answer, item_2_answer): 
    persona_background = f'''
    A research participant answered the following questions: 
    
    1) 
    Question: Which topics are most likely to decide how you vote in the next national election? 
    (feel free to mention as many or as few topics as you please).
    Answer: {item_1_answer}
    
    2) 
    Question: For each of these topics, could you tell me a little more about why this is important to you? 
    (maximum 5 topics)
    Answer: {item_2_answer}
    '''
    return persona_background

# just do it for one person first 
taker = os.listdir(inpath)
taker = taker[0]
with open(os.path.join(inpath, taker), 'r') as f:
    data = json.load(f)

background_persona = create_persona_messages(data['item_1_answer'], data['item_2_answer'])

# 1. first we just need to actually have it code belief nodes 
m1 = """
I would like you to help me understand the beliefs of this person.
Please list all things with which the person agrees or disagrees, even if not stated directly. 
Please formulate each belief as an assertion that one can be `for` or `against`.
Then provide a short-hand for the belief (very short). Please use the following format: 
[("assertion A", "assertion A (short-hand)"), ("assertion B", "assertion B (short-hand)"), ...]
"""

# excract them 
response = ask_as_persona(background_persona, [m1], model)
clean_responses = load_and_clean(response[0], replacements)
responses_long = [x for x, _ in clean_responses]
responses_short = [y for _, y in clean_responses]

# 2. now we need a rating for each of these belief nodes.
# here we aer getting a really strong ceiling effect.
m2 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
Based on the these responses, please indicate your stance on `{belief}` on a scale from -1 to 1,
where -1 is complete disagreement and 1 is complete agreement. 
Please evaluate how important the belief is to you 
on a scale from 0 to 1, where 0 is not important at all and 1 is extremely important.
Please provide this information in the following format:
("belief", agreement, importance)
"""

new_messages = [m2.format(belief=belief) for belief in responses_short]

# why does this take forever?
# honestly; what the fuck.
belief_ratings = []
for message in new_messages: 
    response = ask_as_persona(background_persona, [message], model)
    belief_ratings.append(response[0])
clean_belief_ratings = [load_and_clean(x, replacements) for x in belief_ratings]
belief_ratings_df = pd.DataFrame(clean_belief_ratings, columns=['belief', 'stance', 'attention'])
belief_ratings_df.to_csv(os.path.join(outpath, f'{taker}_nodes.csv'), index=False)

# 3. now make all combinations of these beliefs
clean_belief_list = [x for x, y, z in clean_belief_ratings]
from itertools import permutations 
pairs = list(permutations(clean_belief_list, 2))

m3 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
Imagine that you changed your stance on `{belief_x}`. Would that affect your stance on `{belief_y}`.
If changing your mind on `{belief_x}` would not at all change your mind on `{belief_y}` then assign 0.
If changing your mind on `{belief_x}` would certainly change your mind on `{belief_y}` then assign 1.
Otherwise, assign a score between 0 and 1. 
Please return only the rating and no additional text. 
"""

# this only gives me 0.2 and 0.5 for some reason? 
# does not seem really consistent as well 
# think it is struggling with this. 
# maybe if you do this many times you get something reasonable.
# wondering whether this improves on Brandt actually. 
pair_ratings = []
for belief_x, belief_y in pairs: 
    message = m3.format(belief_x=belief_x, belief_y=belief_y)
    response = ask_as_persona(background_persona, [message], model)
    pair_ratings.append((belief_x, belief_y, response[0]))

pair_ratings_df = pd.DataFrame(pair_ratings, columns=['belief_x', 'belief_y', 'influence'])
pair_ratings_df['influence'] = pair_ratings_df['influence'].astype(float)
pair_ratings_df.to_csv(os.path.join(outpath, f'{taker}_edges_directed.csv'), index=False)

# also get the undirected one # 
pair_ratings_symmetric = pair_ratings_df.copy()
pair_ratings_symmetric['undirected_pair'] = pair_ratings_symmetric.apply(lambda x: tuple(sorted([x['belief_x'], x['belief_y']])), axis=1)
pair_ratings_symmetric = pair_ratings_symmetric.groupby('undirected_pair', as_index=False)['influence'].mean()
pair_ratings_symmetric[['belief_x', 'belief_y']] = pd.DataFrame(pair_ratings_symmetric['undirected_pair'].tolist(), index=pair_ratings_symmetric.index)
pair_ratings_symmetric = pair_ratings_symmetric.drop(columns='undirected_pair')
pair_ratings_symmetric.to_csv(os.path.join(outpath, f'{taker}_edges_undirected.csv'), index=False)

### now we are moving past what is in the data ### 
# m4 (basically m1)
m4 = """
The person who gave the responses above was coded agree with the following stances: 
{belief_list}

You are GPT, but I would like you to answer as the person who gave the responses above.
Please formulate five additional beliefs that you hold, even if not stated directly. 
Please formulate each belief as an assertion that one can be `for` or `against`.
Then provide a short-hand for the belief (very short). Please use the following format: 
[("assertion A", "assertion A (short-hand)"), ("assertion B", "assertion B (short-hand)"), ...]
"""

# try this out. 
takes = 'onw.json'
belief_ratings_df = pd.read_csv(os.path.join(outpath, f'{taker}_nodes.csv'))

test_lst = []
for num, row in belief_ratings_df.iterrows():
    test_lst.append(row['belief'])

belief_string = ""
for num, ele in enumerate(test_lst): 
    belief_string += str(num+1) + ": " + ele + "\n"

message = m4.format(belief_list=belief_string)

response = ask_as_persona(background_persona, [message], model)
response_clean = load_and_clean(response[0], replacements)
responses_long = [x for x, _ in response_clean]
responses_short = [y for _, y in response_clean]

### and now we can repeat steps ### 
### this is almost the same as m2 ### 
m5 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
Based on the these responses, please indicate your stance on `{belief}` on a scale from -1 to 1,
where -1 is complete disagreement and 1 is complete agreement. You might not have 
mentioned this belief directly but that is okay. 
Please evaluate how important the belief is to you 
on a scale from 0 to 1, where 0 is not important at all and 1 is extremely important.
Please provide this information in the following format:
("belief", agreement, importance)
"""

belief_ratings_2 = []
for belief in responses_short: 
    message = m5.format(belief=belief)
    response = ask_as_persona(background_persona, [message], model)
    belief_ratings_2.append(response[0])

belief_ratings_2
clean_belief_ratings_2 = [load_and_clean(x, replacements) for x in belief_ratings_2]
belief_ratings_df_2 = pd.DataFrame(clean_belief_ratings_2, columns=['belief', 'stance', 'attention'])
belief_ratings_df_2.to_csv(os.path.join(outpath, f'{taker}_nodes_additional.csv'), index=False)


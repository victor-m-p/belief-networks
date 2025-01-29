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
from itertools import permutations, product

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
# taker = os.listdir(inpath)
taker = 'vmp.json'
with open(os.path.join(inpath, taker), 'r') as f:
    data = json.load(f)

background_persona = create_persona_messages(data['item_1_answer'], data['item_2_answer'])

# 1. first we just need to actually have it code belief nodes 
p1 = """
I would like you to help me understand the beliefs of this person.
Please list all things with which the person agrees or disagrees, even if not stated directly. 
Please formulate each belief as an assertion that one can be `for` or `against`.
Then provide a short-hand for the belief (very short). Please use the following format: 
[("assertion A", "assertion A (short-hand)"), ("assertion B", "assertion B (short-hand)"), ...]
"""

# excract them 
response_p1 = ask_as_persona(background_persona, [p1], model)
response_p1_clean = load_and_clean(response_p1[0], replacements)
response_p1_long = [x for x, _ in response_p1_clean]
response_p1_short = [y for _, y in response_p1_clean]

# 2. now we need a rating for each of these belief nodes.
# here we aer getting a really strong ceiling effect.
p2 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
Based on the these responses, please indicate your stance on `{belief}` on a scale from -1 to 1,
where -1 is complete disagreement and 1 is complete agreement. 
Please evaluate how important the belief is to you 
on a scale from 0 to 1, where 0 is not important at all and 1 is extremely important.
Please provide this information in the following format:
("belief", agreement, importance)
"""

p2_formatted = [p2.format(belief=belief) for belief in response_p1_short]

# why does this take forever?
# honestly; what the fuck.
belief_ratings_p2 = []
for message in p2_formatted: 
    response_p2 = ask_as_persona(background_persona, [message], model)
    belief_ratings_p2.append(response_p2[0])

beliefs_p2_clean = [load_and_clean(x, replacements) for x in belief_ratings_p2]
beliefs_p2_df = pd.DataFrame(beliefs_p2_clean, columns=['belief', 'stance', 'attention'])
beliefs_p2_df.to_csv(os.path.join(outpath, f'{taker}_nodes.csv'), index=False)

# 3. now make all combinations of these beliefs
beliefs_p2_node = [x for x, y, z in beliefs_p2_clean]
beliefs_p2_pairs = list(permutations(beliefs_p2_node, 2))

p3 = """
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
couplings_p3 = []
for belief_x, belief_y in beliefs_p2_pairs: 
    message = p3.format(belief_x=belief_x, belief_y=belief_y)
    response_p3 = ask_as_persona(background_persona, [message], model)
    couplings_p3.append((belief_x, belief_y, response_p3[0]))

couplings_p3_df = pd.DataFrame(couplings_p3, columns=['belief_x', 'belief_y', 'influence'])
couplings_p3_df['influence'] = couplings_p3_df['influence'].astype(float)
couplings_p3_df.to_csv(os.path.join(outpath, f'{taker}_edges_directed.csv'), index=False)

# also get the undirected one # 
couplings_p3_sym = couplings_p3_df.copy()
couplings_p3_sym['undirected_pair'] = couplings_p3_sym.apply(lambda x: tuple(sorted([x['belief_x'], x['belief_y']])), axis=1)
couplings_p3_sym = couplings_p3_sym.groupby('undirected_pair', as_index=False)['influence'].mean()
couplings_p3_sym[['belief_x', 'belief_y']] = pd.DataFrame(couplings_p3_sym['undirected_pair'].tolist(), index=couplings_p3_sym.index)
couplings_p3_sym = couplings_p3_sym.drop(columns='undirected_pair')
couplings_p3_sym.to_csv(os.path.join(outpath, f'{taker}_edges_undirected.csv'), index=False)

### now we are moving past what is in the data ### 
# m4 (basically m1)
p4 = """
The person who gave the responses above was coded agree with the following stances: 
{belief_list}

You are GPT, but I would like you to answer as the person who gave the responses above.
Please formulate five additional beliefs that you hold, even if not stated directly. 
Please formulate each belief as an assertion that one can be `for` or `against`.
Then provide a short-hand for the belief (very short). Please use the following format: 
[("assertion A", "assertion A (short-hand)"), ("assertion B", "assertion B (short-hand)"), ...]
"""

belief_string_p4 = ""
for num, ele in enumerate(beliefs_p2_node): 
    belief_string_p4 += str(num+1) + ": " + ele + "\n"

message_4 = p4.format(belief_list=belief_string_p4)
response_4 = ask_as_persona(background_persona, [message_4], model)

response_4_clean = load_and_clean(response_4[0], replacements)
response_4_long = [x for x, _ in response_4_clean]
response_4_short = [y for _, y in response_4_clean]

### and now we can repeat steps ### 
### this is almost the same as m2 ### 
p5 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
Based on the these responses, please indicate your stance on `{belief}` on a scale from -1 to 1,
where -1 is complete disagreement and 1 is complete agreement. You might not have 
mentioned this belief directly but that is okay. 
Please evaluate how important the belief is to you 
on a scale from 0 to 1, where 0 is not important at all and 1 is extremely important.
Please provide this information in the following format:
("belief", agreement, importance)
"""

belief_ratings_p5 = []
for belief in response_4_short: 
    message = p5.format(belief=belief)
    response = ask_as_persona(background_persona, [message], model)
    belief_ratings_p5.append(response[0])

beliefs_clean_p5 = [load_and_clean(x, replacements) for x in belief_ratings_p5]
beliefs_clean_p5_df = pd.DataFrame(beliefs_clean_p5, columns=['belief', 'stance', 'attention'])
beliefs_clean_p5_df.to_csv(os.path.join(outpath, f'{taker}_nodes_additional.csv'), index=False)

beliefs_p5_node = [x for x, y, z in beliefs_clean_p5]

# 3. now make all combinations of these beliefs
within_pairs = list(permutations(beliefs_p5_node, 2))
forward_pairs = list(product(beliefs_p5_node, beliefs_p2_node))
reverse_pairs = list(product(beliefs_p2_node, beliefs_p5_node))
all_couplings_p6 = within_pairs + forward_pairs + reverse_pairs

p6 = """
You are GPT, but I would like you to answer as the person who gave the responses above.
I am going to ask you about some stances that you might or might not have mentioned directly in the text.
Either way is fine.
Imagine that you changed your stance on `{belief_x}`. Would that affect your stance on `{belief_y}`.
If changing your mind on `{belief_x}` would not at all change your mind on `{belief_y}` then assign 0.
If changing your mind on `{belief_x}` would certainly change your mind on `{belief_y}` then assign 1.
Otherwise, assign a score between 0 and 1. 
Please return only the rating and no additional text. 
"""

couplings_p6 = []
for belief_x, belief_y in all_couplings_p6: 
    message = p6.format(belief_x=belief_x, belief_y=belief_y)
    response_p6 = ask_as_persona(background_persona, [message], model)
    couplings_p6.append((belief_x, belief_y, response_p6[0]))

couplings_p6_df = pd.DataFrame(couplings_p6, columns=['belief_x', 'belief_y', 'influence'])
couplings_p6_df['influence'] = couplings_p6_df['influence'].astype(float)
couplings_p6_df.to_csv(os.path.join(outpath, f'{taker}_edges_directed_additional.csv'), index=False)

# also get the undirected one # 
couplings_p6_sym = couplings_p6_df.copy()
couplings_p6_sym['undirected_pair'] = couplings_p6_sym.apply(lambda x: tuple(sorted([x['belief_x'], x['belief_y']])), axis=1)
couplings_p6_sym = couplings_p6_sym.groupby('undirected_pair', as_index=False)['influence'].mean()
couplings_p6_sym[['belief_x', 'belief_y']] = pd.DataFrame(couplings_p6_sym['undirected_pair'].tolist(), index=couplings_p6_sym.index)
couplings_p6_sym = couplings_p6_sym.drop(columns='undirected_pair')
couplings_p6_sym.to_csv(os.path.join(outpath, f'{taker}_edges_undirected_additional.csv'), index=False)

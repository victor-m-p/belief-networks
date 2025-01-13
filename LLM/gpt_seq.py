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
    Question: Which topics are most likely to decide how you vote in the next national election? (feel free to mention as many or as few topics as you please).
    Answer: {item_1_answer}
    
    2) 
    Question: For each of these topics, could you tell me a little more about why this is important to you? (maximum 5 topics)
    Answer: {item_2_answer}
    '''
    return persona_background

# test 
taker = os.listdir(inpath)
taker = taker[0]
with open(os.path.join(inpath, taker), 'r') as f:
    data = json.load(f)

background_persona = create_persona_messages(data['item_1_answer'], data['item_2_answer'])

# first we just need to actually have it code belief nodes 
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

# now we need a rating for each of these belief nodes  
m2 = """
You are GPT, but I would like to have you answer as this person using first-person language.
Based on the answers to the previous questions, please indicate your stance on `{belief}` on a scale from -1 to 1,
where -1 is complete disagreement and 1 is complete agreement. Please evaluate how important the belief is to you 
on a scale from 0 to 1, where 0 is not important at all and 1 is extremely important.
Please provide this information in the following format:
("belief", agreement, importance)
"""

new_messages = [m2.format(belief=belief) for belief in responses_short]

# why does this take forever?
response, messages = ask_as_persona(background_persona, new_messages[0], model)

# okay now actually build belief network # 
questions = [
    # question 1: nodes 
    '''Which beliefs are mentioned in your survey responses? 
    please list each belief separately and formulate it as an 
    assertion that one can be `for` or `against`. Then provide a 
    short-hand for the belief (very short). Next, indicate your stance on a scale from -1 to 1 
    (where -1 is complete disagreement and 1 is complete agreement). 
    Finally, evaluate how important the belief is to you on a scale 
    from 0 to 1 (where 0 is not important at all and 1 is extremely important).
    Please provide this information in the following format: 
    [("assertion A", "assertion A (short-hand)", agreement, importance), 
    ("assertion B", "assertion B (short-hand)", agreement, importance), ...]''',
    
    # question 2: edges (the tricky part)
    '''For all pairs of beliefs (assertions) that you mentioned please do the following.
    Imagine that you changed your mind on one of the beliefs. Would that affect
    the other belief? If yes, assign a score between 0 and 1 where 1 is perfectly related.
    If they are not related assign a score of 0. Please provide this information in the following format:
    [("assertion A (short-hand)", "assertion B (short-hand)", related score), 
    ("assertion A (short-hand)", "assertion C (short-hand)", related score), ...]''',
    
    # question 3: additional nodes (maybe not directly mentioned)
    '''list all things with which the person agrees or disagrees 
    in this text, even if not stated directly. Again, please formulate
    each of these as an assertion that one can be `for` or `against`. 
    Then provide a short-hand for the belief (very short).
    For each belief 
    identified, evaluate how much they agree or disagree on a 
    scale from -1 to 1 (where -1 is complete disagreement and 
    1 is complete agreement). Finally, evaluate how important
    the belief is to you on a scale from 0 to 1 (where 0 is not important at all
    and 1 is extremely important. Please provide this information in the following format:
    [("assertion A", "assertion A (short-hand)" agreement, importance), 
    ("assertion B", "assertion B (short-hand)", agreement, importance), ...]''',
    
    # question 4: additional edges 
    '''For all pairs of beliefs (assertions) that you mentioned please do the following.
    Imagine that you changed your mind on one of the beliefs. Would that affect
    the other belief? If yes, assign a score between 0 and 1 where 1 is perfectly related.
    If they are not related assign a score of 0. Please provide this information in the following format:
    [("assertion A (short)", "assertion B (short)", related score), 
    ("assertion A (short)", "assertion C (short)", related score), ...]''',
    
    # question 5: additional edges (predictions)
    '''besides the beliefs that you mentioned, are there any other beliefs that are important to you? 
    if yes, please list the most important ones (maximum 10). Please list them in the following format: 
    [("assertion A", importance), ("assertion B", importance), ...]'''
    
    # question 5: 
    #"would you support a tax increase to fund public health care?",
    #"would you support a tax on carbon emissions?",
    #"are you more likely to vote for a left-wing party, a centrist party, or a right-wing party?"
]

def save_answers_with_id(id_value, answers_list, outpath):
    """
    id_value: str, e.g. "xxx"
    answers_list: list of strings
    outpath: path to save the JSON file
    """
    # 1. Build a dict with "id" and then answer_1, answer_2, ...
    data = {"id": id_value}
    
    # Enumerate the answers and add them as answer_1, answer_2, etc.
    for i, answer in enumerate(answers_list, start=1):
        data[f"answer_{i}"] = answer
    
    # 2. Construct the output filename. 
    #    For example, if you want the file name to be {id_value}.json
    filename = f"{id_value}.json"
    filepath = os.path.join(outpath, filename)
    
    # 3. Write the dict to JSON (this will overwrite if the file already exists)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# now try to run this for each of us
data_input = os.listdir(inpath)
for taker in data_input:
    print(taker)
    with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)
    # this needs to be more flexible of course
    item_1_answer = data['item_1_answer']
    item_2_answer = data['item_2_answer']
    id = data['id']
    persona = create_persona_messages(item_1_answer, item_2_answer)
    answers = ask_as_persona(persona, questions, model)
    save_answers_with_id(id, answers, outpath)

# okay so we need to do something more advanced for the "ask as persona".
# we cannot really pre-determine all of the questions because we would need 
# to actually know the belief nodes (what are the labels that we are using).
# we could do it in 2 steps I guess. 
# 1) first we get the belief nodes (maybe both the "small" and the "large" one.
# 2) then we extract these and append them to questions for the Mirta formulation.

# we might also actually want to think about what we do with memory, and what we do fresh.
# we could also simply have the first part being simply "give me belief nodes". 

# and then both the attention + stance + importance + edges we can do afterwards
# and potentially separately. 
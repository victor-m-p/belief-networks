'''
VMP 2025-09-01
'''

from fun import ask_as_persona
from openai import OpenAI
import os 
from dotenv import load_dotenv
import json 

# setup
outpath='data_output'
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

# function to create completion
# figure out how this actually works
# I think now it does it sequentially (i.e., feeds responses back in)
# which we might or might not want. 

# consider name, age, gender, country (demographics)
def create_persona_messages(item_1_answer, item_2_answer): 
    persona_background = f'''
    You are GPT, but you will respond as an individual who provided a set of answers to a survey.
    
    1) 
    Question: Which topics are most likely to decide how you vote in the next national election? (feel free to mention as many or as few topics as you please).
    Answer: {item_1_answer}
    
    2) 
    Question: For each of these topics, could you tell me a little more about why this is important to you? (maximum 5 topics)
    Answer: {item_2_answer}
    
    Use first-person language when answering questions about yourself.
    '''
    return persona_background

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

# loop over these 
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

# can do an example
data_input = os.listdir(inpath)
taker = data_input[0]
with open(os.path.join(inpath, taker), 'r') as f:
    data = json.load(f)
item_1_answer = data['item_1_answer']
item_2_answer = data['item_2_answer']
id = data['id']
persona = create_persona_messages(item_1_answer, item_2_answer)
answers = ask_as_persona(persona, questions, model)


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
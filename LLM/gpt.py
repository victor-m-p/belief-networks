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
import time 

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
@retry(wait=wait_random_exponential(min=1, max=200), stop=stop_after_attempt(10))
def ask_as_persona(persona_background, questions, model, temperature=0.7, max_tokens=500): 
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
    return responses

# consider name, age, gender, country (demographics)
def create_persona_messages(item_1_answer, item_2_answer): 
    persona_background = f'''
    You are GPT, but you will respond as an individual who provided a set of answers to a survey.
    
    1) Which topics are most likely to decide how you vote in the next national election? (feel free to mention as many or as few topics as you please).
    {item_1_answer}
    
    2) For each of these topics, could you tell me a little more about why this is important to you? (maximum 5 topics)
    {item_2_answer}
    
    Use first-person language when answering questions about yourself.
    '''
    return persona_background

# okay now actually build belief network # 
questions = [
    "which topics are mentioned in your survey responses? please list each topic separately and formulate it as an assertion that one can be `for` or `against`. Then indicate your stance on a scale from -1 to 1 (where -1 is complete disagreement and 1 is complete agreement) and how important the topic is to you (not important, somewhat important, very important).",
    #"for all pairs of topics that you mentioned, please evaluate which one is more important to you.",
    "for all pairs of topics that you mentioned, please evaluate how related they are to each other on a scale from 0 to 1 where 0 is not related at all and 1 is perfectly related.",
    "based on your previous answers, please provide a list of tuples of all your topic relatedness evaluations. Please provide it in the following format: [('topic', 'topic', related score), ('topic', 'topic', related score), ...]",
    #"list all things with which the person agrees or disagrees in this text, even if not stated directly. For each topic identified, evaluate how much they agree or disagree on a scale from -1 to 1 (where -1 is complete disagreement and 1 is complete agreement).",
    #"besides the topics that you mentioned, are there any other topics that are important to you? if yes, please list the most important ones (maximum 5)",
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

# now try to run this for each of us;
data_input = os.listdir(inpath)
for taker in data_input:
    with open(os.path.join(inpath, taker), 'r') as f:
        data = json.load(f)
    item_1_answer = data['item_1_answer']
    item_2_answer = data['item_2_answer']
    id = data['id']
    persona = create_persona_messages(item_1_answer, item_2_answer)
    answers = ask_as_persona(persona, questions, model)
    save_answers_with_id(id, answers, outpath)
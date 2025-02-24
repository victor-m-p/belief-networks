from openai import OpenAI
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
import json 

# setup
model='gpt-4o-mini' # gpt-4o being the flagship
temperature=0.8

load_dotenv(".env")
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

def json_persona(model, background, question, format):
    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": background},
            {"role": "user", "content": question},
            ],
        response_format=format,
    )
    return completion.choices[0].message.parsed.model_dump()

class QuestionnaireRatings(BaseModel): 
    question_key: list[str]
    question_text: list[str]
    question_rating: list[int] 

def prepare_prompts(participant_id=16):
    # this could be any participant--we are not using answers.
    with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())
    
    memi_data = metadict['memi']
    vemi_data = metadict['vemi']
        
    # memi overall framing
    memi_prompt = """
    We asked the participant to complete a survey on their motivations to eat meat. 

    The participant saw the following prompt:

    "
    Below there is a list of reasons to eat meat and other animal products like eggs and dairy. Please rate how important different reasons are for you, personally. You should give a range of ratings to indicate the reasons that are especially important for you, those that are relatively unimportant, and those that are moderately important.
    If you never eat meat, answer based on the reasons you might have to eat meat.
    "    

    """

    # memi questions
    memi_prompt += "\n".join([f"- {key}: {val['text']}" for key, val in memi_data.items()])

    # memi instructions
    memi_prompt += """

    Participants rated the items on a 7-point likert scale where: 
    1: Least important
    4: Moderately important
    7: Most important

    Based on your understanding of the participant, please predict their ratings for these questions.

    Please provide the answer in the following format:
        - [question_key1, question_key2, ...]
        - [question_text1, question_text2, ...] 
        - [question_rating1, question_rating2, ...]
    """
    
    #### VEMI ####
    vemi_prompt = """
    We asked the participant to complete a survey on their motivations to eat less meat and animal products.

    The participant saw the following prompt:

    "
    Please rate the importance of each of the following reasons for you to eat less meat or animal products. 
    Please rate these items even if you don't intend to change your diet. 
    "    

    """

    # memi questions
    vemi_prompt += "\n".join([f"- {key}: {val['text']}" for key, val in vemi_data.items()])

    # memi instructions
    vemi_prompt += """

    Participants rated the items on a 7-point likert scale where: 
    1: Not important
    4: Moderately important
    7: Very important

    Based on your understanding of the participant, please predict their ratings for these questions.

    Please provide the answer in the following format:
        - [question_key1, question_key2, ...]
        - [question_text1, question_text2, ...] 
        - [question_rating1, question_rating2, ...]
    """
    
    return memi_prompt, vemi_prompt


def predict_questionnaires(participant_id, memi_prompt, vemi_prompt, model): 
    
    # load metadict
    with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())

    # extract questionnaire data
    memi_data = metadict['memi']
    vemi_data = metadict['vemi']
    
    # overall background prompt
    with open(f'data/text/prompt_{participant_id}.txt') as f:
        background = f.read()
        
    # MEMI
    max_retries = 5
    attempts = 0
    while attempts < max_retries:
        memi_llm = json_persona(
            model, 
            background, 
            memi_prompt, 
            QuestionnaireRatings
            )
        
        if list(memi_data.keys()) == memi_llm['question_key']:
            break 
        
        attempts += 1

    # VEMI
    attempts = 0
    while attempts < max_retries:
        vemi_llm = json_persona(
            model, 
            background, 
            vemi_prompt, 
            QuestionnaireRatings
            )

        if list(vemi_data.keys()) == vemi_llm['question_key']:
            break 

        attempts += 1    

    return memi_llm, vemi_llm

participant_ids = [16, 17, 18, 19, 22, 26, 27]
memi_prompt, vemi_prompt = prepare_prompts()

memi_questionnaire = {}
vemi_questionnaire = {}
for p_id in participant_ids:
    memi_llm, vemi_llm = predict_questionnaires(
        p_id, 
        memi_prompt, 
        vemi_prompt, 
        model
        )
    memi_questionnaire[p_id] = memi_llm
    vemi_questionnaire[p_id] = vemi_llm

# save the results
with open('data/gpt_questionnaires/memi_questionnaire.json', 'w') as f:
    json.dump(memi_questionnaire, f)

with open('data/gpt_questionnaires/vemi_questionnaire.json', 'w') as f:
    json.dump(vemi_questionnaire, f)
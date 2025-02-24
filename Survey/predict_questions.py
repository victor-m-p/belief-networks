from openai import OpenAI
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
import json 
import numpy as np

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
    question_key: str
    question_text: str
    question_rating: int 

# find the data on panels # 
participant_ids = [16, 17, 18, 19, 22, 26, 27]
participant_id = 17
with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())


# so for all of these, 
    """
    Please rate the importance of each of the following reasons for you to eat less meat or animal products. 

    Please rate these items even if you don't intend to change your diet. 
    
    Participants rated the items on a 7-point likert scale where: 
    1: Not important
    4: Moderately important
    7: Very important
    
    
    """


metadict['vemi']
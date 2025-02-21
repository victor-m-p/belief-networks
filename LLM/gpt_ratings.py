from openai import OpenAI
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
import json 
import numpy as np

# setup
outpath='data_output'
inpath='text'
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

# load background text + metadict 
def generate_data(participant_id, model):

    with open(f'text/prompt_{participant_id}.txt') as f: 
        background = f.read()

    with open(f'../Survey/data/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())

    ### ratings for focal ### 
    focal_text = """
    We asked the participant the following two questions: 

    1. 'Which best describes your meat eating habits?'
    2. 'How important are your meat eating habits to you?'

    The first question we asked them to answer on a 7-point likert.
    We anchored the scale with 1="Never consume meat", 4="Limited meat consumption", 7="Consume meat daily".

    The second question we asked them to rate on a scale from 0-100.

    Based on your understanding of the participant, please predict their ratings for these questions:

    Please provide it in the following format: 
    - consumption: int
    - importance: int
    """    

    class FocalBeliefs(BaseModel): 
        consumption: int
        importance: int

    focal_node_gpt = json_persona(
        model, 
        background, 
        focal_text, 
        FocalBeliefs
    )

    ### ratings for personal beliefs ### 
    p_node_text = """
    The participant mentioned the following motivations to eat meat and not eat meat.
    """

    for key, val in metadict['free_text'].items(): 
        if len(key)==3 and key.startswith('b_'): 
            p_node_text += '\n' + f'- key: {val}' + '\n'

    p_node_text += """
    We then asked the participant about the reasons and values that underlie these motivations.

    'How important is each motivation to you in general?'

    'How necessary is it to (eat / not eat) meat to fulfill this motivation?'

    They could rate both the importance and the necessity from 0-100 with a slider. 

    Based on your understanding of the participant, please predict their ratings for these questions:

    Please provide it in the following format: 
    - name: ["b_0", "b_1", etc.]
    - importance: [int, int, etc.]
    - coupling: [int, int, etc.]
    """

    # this is really nice.
    class PersonalBeliefs(BaseModel): 
        name: list[str]
        importance: list[int]
        coupling: list[int]

    personal_nodes_gpt = json_persona(
        model,
        background,
        p_node_text,
        PersonalBeliefs
    )

    ### now do couplings between beliefs ### 
    p_edge_text = """
    We asked the participant about the relationships between their motivations.

    For each pair of motivations they rated the following: 
    - given that someone like you is motivated by one of these reasons, how likely is it that they are motivated by the other reason as well?

    Recall that the motivations were: 
    """

    for key, val in metadict['free_text'].items(): 
        if len(key)==3 and key.startswith('b_'): 
            p_edge_text += '\n' + f'- key: {val}' + '\n'

    p_edge_text += """
    The answers were provided on a 7-point likert scale.
    We anchored the scale with 1="Not at all likely", 4="Equally likely", 7="Very likely".

    Based on your understanding of the participant, please predict their ratings for these questions:

    Please provide the answer in the following format: 
    - source: ["b_0", "b_1", etc.]
    - target: ["b_1", "b_2", etc.]
    - coupling: [int, int, etc.]
    """

    class PersonalEdges(BaseModel): 
        source: list[str]
        target: list[str]
        coupling: list[int]

    personal_edges_gpt = json_persona(
        model,
        background,
        p_edge_text,
        PersonalEdges
    ) 

    # okay get the personal guys # 
    s_focal_text = """
    We asked the participant to mention 3 people that they interact with regularly, and whose opinions are important to them.

    They provided the following names (anonymized): A, B, C.

    We then asked the participant to rate the following questions:

    1. 'Which best describes the meat eating habits of this person?'
    2. 'How important is the opinion of this person to you in general?'

    The first question we asked them to rate on a 7-point likert.
    We anchored the scale with 1="Never consume meat", 4="Limited meat consumption", 7="Consume meat daily".

    The second question we asked them to rate on a scale from 0-100.

    Based on your understanding of the participant, please predict their ratings for these questions:

    Please also write a short description of each person.

    Please provide it in the following format: 
    - name: ["A", "B", "C"]
    - description: [string, string, string]
    - consumption: int
    - importance: int
    """

    class SocialFocal(BaseModel): 
        name: list[str]
        description: list[str]
        consumption: list[int]
        importance: list[int]

    social_focal_gpt = json_persona(
        model, 
        background, 
        s_focal_text, 
        SocialFocal
    )

    # maybe write a short description of this person # 
    s_personal_text = """
    We asked the participant to mention 3 people that they interact with regularly, and whose opinions are important to them.

    They provided the following names (anonymized): A, B, C.

    We then asked the participant to rate the following questions:

    1. 'Which best describes the meat eating habits of this person?'
    2. 'How important is the opinion of this person to you in general?'

    The first question we asked them to rate on a 7-point likert.
    We anchored the scale with 1="Never consume meat", 4="Limited meat consumption", 7="Consume meat daily".

    The second question we asked them to rate on a scale from 0-100.

    They also provided a short description of each person. 

    They gave the following answers:
    """

    for key, val in social_focal_gpt.items(): 
        s_personal_text += '\n' + f'- {key}: {val}' + '\n'

    background_soc = background + s_personal_text

    s_personal_q = """
    We asked the participant to rate the following question:

    What would each of these people think about the motivations you provided for/against eating meat?

    Recall that the motivations the participant provided were: 
    """

    for key, val in metadict['free_text'].items(): 
        if len(key)==3 and key.startswith('b_'): 
            s_personal_q += '\n' + f'- key: {val}' + '\n'
            
    s_personal_q += """
    The participant rated this question on a 7-point likert scale.
    The scale was anchored with 1="Good reason to not eat meat", 4="Not a good reason for or against", 7="Good reason to eat meat".

    Based on your understanding of the participant, please predict their ratings for these questions:

    Please provide it in the following format:
    - name: ["A", "A", ..., "B", "B", ..., "C", "C", ...]
    - motivation: ["b_0", "b_0", ..., "b_1", "b_1", ...]
    - rating: [int, int, ..., int, int, ..., int, int, ...]
    """

    class SocialPersonal(BaseModel): 
        name: list[str]
        motivation: list[str]
        rating: list[int]
        
    social_personal_gpt = json_persona(
        model, 
        background_soc, 
        s_personal_q, 
        SocialPersonal
    )

    ### save it ### 
    metadict_gpt = {
        'focal_node_gpt': focal_node_gpt,
        'personal_nodes_gpt': personal_nodes_gpt,
        'personal_edges_gpt': personal_edges_gpt,
        'social_focal_gpt': social_focal_gpt,
        'social_personal_gpt': social_personal_gpt
    }

    with open(f'../Survey/data/gpt_raw/metadict_gpt_{participant_id}.json', 'w') as f:
        f.write(json.dumps(metadict_gpt))

# run all 
participant_ids = [16, 17, 18, 19, 22, 26, 27]
for p_id in participant_ids: 
    generate_data(p_id, model)

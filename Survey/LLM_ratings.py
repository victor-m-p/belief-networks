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

def coupling_text(motivation_keys, motivation_vals):
    p_edge_list = []
    for num, key_from in enumerate(motivation_keys): 
        p_edge_text = """
        We asked the participant about the relationships between their motivations.
    
        Given that someone like you is motivated by:
        """
        p_edge_text += f'- {key_from}: {motivation_vals[num]}' + '\n'
        
        p_edge_text += """
        How likely are they to also be motivated by each of:
        """
    
        for key, val in zip(motivation_keys, motivation_vals):
            p_edge_text += f'- {key}: {val}' + '\n'
            
        p_edge_text += """
        The answers were provided on a 7-point likert scale.
        We anchored the scale with 1="Not at all likely", 4="Equally likely", 7="Very likely".
        
        When the source and the target are the same motivation, the participant was instructed to rate the coupling as 7 (very likely).

        Based on your understanding of the participant, please predict their ratings for these questions.
        Be sure to provide a rating for each pair of motivations.
        
        Please provide the answer in the following format:
        - source_code: ["b_0", "b_0", ...]
        - target_code: ["b_1", "b_2", ...]
        - source: [string, string, ...]
        - target: [string, string, ...]
        - coupling: [int, int, ...]
        """
        p_edge_list.append((key_from, p_edge_text))
    return p_edge_list

def social_text(metadict, social_focal_gpt):
    b_pro = []
    b_con = []
    for key, val in metadict['free_text'].items(): 
        if len(key)==3 and key.startswith('b_'): 
            num = key.split('_')[1]
            num = int(num)
            if num >= 5: 
                b_con.append((key, val))
            else: 
                b_pro.append((key, val))
    
    name = social_focal_gpt['name']
    description = social_focal_gpt['description']
    consumption = social_focal_gpt['consumption']
    importance = social_focal_gpt['importance']
    
    s_backgrounds = []
    s_prompts = []
    for name, desc, cons, imp in zip(name, description, consumption, importance):

        s_personal_background = """
        We asked the participant to mention 3 people that they interact with regularly, and whose opinions are important to them.

        They provided the following names (anonymized): A, B, C.

        We then asked the participant to rate the following questions:

        1. 'Which best describes the meat eating habits of this person?'
        2. 'How important is the opinion of this person to you in general?'

        The first question we asked them to rate on a 7-point likert.
        We anchored the scale with 1="Never consume meat", 4="Limited meat consumption", 7="Consume meat daily".

        The second question we asked them to rate on a scale from 0-100.

        They also provided a short description of each person. 

        They described one person in the following way:
        """
        
        s_personal_background += f"name: {name}" + '\n'
        s_personal_background += f"description: {desc}" + '\n'
        s_personal_background += f"consumption: {cons}" + '\n'
        s_personal_background += f"importance: {imp}" + '\n'

        # now personal prompt
        s_personal_prompt = """
        We asked the participant to rate the following question:
        
        What would this person think about the motivations you provided for/against eating meat?
        
        The participant rated this question on a 7-point likert scale.
        The scale was anchored with 1="Good reason to not eat meat", 4="Not a good reason for or against", 7="Good reason to eat meat".
        
        Remember that the motivations the participant provided in favor of eating meat were:
        """
        
        for key, val in b_pro: 
            s_personal_prompt += '\n' + f'- {key}: {val}' + '\n'
        
        s_personal_prompt += """
        And the motivations the participant provided agaisnt eating meat were: 
        """
        
        for key, val in b_con:
            s_personal_prompt += '\n' + f'- {key}: {val}' + '\n'
        
        s_personal_prompt += """
        A social contact might not think that a reason provided is good (rating=4) but thinking that a motivation provided 
        in favor of eating meat actively constitutes an argument against eating meat (or the other way around) should be rare.
        
        This means that for motivations that the participant provided in favor of eating meat should rarely be rated as below 4 by a social contact.
        The same goes for motivations provided against eating meat which should rarely be rated as above 4 by a social contact.
        
        Provide a predicted social belief for each of the motivations provided by the participant.
        
        Please provide your predictions in the following format:
        - name: "name"
        - person_description: "description"
        - motivation: ["b_0", "b_1", ...]
        - rating: [int, int, ...]
        """
        
        s_backgrounds.append(s_personal_background)
        s_prompts.append(s_personal_prompt)
    
    return s_backgrounds, s_prompts


class FocalBeliefs(BaseModel): 
    consumption: int
    importance: int
    
class PersonalBeliefs(BaseModel): 
    name: list[str]
    importance: list[int]
    coupling: list[int]

class PersonalEdges(BaseModel): 
    source_code: list[str]
    target_code: list[str]
    source: list[str]
    target: list[str]
    coupling: list[int]

class SocialFocal(BaseModel): 
    name: list[str]
    description: list[str]
    consumption: list[int]
    importance: list[int]

class SocialPersonal(BaseModel): 
    name: str
    description: str
    motivation: list[str]
    rating: list[int]

class MetaVar(BaseModel): 
    importance_personal: int
    importance_social: int
    conflict_personal: int
    conflict_social: int

def likert_conversion(x, y, n):
    linspace = np.linspace(x, y, n)
    return {i: val for i, val in enumerate(linspace, 1)}

# load background text + metadict 
def generate_data(participant_id, model):
    
    with open(f'text/prompt_{participant_id}.txt') as f: 
        background = f.read()

    with open(f'../Survey/data/human_clean/metadict_{participant_id}.json') as f:
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

    personal_nodes_gpt = json_persona(
        model,
        background,
        p_node_text,
        PersonalBeliefs
    )

    ### now do couplings between beliefs ### 
    motivation_keys = [key for key, val in metadict['free_text'].items() if len(key)==3 and key.startswith('b_')]
    motivation_vals = [val for key, val in metadict['free_text'].items() if len(key)==3 and key.startswith('b_')]

    p_edge_list = coupling_text(motivation_keys, motivation_vals)

    # expected length and actual length
    expected_num = len([key for key in metadict['personal_nodes'].keys() if len(key)==3 and key.startswith('b_')])
    max_retries = 5
    gpt_couplings = []
    for key, p_edge_text in p_edge_list:

        attempts = 0

        while attempts < max_retries:
            personal_edges_gpt = json_persona(
                model,
                background,
                p_edge_text,
                PersonalEdges
            )
            output_num = len(personal_edges_gpt['source_code'])

            if output_num == expected_num:
                # If we get the expected number, stop trying.
                break

            attempts += 1
        
        gpt_couplings.append(personal_edges_gpt)

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

    social_focal_gpt = json_persona(
        model, 
        background, 
        s_focal_text, 
        SocialFocal
    )

    # maybe write a short description of this person # 
    s_backgrounds, s_prompts = social_text(metadict, social_focal_gpt)
    social_list_gpt = []
    for s_backgrounds, s_prompts in zip(s_backgrounds, s_prompts):
        total_background = background + s_backgrounds
        social_personal_gpt = json_persona(
            model, 
            total_background, 
            s_prompts, 
            SocialPersonal
        )
        social_list_gpt.append(social_personal_gpt)

    ### metavar ###
    metavar_text = """
    We asked the participant a couple of overall questions. 

    1. It is important to me that my meat eating habits are consistent with my personal beliefs (1="Strongly disagree", 7="Strongly agree")
    2. It is important to me that my beliefs and behaviors around meat eating are consistent with those of my social contacts (1="Strongly disagree", 7="Strongly agree")
    3. I experience no conflict at all between my personal beliefs and behaviors around eating meat (1="Strongly disagree", 7="Strongly agree")
    4. I experience no conflict at all between my beliefs and behaviors around meat eating and those of my social contacts (1="Strongly disagree", 7="Strongly agree")

    Based on your understanding of the participant, please predict their ratings for these questions.

    Please provide it in the following format:
    - importance_personal: int
    - importance_social: int
    - conflict_personal: int
    - conflict_social: int
    """
    metavar_gpt = json_persona(
    model, 
    background, 
    metavar_text, 
    MetaVar
    )

    likert_scale = likert_conversion(0, 1, 7)

    metavar = {
        'attention_pers': metavar_gpt['importance_personal'],
        'attention_pers_num': likert_scale[metavar_gpt['importance_personal']],
        'attention_soc': metavar_gpt['importance_social'],
        'attention_soc_num': likert_scale[metavar_gpt['importance_social']],
        'dissonance_pers': metavar_gpt['conflict_personal'],
        'dissonance_pers_num': likert_scale[metavar_gpt['conflict_personal']],
        'dissonance_soc': metavar_gpt['conflict_social'],
        'dissonance_soc_num': likert_scale[metavar_gpt['conflict_social']]
    }

    ### gather social ### 
    name_list = []
    motivation_list = []
    rating_list = []
    for i in social_list_gpt:
        name = i['name']
        motivation = i['motivation']
        rating = i['rating']
        n_ele = len(motivation)
        name_list.extend([name]*n_ele)
        motivation_list.extend(motivation)
        rating_list.extend(rating)
    social_personal_gpt = {
        'name': name_list,
        'motivation': motivation_list,
        'rating': rating_list
    }

    ### gather coupling ### 
    source_list = []
    target_list = []
    coupling_list = []
    for i in gpt_couplings: 
        source = i['source_code']
        target = i['target_code']
        coupling = i['coupling']
        source_list.extend(source)
        target_list.extend(target)
        coupling_list.extend(coupling)

    personal_edges_gpt = {
        'source': source_list,
        'target': target_list,
        'coupling': coupling_list
    }

    ### save it ### 
    metadict_gpt = {
        'focal_node_gpt': focal_node_gpt,
        'personal_nodes_gpt': personal_nodes_gpt,
        'personal_edges_gpt': personal_edges_gpt,
        'social_focal_gpt': social_focal_gpt,
        'social_personal_gpt': social_personal_gpt,
        'metavar_gpt': metavar
    }

    with open(f'../Survey/data/gpt_raw/metadict_{participant_id}.json', 'w') as f:
        f.write(json.dumps(metadict_gpt))

# run all 
participant_ids = [16, 17, 18, 19, 22, 26, 27]
for p_id in participant_ids: 
    generate_data(p_id, model)

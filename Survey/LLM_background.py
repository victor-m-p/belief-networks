import json

def create_background(participant_id): 
    with open(f'../Survey/data/metadict_{participant_id}.json') as f:
            metadict = json.loads(f.read())

    prompt_background = """
    You are GPT, but you will take on the personality of an psychology expert. 
    You will help me construct the belief networks of an individual based on free-text responses.
    Pay attention to what is important to them & how their beliefs are related to each other.
    """

    b_focal = """
    First we asked the participant: 
    'What are some things that come to mind when thinking about your meat consumption?'

    They gave the following response: 
    """

    b_pro = """
    We then asked the partipant: 
    'Write up to 5 motivations to eat meat that are important to you personally.'

    And we told them that: 
    'Even if you never eat meat, please provide at least 1 thing that might/would motivate you to eat meat.'

    They gave the following responses:
    """

    b_con = """
    We then asked the participant: 
    'Write up to 5 motivations to not eat meat that are important to you personally.'

    And we told them that they should provide at least 1 thing that might/would motivate them to eat meat.

    They gave the following responses: 
    """

    b_cmv = """
    We then asked them to reflect on their beliefs and behaviors: 
    'Please elaborate on why you have (or have not) changed your meat eating habits'

    They gave the following responses:
    """

    b_soc = """
    Finally, we asked them about their social environment: 

    'Think about the people you interact with on a regular basis and whose opinions are important to you.
    What are their behaviors and beliefs around meat eating?'

    They gave the following responses:
    """

    for key, val in metadict['free_text'].items(): 
        if key == 'b_focal': 
            b_focal = b_focal + '\n' + '- ' + val + '\n'
        if key in ['b_0', 'b_1', 'b_2', 'b_3', 'b_4']: 
            b_pro = b_pro + '\n' + f'- {key}: ' + val + '\n'
        if key in ['b_5', 'b_6', 'b_7', 'b_8', 'b_9']: 
            b_con = b_con + '\n' + f'- {key}: ' + val + '\n'
        if key == 'cmv_focal': 
            b_cmv = b_cmv + '\n' + '- ' + val + '\n'
        if key == 'cmv_other': 
            b_cmv = b_cmv + '\n' + '- ' + val + '\n'
        if key == 'social': 
            b_soc = b_soc + '\n' + '- ' + val + '\n'

    # collect all of the background # 
    prompt_background = prompt_background + b_focal + b_pro + b_con + b_cmv + b_soc

    with open (f'data/text/prompt_{participant_id}.txt', 'w') as f:
        f.write(prompt_background)

participant_ids = [16, 17, 18, 19, 22, 26, 27]
for p_id in participant_ids: 
    create_background(p_id) 
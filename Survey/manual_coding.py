import json
import textwrap
import os 

participant_ids = [16, 17, 18, 19, 22, 26, 27]
outpath = 'data/annotation'

def format_strings(metadict): 
        text_string = ''
        for key, val in metadict['free_text'].items(): 
                val_format = textwrap.fill(val, width=80)
                text_string += key + ":" + "\n"
                text_string += val_format + "\n\n"
        return text_string 
        
for participant_id in participant_ids: 

        with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())
                
        wrapped_text = format_strings(metadict)

        # Write the formatted string to a file
        outname = os.path.join(outpath, str(participant_id))
        with open(f'{outname}.txt', 'w', encoding='utf-8') as f:
                f.write(wrapped_text)

# codings: 

# problem 1: 
# --> one tricky thing is if the same thing is mentioned more than once ... 
# --> open-target is really crazy. 

# can we like collapse it then? 
vars = {
        "animal rights and ethics",
        "climate change",
        "factory farming",
        "environment",
        "nutrition and health", 
}

# maybe just more simple--or sentence-by-sentence? 

node_list = [
        # from b_focal
        ('animal rights are important', 'animal rights', 1, 'explicit'), 
        ('factory farming is ethical', 'factory farming', -1, 'explicit'),
        ('meat consumption is ethical', 'meat consumption', -1, 'implicit'),
        ('concerned about climate change', 'climate change', 1, 'explicit'),
        ('concerned about environment', 'environment', 1, 'explicit'),
        ('great vegetarian meat alternatives', 'vegetarian food', 1, 'explicit')
]

# and now if I do not have them as nodes 

# targets
## question is--could we discover these from the text? ##  
targets = [
        'animal rights and ethics',
        'climate change',
        'meat consumption', # also production ...
        'environment',
        'nutrition and health',
        'pleasure',
        'normality',
        # ...
]

# n=16
nodes = [
        ('animal rights and ethics', 1),
        ('climate change', 1),
        ('environment', 1),
        ('meat consumption', -1),
        ('nutrition and health', 1),
        ('pleasure', 1)
]

couplings = [
        ('animal rights and ethics', 'meat consumption', -1),
        ('climate change', 'meat consumption', -1),
        ('environment', 'meat consumption', -1),
        ('nutrition and health', 'meat consumption', 0), 
        ('pleasure', 'meat consumption', 0)
]

### LLM pipeline ### 
from openai import OpenAI
from pydantic import BaseModel
import os 
from dotenv import load_dotenv
import json 
from groq import Groq
from ollama import chat
load_dotenv(".env")
import instructor
#api_key = os.getenv("GROQ_API_KEY")
#client = Groq(api_key=api_key)

# now look 
participant_id = 16

with open(f'data/human_clean/metadict_{participant_id}.json') as f:
        metadict = json.loads(f.read())
                
# extract 

# now try to extract beliefs # 
def write_prompt_open_target(metadict):
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        cmv_other = metadict['free_text']['cmv_other']
        cmv_other = textwrap.fill(cmv_other, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        prompt = f"""

        ### Overview ###

        Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
        Your task is to analyze an interview about meat eating and to generate all beliefs that are relevant to the interviewee in this context.

        ### Interview Transcript ###
        - Question: "What are some things that come to mind when thinking about your meat consumption?"
        
        - Answer: {b_focal}
        
        - Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
        
        - Answer: {cmv_focal}
        
        - Question: "Think about the people you interact with on a regular basis and whose opinions are important to you.
        What are their behaviors and beliefs around meat eating?'
        
        - Answer: {b_social}

        ### Task Description ###

        1. Identify all the expressed targets that the interviewee holds. 
                - The targets can be a single word or concept (e.g., "climate change") or a phrase, but its maximum length MUST be 4 words.

        2. For each target, determine the stance that is expressed:
                2.1. Classify the stance towards the target 
                - If the stance is in favor of the target, write FAVOR.
                - If the stance is against the target, write AGAINST.
                - If the stance is ambiguous, write NONE - that means the user is clearly speaking about the topic but the stance is not clear.
        
                2.2. Classify the stance towards meat eating 
                - If the stance is in favor meat eating, write FAVOR.
                - If the stance is against meat eating, write AGAINST.
                - If the stance is ambiguous, write NONE.
                
                2.3. Provide the stance type:
                - EXPLICIT: when the stance is directly stated in the interview.
                - IMPLICIT: when the stance is implied but not explicitly stated.

        3. Provide explanations
                - For each stance provide a brief explanation for the provided stance.
                - Formulate explanations like [stance BECAUSE reason]

        For each target and stance classify whether this is an opinion or stance that the interviewee holds personally,
        or whether it is an opinion or stance that social contacts of the interviwee hold. 
                - If personal opinion or stance, write PERSONAL
                - If social contact opinion or stance, write SOCIAL
        
        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "target": "<target description - maximum 4 words>", 
                "stance": "<one among [FAVOR, AGAINST, NONE]>", 
                "stance_meat": "<one amoung [FAVOR, AGAINST, NONE]>",
                "stance_type": "<one among [EXPLICIT, IMPLICIT]>",
                "explanation": "<explanation of how the key claims support the stance classification>"
                "belief_type": "<one among [PERSONAL, SOCIAL]>" 
                }},
                // Repeat for each target expressed by the user's comment
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

from typing import List

class CommentStanceOT(BaseModel): 
    target: str
    stance: str 
    stance_meat: str
    stance_type: str
    explanation: str
    belief_type: str

class FullStancesOT(BaseModel): 
    results: List[CommentStanceOT]

prompt = write_prompt_open_target(metadict)

def call_groq(response_model, content_prompt: str, model_name: str = 'deepseek-r1-distill-llama-70b', temp: float = 0.75):

    # Initialize Groq client with API key from environment variable
    client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    # Patch client with instructor for structured output support
    client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)

    # Generate structured output based on provided schema (FullStances)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": content_prompt}],
        response_model=response_model,
        temperature=temp,
    )

    return response

model = 'llama3-70b-8192'
llm_output = call_groq(
        FullStancesOT, 
        prompt,
        model
        )

beliefs = json.loads(llm_output.model_dump_json(indent=2))
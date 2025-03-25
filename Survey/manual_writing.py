import json
import textwrap
import os 
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

# now try to extract beliefs # 
def write_prompt_open_target(answer):
    
        prompt = f"""

        ### Overview ###

        Stance classification is the task of determining the expressed or implied opinion, or stance, of a statement toward a certain, specified target.
        Your task is to analyze an interview about meat eating and to generate all beliefs that are relevant to the interviewee in this context.

        ### Interview Transcript ###
        - Question: "Please talk to me a bit about political topics that concern you"
        
        - Answer: {answer}

        ### Task Description ###

        1. Identify all the expressed targets that the interviewee holds. 
                - The targets can be a single word or a multi-word concept (e.g., climate change), but must NEVER be more than one concept.
                - The maximum length of the target MUST be 4 words.
                - Do never use the word AND. 

        2. For each target, determine the stance that is expressed:
                2.1. Classify the stance towards the target 
                - If the stance is in favor of the target, write FAVOR.
                - If the stance is against the target, write AGAINST.
                - If stance is mixed--both FOR and AGAINST, or TORN--write MIXED.
                - If the stance is ambiguous, write NONE - that means the user is clearly speaking about the topic but the stance is not clear.
        
                2.2. Evaluate the importance of the stance to the interviewee:
                - Label the least important stances "WEAK"
                - Label the most important stances "STRONG"
                - Label the rest of the stances "MEDIUM"
            
                2.3. Provide the stance type:
                - EXPLICIT: when the stance is directly stated in the comment
                - IMPLICIT: when the stance is implied but not explicitly stated

        3. Provide explanations (from the viewpoint of the interviewee)
                - For each stance provide a brief explanation for the provided stance.
                - ALWAYS start explanations like this "I agree with the following: ..." 

        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "target": "<target description - maximum 4 words>", 
                "stance": "<one among [FAVOR, AGAINST, MIXED, NONE]>", 
                "importance": "<one of [WEAK, MEDIUM, STRONG]>",
                "stance_type": "<one among [EXPLICIT, IMPLICIT]>",
                "explanation": "<I agree with the following: ...>"
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
    importance: str
    stance_type: str
    explanation: str

class FullStancesOT(BaseModel): 
    results: List[CommentStanceOT]

answer = """
The first thing that comes to mind is the rise of authoritarianism. 
Basically I am afraid of wars and instability.
I am afraid that Europe is getting left behind economically.
That the United States and China are winning the AI race and attracting more growth and opportunity.
And that Europe and a few other countries now (with Trump) seem very alone,
Both in terms of upholding the values (democracy, liberalism, etc.) that I value,
But also militarily (e.g., NATO) and economically. 
Even in Europe there seems to be a recent trend towards right-wing authoritarianism.
There is this incredible backlash against “woke” culture which I think is extremely dangerous.
I can definitely understand some of the frustration with identity politics, and DEI, 
And I think that the elites have focused too much on race and identity, and focused too little on class.
I can understand that some white working class people feel that they do not have privilege. 
But I think that the target of the anger, often minority groups is misguided.
I really think that the driver of a lot of the anger that we are seeing in the world is more systemic and economic.
In particular, inequality and poverty is extremely dangerous.
It never bodes well when parents cannot promise and provide a better future for their kids, 
And this is true for many normal people—especially in the places where the backlash is strongest. 
That being said I must also say that I am myself mixed on the immigration question.
On the one hand I think that we desperately need immigration, partly because of demographic shifts.
And I think that we should be much more open to economic immigration (at least).
My main concern is that it is difficult to integrate people from cultures that are very dissimilar. 
I do think that it is true that most people in the world do not share our perception of women,
LGBT, etc. in Denmark, and this is a liberal and progressive culture that we should protect.
This is probably also part of the reason that I am so torn on the Israel-Palestine conflict.
"""

prompt = write_prompt_open_target(answer)

# check prompt # 
with open('prompt.txt', 'w') as f: 
    f.write(prompt)

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
beliefs_res = beliefs['results']

# definitely still some issues here ... 
# things to do: 
# - importance
# - couplings 

belief_nodes = [node['target'] for node in beliefs_res]
format_nodes = "\n".join([x for x in belief_nodes])

focus_node = belief_nodes[0]
new_list = belief_nodes[:0] + belief_nodes[0 + 1:]

def belief_couplings_prompt(answer, nodes, idx):
    
        focus_node = belief_nodes[idx]
        other_nodes = nodes[:idx] + nodes[idx + 1:]
        format_nodes = "\n".join([x for x in other_nodes])
    
        prompt = f"""

        ### Overview ###

        The following is an interview transcript: 

        ### Interview Transcript ###
        
        - Question: "Please talk to me a bit about political topics that concern you"
        
        - Answer: {answer}

        ### The following targets were classified ### 
        
        {nodes}
        
        ### Task Description ###
        
        Your task is to focus the following target (focal):
        
        {focus_node}
        
        And to evaluate how this relates to each of these targetes:
        
        {format_nodes}
        
        1. Evaluate whether {focus_node} relates to each target: 
                - If they are related for the person, write "RELATED"
                - If not related for the person, write "UNRELATED"
        
        2. Explain how the targets are related:
                - Provide a brief explanation for why the targets are related or not related. 
        
        3. Determine the type of the relation: 
                - If the relation is directly stated the text, write "EXPLICIT"
                - If the relation is not directly stated in the text, write "IMPLICIT"

        4. Determine the direction of the relation:
                - If the relation is positive, write "POSITIVE"
                - If the relation is negative, write "NEGATIVE"

        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "target_tuple": "<(focal_target, other_target)>", 
                "relation_presence": "<one amoung [RELATED, UNRELATED]>"
                "explanation": "<brief explanation>"
                "relation_type": "<one among [EXCPLICIT, IMPLICIT]>"
                "relation_direction": "<one among [POSITIVE, NEGATIVE]>"
                }},
                // Repeat for each target expressed by the user's comment
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

prompt = belief_couplings_prompt(answer, belief_nodes, 0)

# quick save to check # 
with open('couplings.txt', 'w') as f: 
    f.write(prompt)

class CouplingOT(BaseModel): 
    target_tuple: str
    relation_presence: str 
    explanation: str
    relation_type: str
    relation_direction: str

class CouplingLST(BaseModel): 
    results: List[CouplingOT]

llm_couplings = call_groq(
        CouplingLST, 
        prompt,
        model
        )

couplings = json.loads(llm_couplings.model_dump_json(indent=2))
couplings 
beliefs_res = beliefs['results']


# intersectional inequalities in social networks # 
# think about it: 
# do we actually have these networks in our head?
# or is there a simpler mechanism?
# e.g., independently summing on dimensions.
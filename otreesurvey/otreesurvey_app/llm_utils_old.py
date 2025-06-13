from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel, field_validator, AfterValidator, ValidationError
from typing import List
import instructor
from instructor import openai_moderation
from tenacity import retry, stop_after_attempt, wait_fixed
from pathlib import Path
import re 
from typing_extensions import Annotated

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
#client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )

@custom_retry
def call_openai(response_model, content_prompt, model_name='gpt-4.1', temp=0.7): # gpt-4.1
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

    kwargs = dict(
        model=model_name,
        messages=[{"role": "user", "content": content_prompt}],
        response_model=response_model,
    )

    if model_name not in ['o3', 'o3-mini', 'o4-mini']:
        kwargs['temperature'] = temp

    try:
        return client.chat.completions.create(**kwargs)
    except Exception as exc:
        print(f"Exception with model {model_name}: {exc}")
        raise

# this does not quite work right now 
# wants the response model 
'''
@custom_retry 
def call_openai_moderation(response_model, content_prompt, model_name='gpt-4.1', temp=0.7):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

    kwargs = dict(
        model=model_name,
        messages=[{"role": "user", "content": content_prompt}],
        #response_model=response_model,
    )

    if model_name not in ['o3', 'o3-mini', 'o4-mini']:
        kwargs['temperature'] = temp

    try:
        # Generate the summary using the language model
        response = client.chat.completions.create(**kwargs)
        summary_text = response.choices[0].message.content

        # Use the Moderation API to evaluate the generated summary
        moderation_response = client.moderations.create(input=summary_text)
        flagged = moderation_response.results[0].flagged

        if flagged:
            # Handle flagged content appropriately
            raise ValueError("Generated content was flagged by moderation.")
        return response, moderation_response #summary_text

    except Exception as exc:
        print(f"Exception with model {model_name}: {exc}")
        raise

@custom_retry
def call_openai_validate(response_model, content_prompt, model_name='gpt-4.1', temp=0.7): # gpt-4.1
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

        kwargs = dict(
                model=model_name,
                messages=[{"role": "user", "content": content_prompt}],
                response_model=response_model,
        )

        if model_name not in ['o3', 'o3-mini', 'o4-mini']:
                kwargs['temperature'] = temp

        try:
                return client.chat.completions.create(**kwargs)
        except ValidationError as e:
                print(f"Validation error: {e}")
        except Exception as exc: 
                print(f"Exception with model {model_name}: {exc}") 
'''
# prompt to extract nodes 
def make_node_prompt(questions_answers: dict) -> str:
        # Format Q&A block
        questions_answers_lines = "\n".join(
                f"- Q: {q}\n- A: {a}" for q, a in questions_answers.items()
        )
        
        prompt = f"""
        
### Task Overview ###

Your task is to analyze an interview transcript and identify the most central beliefs, attitudes and considerations expressed by the interviewee.
By "beliefs" we mean statements with a truth value, such as "production animals are treated badly" or "meat consumption does not contribute to climate change". 
By "attitudes" and "considerations" we mean evaluative statements without a truth value such as "I don't like meat" or "eating meat seems natural to me". 
We will refer to all of the beliefs, attitudes, and considerations collectively as "stances". 

### Interview Transcript ###

{questions_answers_lines}

### Instructions ###

1. Identify stances (beliefs, attitudes, considerations):
- Formulate each stance as a short statement starting exactly with: "I agree with the following: <...>".
- Avoid empty statements such as "some people avoid eating meat because of important reasons".
- Avoid statements that express more than one stance. Thus avoid words like "and" and instead break more complex stances up into simpler individual ones. 
- Keep each statement short and concise and avoid filler words. 
- Be direct in formulations (e.g. "climate change is human caused" is preferred to "I believe that climate change is human caused").
- Avoid filler-words such as "major" (e.g. "concern" better than "major concern") and "key" (e.g., "challenge" better than "key challenge").
- Aim for a maximum length of 4-8 words per stance formulation, and for a maximum of the 7 most important stances.

2. Rate importance for each stance:
- Classify how important each stance (belief, attitude, consideration) is to the interviewee in the context of meat consumption.
- Return your answer as one of [LOW, MEDIUM, HIGH] where LOW are not very important and HIGH are extremely important. 

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "stance": "I agree with the following: <stance>",
        "importance": "<one of [LOW or MEDIUM or HIGH]>",
}},
// Repeat for each stance expressed by the interviewee
]
}}

Return ONLY the JSON object, nothing else.
"""
        return prompt

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

'''
class NodeModelValidate(BaseModel): 
        stance: Annotated[str, AfterValidator(openai_moderation(client=client))]
        importance: Annotated[str, AfterValidator(openai_moderation(client=client))]

class NodeModelValidateList(BaseModel):
        results: List[NodeModelValidate]
'''
class NodeModel(BaseModel): 
        stance: str
        importance: str 

class NodeModelList(BaseModel): 
        results: List[NodeModel]

# Edge Model 
def make_edge_prompt(questions_answers:dict, nodes_list): 
        
        # Format Q&A block
        questions_answers_lines = "\n".join(
                f"- Q: {q}\n- A: {a}" for q, a in questions_answers.items()
        )
        
        # Format the nodes     
        belief_string = "\n".join([f"- {x}" for x in nodes_list])
        
        prompt = f"""
        
### Task Overview ### 

Your task is to analyze an interview transcript about political beliefs, attitudes and concerns.
A number of stances (beliefs, attitudes, concerns) have been extracted from this transcript. 
Your job is to judge which of the extracted stances are related for the interviewee.

### Definitions ###
- "Related" means there is a clear logical, conceptual, argumentative, or social connection.
- A "POSITIVE" relation means that the two targets reinforce, support, or align with each other (they tend to go together).
- A "NEGATIVE" relation means that the two targets conflict, oppose, contradict, or are mutually incompatible (they tend not to go together).
- Do not use POSITIVE/NEGATIVE as a normative judgment (good/bad) but think in terms of reinforcement (POSITIVE) or conflict (NEGATIVE)

### Examples ###
- Two negative outcomes can have a POSITIVE relationship if one reinforces or leads to the other (e.g., meat consumption reinforces climate change concerns).
- Two positive outcomes can have a NEGATIVE relationship if they conflict or oppose each other (e.g., health benefits from meat reduction conflicting with personal enjoyment of meat).

### Interview Transcript ###

{questions_answers_lines}

### Targets ###
The following stances (opinions, attitudes, concerns) were identified as held by the interviewee:

{belief_string}

### Task ###

1. Find stances that POSITIVELY reinforce each other or NEGATIVELY conflict with each other. 
2. Classify whether the direction is POSTIVE or NEGATIVE. 
3. Classify whether the connection is STRONG or WEAK.
4. A connection is symmetric so do not classify the same stance pair twice.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "stance_1": "<full stance>",
        "stance_2": "<full stance>",
        "direction": "<one among [POSITIVE, NEGATIVE]>",
        "strength": "<one among [STRONG, WEAK]>"
}}
// Repeat for each relation between stances that is discovered
]
}}

Return ONLY the JSON object, nothing else.
        """
        return prompt


class EdgeModel(BaseModel): 
        stance_1: str
        stance_2: str 
        direction: str 
        strength: str 
        
        @field_validator("*")
        def no_empty_or_unusual_strings(cls, v, field):
                if isinstance(v, str):
                        cleaned = re.sub(r'\s+', ' ', v).strip()
                        if cleaned == "":
                                raise ValueError(f"{field.name} must not be empty or whitespace.")
                        return cleaned
                return v
                
class EdgeModelList(BaseModel):
        results: List[EdgeModel]
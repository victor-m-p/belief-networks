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


# prompt to extract nodes 
def make_node_prompt(questions_answers: dict) -> str:
        # Format Q&A block
        questions_answers_lines = "\n".join(
                f"- Q: {q}\n- A: {a}" for q, a in questions_answers.items()
        )
        
        prompt = f"""
### Task Overview ###

Analyze the interview transcript provided and clearly extract attitudes (beliefs, concerns, etc.) and behaviors around meat eating.

### Interview Transcript ###
{questions_answers_lines}

### Extraction Instructions ###

1. Summarize the interviewee's behaviors about meat eating (PERSONAL, BEHAVIORS):
- EXAMPLES: "I eat meat every day", "I only eat meat at special occasions".

2. Summarize the interviewee's attitudes about meat eating (PERSONAL, MOTIVATIONS):
- EXAMPLES: "meat is high protein", "I like the taste of meat", "meat production harms the environment", "I am concerned about animal welfare".

3. Summarize the behaviors of the social contacts of the interviewee about meat eating (SOCIAL, BEHAVIORS):
- EXAMPLES: "My family eats meat every day", "Most friends eat meat less than once a week". 

4. Summarize the attitudes of the social contacts of the interviewee about meat eating (SOCIAL, MOTIVATIONS):
- EXAMPLES: "My friends are concerned about animal welfare", "Some friends eat meat for protein".

For each category the following rules apply:
- Each attitude or behavior must be concise and MAXIMUM 8 words.
- Each attitude or behavior must be a complete sentence.
- Each attitide or behavior must be a single thing, not a list of things (avoid "and" or "or").
- EXAMPLES: "I am concerned about animal welfare and climate change" is not allowed, but "I am concerned about animal welfare" and "I am concerned about climate change" are allowed.

5. Rate importance for each node:
- Rate the importance of each node on a scale from 1 to 10 where 1 is "not important at all" and 10 is "extremely important".

6. Create an extremely short (2 word) summary of each attitude or behavior
- For each summary create a 2 word unique short hand (no duplicates allowed).
- EXAMPLES: "I am concerned about animal welfare" --> "Animal welfare", "I rarely eat meat" --> "Rare meat"

For each type-category pair return a MAXIMUM of 10 things.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "stance": "<concise summary of attitude or behavior>",
        "stance_short": "<2 WORD summary>",
        "importance": "<importance rating from 1 to 10>",
        "type": "<one among [PERSONAL, SOCIAL]>",
        "category": "<one among [BEHAVIOR, MOTIVATION]>"
}},
// Repeat for each node found
]
}}

Return ONLY the JSON object, nothing else.
                """
        return prompt

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

class NodeModel(BaseModel): 
    stance: str
    stance_summary: str
    importance: str 
    type: str
    category: str

class NodeModelList(BaseModel): 
    results: List[NodeModel]

def make_social_behavior_prompt(questions_answers: dict) -> str:

        # Format Q&A block
        questions_answers_lines = "\n".join(
                f"- Q: {q}\n- A: {a}" for q, a in questions_answers.items()
        )

        prompt = f"""
### Task Overview ###

Analyze the interview transcript provided and predict the distribution of meat eating behavior among the social contacts of the interviewee.

### Interview Transcript ###
{questions_answers_lines}

### Meat Eating Scale ### 

The interviewee was asked the following question:

Question: 
"Think about your most important social contacts (friends, family, colleagues, etc.).
Out of 100 people how many of them do you think eat meat in the following ways?"

Answer options: 
- 1: never
- 2: less than once a week 
- 3: one or two days a week 
- 4: three or four days a week
- 5: five or six days a week 
- 6: every day: 

For the following questions, by "meat", we mean any meat or meat products, including
chicken, fish, beef, pork, lamb, mutton, goat etc.

It is important that your answers add up to 100 people exactly.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "answer_option": "<[1-6] one of the answer options>",
        "answer_name": "<one of [never, less than once a week, one or two days a week, three or four days a week, five or six days a week, every day]>",
        "number_contacts": "<[1-100] number of contacts who eat meat in this way>"
}},
// Repeat for each node found
]
}}

Return ONLY the JSON object, nothing else.
                """
        return prompt

class SocialBehavior(BaseModel): 
    answer_option: str
    answer_name: str 
    number_contacts: str

class SocialBehaviorList(BaseModel): 
    results: List[SocialBehavior]

def make_social_node_prompt(questions_answers: dict, nodes_list: List[str]) -> str:
        # Format Q&A block
        questions_answers_lines = "\n".join(
                f"- Q: {q}\n- A: {a}" for q, a in questions_answers.items()
        )
        
        # Format the nodes     
        belief_string = "\n".join([f"- {x}" for x in nodes_list])
        
        # For each of the nodes 
        prompt = f"""
### Task Overview ###

An interview transcript about meat eating attitudes and behaviors has been provided.
The interview transcript contains a number of stances (beliefs, attitudes, concerns) that the interviewee holds towards meat eating.
These have been extracted and are provided below. 

The interviewee was asked about their social contacts and their attitudes and behaviors towards meat eating.
Your task is to analyze the interview transcript and judge to which degree the interviewee's social contacts share the attitudes of the interviewee.

### Transcript ###

{questions_answers_lines}

### Targets ###   

{belief_string}

### Instructions ###

For each of the targets, judge the following:

1. Social Agreement: 
- Based on the interview transcript, what percentage of the interviewee's social contacts agree with the target attitude?
- The social agreement score should be a number between 0 and 100, where 0 means no one agrees and 100 means everyone agrees.

2. Social Care:
- Based on the interview transcript, what percentage of the interviewee's social contacts care about the target attitude?
- The social care score should be a number between 0 and 100, where 0 means no one cares and 100 means everyone cares.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "attitude": "<the target attitude from the list>",
        "social_agree": "<[0-100] social agreement score>",
        "social_care": "[0-100] social care score>",
        "explanation": "<a short explanation of the social agreement score and the social care score>"
}},
// Repeat for each item in the list of targets
]
}}

Return ONLY the JSON object, nothing else.

        """
        return prompt

class SocialNodes(BaseModel): 
    attitude: str
    social_agree: str 
    social_care: str
    explanation: str

class SocialNodesList(BaseModel): 
    results: List[SocialNodes]

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
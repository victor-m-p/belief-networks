from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import instructor
from tenacity import retry, stop_after_attempt, wait_fixed
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )

@custom_retry
def call_openai(response_model, content_prompt, model_name='gpt-4.1', temp=0.7):
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
- Aim for a maximum length of 4-8 words per stance formulation, and for a maximum of 15 stances.

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


class NodeModel(BaseModel): 
    stance: str
    importance: str 

class NodeModelList(BaseModel): 
    results: List[NodeModel]

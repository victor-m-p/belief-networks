import openai
import os
from dotenv import load_dotenv
import json 

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_beliefs_from_answers(answers: list[str]) -> list[str]:
    prompt = f"""You are a helpful assistant that extracts belief statements from participant responses.
Below are five open-ended answers. Your job is to identify and extract specific beliefs from them.
Return only a JSON list of belief-like statements (no preamble or explanation).

Answers:
{chr(10).join(f"- {a}" for a in answers)}

Return a JSON list like: ["Belief 1", "Belief 2", ...]
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    content = response['choices'][0]['message']['content']

    try:
        beliefs = json.loads(content)
    except json.JSONDecodeError:
        raise ValueError(f"Could not decode LLM response:\n{content}")

    return beliefs
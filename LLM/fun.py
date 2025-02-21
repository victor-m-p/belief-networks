import re 
import ast 
from openai import OpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
import os 
from dotenv import load_dotenv

replacements = {
    "’": "'",
    "‘": "'",
}

def string_to_list(string): 
    clean_string = re.sub(r"\s+", " ", string).strip()
    clean_list = ast.literal_eval(clean_string)
    return clean_list

def load_and_clean(data, replacements): 
    for old, new in replacements.items(): 
        data = data.replace(old, new)
    data = string_to_list(data)
    return data 

# the big function # 
load_dotenv(".env")
client = OpenAI(
    api_key = os.getenv("OPENAI_API_KEY")
)

@retry(wait=wait_random_exponential(min=1, max=200), stop=stop_after_attempt(10))
def ask_as_persona(persona_background, questions, model, temperature=0.7, max_tokens=5000): 
    messages = [{
        'role': 'system',
        'content': persona_background
    }]
    responses = []
    for question in questions: 
        # add users question to message list
        messages.append({
            'role': 'user',
            'content': question
        })
        # get model response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        # extract message
        assistant_content = response.choices[0].message.content
        responses.append(assistant_content)
        # append messages
        messages.append({
            'role': 'assistant',
            'content': assistant_content
        })
    return responses

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
import pandas as pd 

load_dotenv(dotenv_path=Path(__file__).parent / ".env")
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)

test_sentences = [
    "I hate everyone from group X.",
    "Let's all be kind to each other.",
    "I'm going to kill myself.",
    "You are worthless and should disappear.",
    "This is a very graphic sexual story.",
    "Violence is the only solution.",
]

all_rows = []

for prompt in test_sentences:
    response = client.moderations.create(input=prompt)
    result = response.results[0]
    
    category_scores = result.category_scores.model_dump()
    flags = result.categories.model_dump()

    for category, score in category_scores.items():
        all_rows.append({
            "prompt": prompt,
            "category": category,
            "score": score,
            "flag": flags.get(category, False)
        })

df = pd.DataFrame(all_rows)
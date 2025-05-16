import json
import os 
import pandas as pd 
import os 
from dotenv import load_dotenv
import json 
from groq import Groq
import instructor
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
load_dotenv(".env")
from p_0_prompts import (
        make_node_prompt, 
        make_summary_prompt, 
        make_node_edge_prompt,
        NodeModelList, 
        NodeEdgeModelList,
        SummaryModel
)

### LLM pipeline ### 
custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )

@custom_retry
def call_groq(response_model, content_prompt, model_name='deepseek-r1-distill-llama-70b', temp=0.5):
    client = Groq(api_key=os.getenv('GROQ_API_KEY2'))
    client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content_prompt}],
            response_model=response_model,
            temperature=temp,
        )
        return response
    except Exception as exc:
        print(f"Exception: {exc}")
        raise

# call GPT (very similar.)
@custom_retry
def call_openai(response_model, content_prompt, model_name='gpt-4o-mini', temp=0.5):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))  # or rely on env var OPENAI_API_KEY
    client = instructor.from_openai(client, mode=instructor.Mode.TOOLS)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": content_prompt}],
            response_model=response_model,
            temperature=temp,
        )
        return response
    except Exception as exc:
        print(f"Exception: {exc}")
        raise

# just try nodes for one person #
participant_id = 27
with open(f"data/human_clean/metadict_{participant_id}.json") as f: 
    metadict = json.loads(f.read())

groq_model = 'llama-3.3-70b-versatile'
openai_model = 'gpt-4o-mini'

### SUMMARY ###
summary_prompt = make_summary_prompt(metadict)

with open('prompts/summary.txt', 'w') as f: 
        f.write(summary_prompt)

llm_summary = call_groq(
        SummaryModel,
        summary_prompt,
        groq_model
) 
llm_summary = json.loads(llm_summary.model_dump_json(indent=2))

# save this 
with open(f'llm_codings/summary/{participant_id}.json', 'w') as f:
        json.dump(llm_summary, f, indent=4)

### NODES ###
node_prompt = make_node_prompt(metadict)

# quick save to check that it looks right # 
with open('prompts/node_prompt.txt', 'w') as f: 
        f.write(node_prompt)

# okay sure we get some nodes here
llm_nodes = call_openai(
        NodeModelList,
        node_prompt,
)

# tmp 
json_nodes = json.loads(llm_nodes.model_dump_json(indent=2))
json_res = json_nodes['results']
stances = [x['stance'] for x in json_res]
cleaned = [s.replace("I agree with the following: ", "", 1).strip() for s in stances]
cleaned

y = x['results']
y = [x['stance'] for x in ]

llm_nodes = call_groq(
    NodeModelList,
    node_prompt,
    groq_model 
)
llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))

with open(f'llm_codings/nodes/{participant_id}.json', 'w') as f: 
        json.dump(llm_nodes, f, indent=4)

### NODES AND EDGES at the same time ###
### this seems more useful actually ### 
node_edge_prompt = make_node_edge_prompt(metadict)
with open('prompts/node_edge_prompt.txt', 'w') as f: 
        f.write(node_edge_prompt)

llm_nodes_edges = call_groq(
        NodeEdgeModelList,
        node_edge_prompt,
        groq_model
)

llm_nodes_edges = json.loads(llm_nodes_edges.model_dump_json(indent=2))
with open(f'llm_codings/nodes_edges/{participant_id}.json', 'w') as f: 
        json.dump(llm_nodes_edges, f, indent=4)

### okay so then get edges between concepts ###
### this is the really hard part ### 
belief_list = llm_nodes_edges['results']
belief_list = [i['stance'] for i in belief_list]

### EDGES ### 
import textwrap 
def make_edge_prompt(metadict, belief_list): 
        
        # extract the text from interview
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        
        # extract the belief nodes        
        belief_string = "\n".join([f"- {x}" for x in belief_list])
        
        prompt = f"""
        
### Task Overview ### 
You will analyze a transcript of an interview about meat eating.
From this transcript a number of stances (beliefs, attitudes, concerns) related to meat eating were extracted.
Your job is to analyze the interview and find all stances that are related for the interviewee.

### Definitions ###
- "Related" means there is a clear logical, conceptual, argumentative, or social connection.
- A "POSITIVE" relation means that the two targets reinforce, support, or align with each other (they tend to go together).
- A "NEGATIVE" relation means that the two targets conflict, oppose, contradict, or are mutually incompatible (they tend not to go together).
- Do not use POSITIVE/NEGATIVE as a normative judgment (good/bad) but think in terms of reinforcement (POSITIVE) or conflict (NEGATIVE)

### Examples ###
- Two negative outcomes can have a POSITIVE relationship if one reinforces or leads to the other (e.g., meat consumption reinforces climate change concerns).
- Two positive outcomes can have a NEGATIVE relationship if they conflict or oppose each other (e.g., health benefits from meat reduction conflicting with personal enjoyment of meat).

### Interview Excerpt ###
- Question: "What are some things that come to mind when thinking about your meat consumption?"
- Answer: {b_focal}

- Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Answer: {cmv_focal}

- Question: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Answer: {b_social}

### Targets ###
The following stances (opinions, attitudes, concerns) were identified as held by the interviewee:

{belief_string}

### Task ###

1. Find stances that POSITIVELY reinforce each other or NEGATIVELY conflict with each other. 
2. Classify whether the direction is POSTIVE or NEGATIVE 
3. Classify whether the relation is EXPLICIT (directly stated) or IMPLICIT (implied but not stated).
4. Provide a brief explanation of why the two stances are related for the interviewee.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "stance_1": "<full stance>",
        "stance_2": "<full stance>",
        "direction": "<one among [POSITIVE, NEGATIVE]>",
        "relation_type": "<one among [EXPLICIT, IMPLICIT]>",
        "explanation": "the two stances are related because: <explanation>"
}}
// Repeat for each relation between stances that is discovered
]
}}

Return ONLY the JSON object, nothing else.
        """
        return prompt

import re
from typing import List
from pydantic import BaseModel, field_validator
class EdgeModel(BaseModel): 
        stance_1: str
        stance_2: str 
        direction: str 
        relation_type: str 
        explanation: str 
        
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

edge_prompt = make_edge_prompt(metadict, belief_list)

with open('prompts/edge_prompt.txt', 'w') as f: 
        f.write(edge_prompt)

llm_edges = call_groq(
        EdgeModelList,
        edge_prompt,
        groq_model
)

llm_edges = json.loads(llm_edges.model_dump_json(indent=2))

with open(f'llm_codings/edges/{participant_id}.json', 'w') as f: 
        json.dump(llm_edges, f, indent=4)


######### old #########




# obtain 

llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))

# run participants 
def run_participant2(participant_id, model = 'llama-3.3-70b-versatile'):

        # load participant data 
        with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        directory = f'data/{model}-network'
        if not os.path.exists(directory):
                os.makedirs(directory)

        # nodes 
        node_prompt = make_node_prompt(metadict)
        node_file = f"nodes3_{participant_id}.txt"
        with open(os.path.join(directory, node_file), "w") as f:
                f.write(node_prompt) 

        llm_nodes = call_groq(
                NodeModelList, 
                node_prompt,
                model
                )

        llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))
        llm_nodes = llm_nodes['results']

        beliefs_df = pd.DataFrame(llm_nodes)
        node_file = f"nodes3_{participant_id}.csv"
        beliefs_df.to_csv(os.path.join(directory, node_file), index=False)

        # edges 
        idx_list = [num for num, ele in enumerate(llm_nodes)]

        edge_list = []
        
        edge_file = f"couplings4_{participant_id}.txt"
        for idx in idx_list: 
                llm_edges = gather_edges(metadict, llm_nodes, idx, os.path.join(directory, edge_file))
                edge_list.append(llm_edges)

        llm_edges_df = pd.concat(edge_list)
        edge_file = f"couplings4_{participant_id}.csv"
        llm_edges_df.to_csv(os.path.join(directory, edge_file), index=False)

participant_ids = [16, 17, 18, 19, 22, 26, 27] #[16, 17, 18, 19, 22, 26, 27]
for participant_id in participant_ids: 
        run_participant2(participant_id)
        
### edges ###
# edges 
def gather_edges(metadict, llm_nodes, edge_list, idx, filename, model = 'llama-3.3-70b-versatile'): 
        # make the prompt
        edge_prompt = make_edge_prompt(metadict, llm_nodes, idx)

        # save one example 
        print(idx)
        if idx==0:
                with open(filename, 'w') as f: 
                        f.write(edge_prompt)

        llm_edges = call_groq(
                edge_list, 
                edge_prompt,
                model
                )

        llm_edges = json.loads(llm_edges.model_dump_json(indent=2))
        llm_edges = llm_edges['results']
        llm_edges_df = pd.DataFrame(llm_edges)         
        return llm_edges_df 
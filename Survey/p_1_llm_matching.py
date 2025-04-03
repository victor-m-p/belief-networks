import json
import textwrap
import os 
import pandas as pd 
from pydantic import BaseModel, field_validator
import os 
from dotenv import load_dotenv
import json 
from groq import Groq
import instructor
from typing import List
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv(".env")
class NodeModel(BaseModel): 
    concept: str
    importance: str 
    type: str

class NodeModelList(BaseModel): 
    results: List[NodeModel]
    
class EdgeModel(BaseModel): 
    target_1: str
    target_2: str 
    target_1_type: str
    target_2_type: str
    direction: str
    relation_type: str

class EdgeModelList(BaseModel): 
    results: List[EdgeModel]

### first create the text just for overview ### 
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

### LLM pipeline ### 
custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )

@custom_retry
def call_groq(response_model, content_prompt, model_name='deepseek-r1-distill-llama-70b', temp=0.75):
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

# now try to extract beliefs # 
def make_node_prompt(metadict):
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        prompt = f"""

        ### Overview ###
        
        Your task is to analyze an interview about meat eating and extract all concerns, opinions, or beliefs that are relevant to the interviewee in this context.

        ### Interview Transcript ###
        - Question: "What are some things that come to mind when thinking about your meat consumption?"
        
        - Answer: {b_focal}
        
        - Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
        
        - Answer: {cmv_focal}
        
        - Question: "Think about the people you interact with on a regular basis and whose opinions are important to you.
        What are their behaviors and beliefs around meat eating?'
        
        - Answer: {b_social}

        ### Task Description ###

        1. List all belief nodes: 
                - Identify all the concerns that are expressed in the interview that are related to meat consumption or meat production. 
                - A concern can be a single word or concept (e.g., "climate change") or a short phrase, but its maximum length MUST be 5 words.

        2. Rate the importance of each node: 
                - For each node indicate importance as either "LOW", "MEDIUM", or "HIGH". 

        3. Indicate the type of the node: 
                - If the node is a concern that the interviewee holds, write "PERSONAL"
                - If the node is a concern that social contacts have, write "SOCIAL"
        
        You must create a target called "Meat Consumption and Production" (type = PERSONAL).
        Please also rate the importance of this node. 
        
        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "concept": "<target description - maximum 4 words>", 
                "importance": "<one among [LOW, MEDIUM, HIGH]>", 
                "type": "<one amoung [PERSONAL, SOCIAL]>",
                }},
                // Repeat for each target expressed by the interviewee
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

def make_node_prompt2(metadict):
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        prompt = f"""

        ### Overview ###
        
        Your task is to analyze an interview about meat eating and extract all concerns, opinions, or beliefs that are relevant to the interviewee in this context.

        ### Interview Transcript ###
        - Question: "What are some things that come to mind when thinking about your meat consumption?"
        
        - Answer: {b_focal}
        
        - Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
        
        - Answer: {cmv_focal}
        
        - Question: "Think about the people you interact with on a regular basis and whose opinions are important to you.
        What are their behaviors and beliefs around meat eating?'
        
        - Answer: {b_social}

        ### Task Description ###

        1. List all PERSONAL belief nodes: 
                - Identify all concerns that are expressed in the interview that are related to meat consumption or meat production for them personally.
                - A concern can be a single word or concept (e.g., "climate change", "pleasure", etc.) or a short phrase, but its maximum length MUST be 5 words.

        2. Rate the importance of each node: 
                - For each node indicate importance as either "LOW", "MEDIUM", or "HIGH". 

        3. List all SOCIAL belief nodes:
                - Identify all concerns that the interviewee expresses that social contacts have that are related to meat consumption or meat production.
                - If at all possible give each SOCIAL concern a name that matches one of the PERSONAL concerns that you have extracted.
                - e.g., if you have extracted "climate change" as a PERSONAL node and the interviewee mentions "climate crisis" as a concern in their social circle, then call this node "climate change" as well.
        
        You must create a target called "Meat Consumption and Production" (type = PERSONAL).
        Please also rate the importance of this node. 
        
        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "concept": "<target description - maximum 4 words>", 
                "importance": "<one among [LOW, MEDIUM, HIGH]>", 
                "type": "<one amoung [PERSONAL, SOCIAL]>",
                }},
                // Repeat for each target expressed by the interviewee
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt


def make_node_prompt3(metadict):
        b_focal = textwrap.fill(metadict['free_text']['b_focal'], width=80)
        cmv_focal = textwrap.fill(metadict['free_text']['cmv_focal'], width=80)
        b_social = textwrap.fill(metadict['free_text']['social'], width=80)

        prompt = f"""
### Task Overview ###

Analyze the interview transcript provided and clearly extract beliefs, opinions, or concerns ("nodes") relevant to meat eating.

### Interview Transcript ###
- Question: "What are some things that come to mind when thinking about your meat consumption?"
- Answer: {b_focal}

- Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Answer: {cmv_focal}

- Question: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Answer: {b_social}

### Extraction Instructions ###

1. Identify PERSONAL nodes:
- Concerns or beliefs personally expressed by the interviewee about meat consumption/production.
- Nodes must be concise: MAXIMUM 4 words.

2. Identify SOCIAL nodes:
- Concerns or beliefs attributed by the interviewee to their social circle regarding meat consumption/production.
- If possible, use exactly the same wording for SOCIAL nodes as PERSONAL nodes (if they overlap or are similar).

3. Mandatory node:
- Always include "Meat Consumption and Production" (PERSONAL node).

4. Rate importance for each node:
- Use exactly one of these values: LOW, MEDIUM, HIGH.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "concept": "<concise node name>",
        "importance": "LOW or MEDIUM or HIGH",
        "type": "PERSONAL or SOCIAL"
}},
// Repeat for each node found
]
}}

Return ONLY the JSON object, nothing else.
                """
        return prompt

def make_edge_prompt(metadict, belief_nodes):
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        
        prompt = f"""

        ### Overview ###

        The following is an interview transcript: 

        ### Interview Transcript ###
        - Question: "What are some things that come to mind when thinking about your meat consumption?"
        
        - Answer: {b_focal}
        
        - Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
        
        - Answer: {cmv_focal}
        
        - Question: "Think about the people you interact with on a regular basis and whose opinions are important to you.
        What are their behaviors and beliefs around meat eating?'
        
        - Answer: {b_social}

        ### The following targets were classified ### 
        
        {belief_nodes}
        
        ### Task Description ###
        
        1. For each target evaluate whether the interviewee relates this to any other targets.
                - By a relation we mean either a clear logical, conceptual or argumentative connection.
                - For each pair that is connected provide names of both targets.
                - Indicate the type (PERSONAL, SOCIAL) of the corresponding targets.
        
        2. Determine the direction of the relation as either "POSITIVE" or "NEGATIVE"
                - By "NEGATIVE" we mean that the two targets are in opposition or conflict with each other.
                - By "POSITIVE" we mean the opposite. 
        
        3. Determine the type of the relation: 
                - If the relation is directly stated in the text, write "EXPLICIT"
                - If the relation is not directly stated in the text, write "IMPLICIT"

        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "target_1": "<a concern from the list>", 
                "target_2": "<a cocnern from the list, >",
                "target_1_type": "<one of [PERSONAL, SOCIAL]>",
                "target_2_type": "<one of [PERSONAL, SOCIAL]>",
                "direction": "<one among [POSITIVE, NEGATIVE]>",
                "type": "<one among [EXPLICIT, IMPLICIT]>",
                }},
                // Repeat for each relation (target_1 - target_2) expressed in the interview
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

def make_edge_prompt2(metadict, beliefs_res, idx):        
        # extract the text from interview
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        
        # extract the belief nodes        
        concept_tuples = [f"target: {x['concept']} (type: {x['type']})" for x in beliefs_res]
        focal_target = concept_tuples[idx]
        other_targets = concept_tuples[:idx] + concept_tuples[idx + 1:]
        other_targets = "\n".join([f"- {x}" for x in other_targets])

        prompt = f"""

        You will be given the transcript from an interview and a number of "targets" (beliefs, concepts, concerns) that were found to be relevant for the interviewee.
        Your task will be to judge how these "targets" are related to each other (logically, conceptually, argumentatively, socially).

        ### Overview ###

        The following is an interview transcript: 

        ### Interview Transcript ###
        - Question: "What are some things that come to mind when thinking about your meat consumption?"
        
        - Answer: {b_focal}
        
        - Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
        
        - Answer: {cmv_focal}
        
        - Question: "Think about the people you interact with on a regular basis and whose opinions are important to you.
        What are their behaviors and beliefs around meat eating?'
        
        - Answer: {b_social}

        ### Targets (beliefs, concepts, concerns) ### 
        
        A number of targets were labeled from the interview above. 
        A target is a concept, concern, belief, or stance that is relevant to meat eating for the interviewee. 
        There are two types of targets: PERSONAL (concerns that the interviewee has) and SOCIAL (concerns that social contacts have)
        
        The focal "target" that you will focus on is: 
        - {focal_target}
        
        The other "targets" that were extracted from the interview are:
        {other_targets}
        
        ### Task Description ###
        
        1. For the focal target, evaluate whether it is related to any of the other targets.
                - By a relation we mean either a clear logical, conceptual or argumentative connection.
                - For each pair that is connected provide names of both targets.
                - Indicate the type (PERSONAL, SOCIAL) of the corresponding targets.
        
        2. Determine the direction of the relation as either "POSITIVE" or "NEGATIVE"
                - By "NEGATIVE" we mean that the two targets are in opposition or conflict with each other.
                - By "POSITIVE" we mean the opposite. 
        
        3. Determine the type of the relation: 
                - If the relation is directly stated in the text, write "EXPLICIT"
                - If the relation is not directly stated in the text, write "IMPLICIT"

        4. Explain why the focal target is related to the other target: 
                - Provide a brief explanation (maximum 10 words) to explain your classification.
                
        ### Output Format: ###

        You must output only JSON format:
        {{
        "results": [
                {{
                "focal_target": "<the focal target>", 
                "other_target": "<another target from the list>",
                "focal_target_type": "<one of [PERSONAL, SOCIAL]>",
                "other_target_type": "<one of [PERSONAL, SOCIAL]>",
                "direction": "<one among [POSITIVE, NEGATIVE]>",
                "relation_type": "<one among [EXPLICIT, IMPLICIT]>",
                "explanation": "<brief explanation>"
                }},
                // Repeat for each concern that is related to the focal target.
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

def make_edge_prompt3(metadict, beliefs_res, idx): 
        
        # extract the text from interview
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        
        # extract the belief nodes        
        concept_tuples = [f"target: {x['concept']} (type: {x['type']})" for x in beliefs_res]
        focal_target = concept_tuples[idx]
        other_targets = concept_tuples[:idx] + concept_tuples[idx + 1:]
        other_targets = "\n".join([f"- {x}" for x in other_targets])
        
        prompt = f"""
You will analyze an interview transcript related to meat eating.
You will be given:

1. A focal "target" (belief, concept, or concern) relevant to meat eating for the interviewee.
2. Several other targets extracted from the same interview.

Your task is to judge clearly whether the focal target is related to each of the other targets.

### Definitions ###
- "Related" means there is a clear logical, conceptual, argumentative, or social connection.
- A "POSITIVE" relation means that one target supports, helps, or reinforces the other.
- A "NEGATIVE" relation means that one target conflicts with, opposes, reduces, or is problematic for the other.

### Interview Excerpt ###
- Question: "What are some things that come to mind when thinking about your meat consumption?"
- Answer: {b_focal}

- Question: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Answer: {cmv_focal}

- Question: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Answer: {b_social}

### Focal Target ###
- {focal_target}

### Other Targets ###
{other_targets}

### Task ###
For EACH of the other targets, evaluate the following explicitly:

1. Is the focal target related to this other target? (YES/NO)
2. If YES:
- Direction: POSITIVE or NEGATIVE
- POSITIVE = supporting, reinforcing, beneficial
- NEGATIVE = conflicting, opposing, problematic
- Relation type: EXPLICIT (clearly stated) or IMPLICIT (conceptual connection but not directly stated)
- Explanation: Short and precise (max. 10 words)

### Important ###
- If targets clearly oppose each other (e.g., concerns about meat consumption and concerns about climate change), you MUST classify this as NEGATIVE.
- DO NOT classify relations as POSITIVE just because the topics are conceptually related. ONLY classify POSITIVE if one helps or supports the other.

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "focal_target": "<focal target>",
        "other_target": "<other target>",
        "focal_target_type": "PERSONAL or SOCIAL",
        "other_target_type": "PERSONAL or SOCIAL",
        "direction": "POSITIVE or NEGATIVE",
        "relation_type": "EXPLICIT or IMPLICIT",
        "explanation": "brief explanation"
}}
// Repeat for each related target
]
}}

Return ONLY the JSON object, nothing else.
        """
        return prompt 

def make_edge_prompt4(metadict, beliefs_res, idx): 
        
        # extract the text from interview
        b_focal = metadict['free_text']['b_focal']
        b_focal = textwrap.fill(b_focal, width=80)

        cmv_focal = metadict['free_text']['cmv_focal']
        cmv_focal = textwrap.fill(cmv_focal, width=80)

        b_social = metadict['free_text']['social']
        b_social = textwrap.fill(b_social, width=80)
        
        # extract the belief nodes        
        concept_tuples = [f"target: {x['concept']} (type: {x['type']})" for x in beliefs_res]
        focal_target = concept_tuples[idx]
        other_targets = concept_tuples[:idx] + concept_tuples[idx + 1:]
        other_targets = "\n".join([f"- {x}" for x in other_targets])
        
        prompt = f"""
You will analyze an interview transcript related to meat eating.
You will be given:

1. A focal "target" (belief, concept, or concern) relevant to meat eating for the interviewee.
2. Several other targets extracted from the same interview.

Your task is to clearly judge whether the focal target is related to each of the other targets, and determine the nature of that relation.

### Definitions ###
- "Related" means there is a clear logical, conceptual, argumentative, or social connection.
- A "POSITIVE" relation means that the two targets reinforce, support, or align with each other (they tend to go together).
- A "NEGATIVE" relation means that the two targets conflict, oppose, contradict, or are mutually incompatible (they tend not to go together).

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

### Focal Target ###
- {focal_target}

### Other Targets ###
{other_targets}

### Task ###
For EACH of the other targets, explicitly evaluate:

1. Is the focal target related to this other target? (YES/NO)
2. If YES:
   - Direction: POSITIVE or NEGATIVE
     - POSITIVE = reinforce, support, or align
     - NEGATIVE = conflict, oppose, or contradict
   - Relation type: EXPLICIT (clearly stated in interview) or IMPLICIT (conceptual connection but not directly stated)
   - Explanation: Short and precise (max. 10 words)

### Important ###
- Do NOT use POSITIVE/NEGATIVE as a normative judgment (good vs. bad). Instead, think purely in terms of reinforcement (POSITIVE) or conflict (NEGATIVE).

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "focal_target": "<focal target>",
        "other_target": "<other target>",
        "focal_target_type": "PERSONAL or SOCIAL",
        "other_target_type": "PERSONAL or SOCIAL",
        "direction": "POSITIVE or NEGATIVE",
        "relation_type": "EXPLICIT or IMPLICIT",
        "explanation": "brief explanation"
}}
// Repeat for each related target
]
}}

Return ONLY the JSON object, nothing else.
        """
        return prompt

import re 
class EdgeModel2(BaseModel): 
        focal_target: str
        other_target: str 
        focal_target_type: str 
        other_target_type: str 
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
                
class EdgeModel2List(BaseModel):
        results: List[EdgeModel2]

# edges 
def gather_edges(metadict, llm_nodes, idx, filename, model = 'llama-3.3-70b-versatile'): 
        # make the prompt
        edge_prompt = make_edge_prompt4(metadict, llm_nodes, idx)

        # save one example 
        print(idx)
        if idx==0:
                with open(filename, 'w') as f: 
                        f.write(edge_prompt)

        llm_edges = call_groq(
                EdgeModel2List, 
                edge_prompt,
                model
                )

        llm_edges = json.loads(llm_edges.model_dump_json(indent=2))
        llm_edges = llm_edges['results']
        llm_edges_df = pd.DataFrame(llm_edges)         
        return llm_edges_df 

def run_participant2(participant_id, model = 'llama-3.3-70b-versatile'):

        # load participant data 
        with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        directory = f'data/{model}-network'
        if not os.path.exists(directory):
                os.makedirs(directory)

        # nodes 
        node_prompt = make_node_prompt3(metadict)
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
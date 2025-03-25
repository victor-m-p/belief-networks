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
    type: str

class EdgeModelList(BaseModel): 
    results: List[EdgeModel]

class EdgeModel2(BaseModel): 
        focal_target: str
        other_target: str 
        focal_target_type: str 
        other_target_type: str 
        direction: str 
        type: str 
        explanation: str 
        
        @field_validator("*")
        def no_empty_strings(cls, v, field):
                if isinstance(v, str) and v.strip() == "":
                        raise ValueError(f"{field.name} must not be empty.")
                return v
                
class EdgeModel2List(BaseModel):
        results: List[EdgeModel2]

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
model = 'llama3-70b-8192'

custom_retry = retry(
        stop=stop_after_attempt(5),      # Number of retries (change as needed)
        wait=wait_fixed(2),              # Wait 2 seconds between retries
        reraise=True                     # Raise the exception if all retries fail
        )

@custom_retry 
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
                "type": "<one among [EXPLICIT, IMPLICIT]>",
                "explanation": "<brief explanation>"
                }},
                // Repeat for each concern that is related to the focal target.
        ]
        }}

        ONLY return the JSON object itself.
        """
        return prompt

# edges 
def gather_edges(metadict, llm_nodes, idx): 
        # make the prompt
        edge_prompt = make_edge_prompt2(metadict, llm_nodes, idx)

        # save one example 
        print(idx)
        if idx==0:
                with open(f'data/gpt_codings_new/couplings2_{participant_id}.txt', 'w') as f: 
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

def run_participant2(participant_id):

        # load participant data 
        with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        # nodes 
        node_prompt = make_node_prompt2(metadict)
        with open(f"data/gpt_codings_new/nodes_{participant_id}.txt", "w") as f:
                f.write(node_prompt) 

        llm_nodes = call_groq(
                NodeModelList, 
                node_prompt,
                model
                )

        llm_nodes = json.loads(llm_nodes.model_dump_json(indent=2))
        llm_nodes = llm_nodes['results']

        beliefs_df = pd.DataFrame(llm_nodes)
        beliefs_df.to_csv(f'data/gpt_codings_new/nodes2_{participant_id}.csv', index=False)

        # edges 
        idx_list = [num for num, ele in enumerate(llm_nodes)]

        edge_list = []
        for idx in idx_list: 
                llm_edges = gather_edges(metadict, llm_nodes, idx)
                edge_list.append(llm_edges)

        llm_edges_df = pd.concat(edge_list)
        llm_edges_df.to_csv(f'data/gpt_codings_new/couplings2_{participant_id}.csv', index=False)

participant_id = 16

run_participant2(participant_id)

### maybe implement extra check on this to ensure consistent format ###
# - edges must use nodes that exist 
# - everything must be answered (and have correct values when this applies.)
# ...

'''
InstructorRetryException: Error code: 400 - {'error': {'message': "Failed to call a function. Please adjust your prompt. See 'failed_generation' for more details.", 'type': 'invalid_request_error', 'code': 'tool_use_failed', 'failed_generation': '<tool-use>{ "results": [ { "focal_target": "Meat Consumption and Production", "other_target": "Animal rights", "focal_target_type": "PERSONAL", "other_target_type": "PERSONAL", "direction": "POSITIVE", "type": "EXPLICIT", "explanation": "Meat consumption raises animal rights concerns" }, { "focal_target": "Meat Consumption and Production", "other_target": "Ethical reasons", "focal_target_type": "PERSONAL", "other_target_type": "PERSONAL", "direction": "POSITIVE", "type": "EXPLICIT", "explanation": "Meat consumption raises ethical concerns" }, { "focal_target": "Meat Consumption and Production", "other_target": "Climate change", "focal_target_type": "PERSONAL", "other_target_type": "PERSONAL", "direction": "POSITIVE", "type": "EXPLICIT", "explanation": "Meat consumption contributes to climate change" }, { "focal_target": "Meat Consumption and Production", "other_target": "Health reasons", "focal_target_type": "PERSONAL", "other_target_type": "PERSONAL", "direction": "POSITIVE", "type": "IMPLICIT", "explanation": "Meat consumption affects health" }, { "focal_target": "Meat Consumption and Production", "other_target": "Climate change", "focal_target_type": "PERSONAL", "other_target_type": "SOCIAL", "direction": "POSITIVE", "type": "IMPLICIT", "explanation": "Social contacts concerned about climate change" }, { "focal_target": "Meat Consumption and Production", "other_target": "Ethical reasons", "focal_target_type": "PERSONAL", "other_target_type": "SOCIAL", "direction": "POSITIVE", "type": "IMPLICIT", "explanation": "Social contacts concerned about ethical reasons" }, { "focal_target": "Meat Consumption and Production", "other_target": "Environmental reasons", "focal_target_type": "PERSONAL", "other_target_type": "SOCIAL", "direction": "POSITIVE", "type": "IMPLICIT", "explanation": "Social contacts concerned about environmental reasons" } ] }</tool-use>'}}
'''

######## ......................... ##########
def run_participant(participant_id, model='llama3-70b-8192'): 

        with open(f'data/human_clean/metadict_{participant_id}.json') as f:
                metadict = json.loads(f.read())

        ## nodes 
        node_prompt = make_node_prompt(metadict)

        # save
        with open(f"data/gpt_codings_new/nodes_{participant_id}.txt", "w") as f:
                f.write(node_prompt) 

        llm_output = call_groq(
                NodeModelList, 
                node_prompt,
                model
                )

        beliefs = json.loads(llm_output.model_dump_json(indent=2))
        beliefs_res = beliefs['results']
        beliefs_df = pd.DataFrame(beliefs_res)

        # save this # 
        beliefs_df.to_csv(f'data/gpt_codings_new/nodes_{participant_id}.csv', index=False)

        ## edges ##
        belief_nodes_format = "\n\n".join([f"- {x['concept']} ({x['importance']} {x['type']} importance)" for x in beliefs_res])
        edge_prompt = make_edge_prompt(metadict, belief_nodes_format)

        # save 
        with open(f'data/gpt_codings_new/couplings_{participant_id}.txt', 'w') as f: 
                f.write(edge_prompt)

        llm_edges = call_groq(
                EdgeModelList, 
                edge_prompt,
                model
                )

        llm_edges = json.loads(llm_edges.model_dump_json(indent=2))
        llm_edges = llm_edges['results']
        llm_edges_df = pd.DataFrame(llm_edges) # ahhh.. social one of them.
        llm_edges_df.to_csv(f'data/gpt_codings_new/couplings_{participant_id}.csv', index=False)
        print(f"finished running participant ID: {participant_id}")

# run for all participants
participant_ids = [16, 17, 18, 19, 22, 26, 27]
p_id = 16
run_participant(p_id)
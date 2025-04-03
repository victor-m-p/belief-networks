import textwrap
from pydantic import BaseModel, field_validator
from typing import List
import re 

def make_summary_prompt(metadict): 
        b_focal = textwrap.fill(metadict['free_text']['b_focal'], width=80)
        cmv_focal = textwrap.fill(metadict['free_text']['cmv_focal'], width=80)
        b_social = textwrap.fill(metadict['free_text']['social'], width=80)

        prompt = f"""

### Task Overview ###

Your task is to analyze an interview transcript about meat eating.
You will be asked to extract 2 things: 
1. The overall attitude of the interviwee towards meat eating. 
2. The most central belief (reason) for this attitude. 

By "attitudes" and we mean evaluative statements without a truth value such as "meat eating is ethically wrong", or "meat eating gives me pleasure"
By "belief" (reason) we mean a statemtn with a truth value such as "meat production causes climate change", or "production animals are not treated well"

### Interview Transcript ###

- Interviewer: "What are some things that come to mind when thinking about your meat consumption?"
- Interviewee: {b_focal}

- Interviewer: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Interviewee: {cmv_focal}

- Interviewer: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Interviewee: {b_social}

### Instructions ###

1. Identify attitude towards meat eating 
- Based on the full interview transcript, formulate an overall attitude for the interviewee towards meat eating.
- Provide your ouput in exactly this format: "My overall attitude towards meat eating is: <attitude description>"

2. Identify the most important reason for the overall attitude
- Provide your output in exactly this format: "My central reason for holding this attitude is: <attitude reason>"

### Output Format (JSON ONLY) ###
"results": {{
        "attitude": "My overall attitude towards meat eating is: <attitude description>",
        "reason": "My central reason for holding this attitude is: <attitude reason>",
}}

Return ONLY the JSON object, nothing else.
"""
        return prompt


class SummaryModel(BaseModel): 
    attitude: str
    reason: str 

def make_node_prompt(metadict):

        b_focal = textwrap.fill(metadict['free_text']['b_focal'], width=80)
        cmv_focal = textwrap.fill(metadict['free_text']['cmv_focal'], width=80)
        b_social = textwrap.fill(metadict['free_text']['social'], width=80)

        prompt = f"""

### Task Overview ###

Your task is to analyze an interview transcript and identify the central beliefs, attitudes and considerations expressed by the interviewee.
By "beliefs" we mean statements with a truth value, such as "production animals are treated badly" or "meat consumption does not contribute to climate change". 
By "attitudes" and "considerations" we mean evaluative statements without a truth value such as "I don't like meat" or "eating meat seems natural to me". 
We will refer to all of the beliefs, attitudes, and considerations collectively as "stances". 

### Interview Transcript ###

- Interviewer: "What are some things that come to mind when thinking about your meat consumption?"
- Interviewee: {b_focal}

- Interviewer: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Interviewee: {cmv_focal}

- Interviewer: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Interviewee: {b_social}

### Instructions ###

1. Identify stances (beliefs, attitudes, considerations):
- Formulate each stance as a short statemtent starting exactly with: "I agree with the following: <...>".
- Avoid empty statements such as "some people avoid eating meat because of important reasons".

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


def make_node_edge_prompt(metadict):

        b_focal = textwrap.fill(metadict['free_text']['b_focal'], width=80)
        cmv_focal = textwrap.fill(metadict['free_text']['cmv_focal'], width=80)
        b_social = textwrap.fill(metadict['free_text']['social'], width=80)

        prompt = f"""

### Task Overview ###

Your task is to analyze an interview transcript and identify the central beliefs, attitudes and considerations expressed by the interviewee.
By "beliefs" we mean statements with a truth value, such as "production animals are treated badly" or "meat consumption does not contribute to climate change". 
By "attitudes" and "considerations" we mean evaluative statements without a truth value such as "I don't like meat" or "eating meat seems natural to me". 
We will refer to all of the beliefs, attitudes, and considerations collectively as "stances". 

### Interview Transcript ###

- Interviewer: "What are some things that come to mind when thinking about your meat consumption?"
- Interviewee: {b_focal}

- Interviewer: "Please elaborate on why you have (or have not) changed your meat eating habits"
- Interviewee: {cmv_focal}

- Interviewer: "Think about people important to you. What are their behaviors and beliefs around meat eating?"
- Interviewee: {b_social}

### Instructions ###

1. Identify stances (beliefs, attitudes, considerations):
- Formulate each stance as a short statemtent starting exactly with: "I agree with the following: <...>".
- Avoid empty statements such as "some people avoid eating meat because of important reasons".

2. Rate importance for each stance:
- Classify how important each stance (belief, attitude, consideration) is to the interviewee in the context of meat consumption.
- Return your answer as one of [LOW, MEDIUM, HIGH] where LOW are not very important and HIGH are extremely important. 

3. Rate direction of each stance: 
- For each classified stance (belief, attitude, consideration) judge whether it is in FAVOR or AGAINST meat eating for the interviewee.
- Return your answer as one of [FAVOR, AGAINST]

### Output Format (JSON ONLY) ###
{{
"results": [
{{
        "stance": "I agree with the following: <stance>",
        "importance": "<one of [LOW or MEDIUM or HIGH]>",
        "direction": "<one of [FAVOR, AGAINST]>
}},
// Repeat for each stance expressed by the interviewee
]
}}

Return ONLY the JSON object, nothing else.
"""
        return prompt

class NodeEdgeModel(BaseModel): 
    stance: str
    importance: str 
    direction: str

class NodeEdgeModelList(BaseModel): 
    results: List[NodeEdgeModel]


def make_edge_prompt(metadict, beliefs_res, idx): 
        
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
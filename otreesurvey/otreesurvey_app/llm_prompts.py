from llm_utils import *
import time
import json
from pathlib import Path

questions_answers = {
    "Please describe your dietary pattern, specifically your meat eating habits. Think about what you would consume in a typical week": "In a typical week I would probably consume some meat most days. But I do not eat meat everyday, and mostly what I consume would be slices of meat on bread for e.g. lunch. I never cook meat myself, but will eat it when I am out.",
    "Are there any personal motivations that you have to eat or not to eat meat? Feel free to write about anything that comes to mind": "Some of the motivations that I have to eat meat is just that it is convenient and that I like the taste of meat. Especially for some things—e.g., slices of meat on bread this is just a habit where I have not properly implemented or found a good alternative. Also meat can be a good source of protein, but overall I actually think that restricting meat is the more healthy option. My main motivations to not eat meat is that I think it is better for the world not to. One reason is climate change, but actually I am more concerned with animal welfare with most meat produced unethically.",  
    "Think about the people you interact with on a regular basis and whoso opinions are important to you. What are their meat eating habits?": "There are some strict vegetarians in my social circle, and I also know some vegans. Very few people that I know eat a lot of meat, but most will occasionally eat meat. Mostly I think that are similar to me in the sense that they would never cook a big steak or something like that, but would maybe be okay with buying a pizza with pepperoni.",
    "Think about the people you interact with on a regular basis and whose opinions are important to you. What are their motivations to eat or to avoid eating meat?": "I think that motivations are generally similar to me. I guess that some of my social contacts are more motivated by climate change considerations and some are more motivated by animal welfare considerations."
    }

node_prompt = make_node_prompt(questions_answers)
with open('LLM/node_prompt.txt', 'w') as f: 
    f.write(node_prompt)

# try different models 
models = [
    'gpt-4o',         # Fast and very accurate (works)
    'gpt-4.1',        # Flagship model (works)
    'gpt-4o-mini',    # Lightweight baseline (works)
    'gpt-4-turbo',    # High-speed, large context (works)
    #'o3',             # error: Your organization must be verified to use the model `o3`
    'o3-mini',        # needs to be without temperature (done)
    'o4-mini',        # needs to be without temperature (done)
]

# this seems okay but sometimes collapses. 
# but not sure what to do with behavior distribution
# also behavior more difficult in the 
# "I agree with the following: " prefix setup.
mdl = 'gpt-4.1' # seems better than 4o-mini
node_prompt = make_node_prompt(questions_answers)

with open('LLM/node_prompt.txt', 'w') as f:
    f.write(node_prompt)

node_response = call_openai(NodeModelList, node_prompt, model_name=mdl)
node_results = node_response.model_dump()['results']
node_results # should this have predicted direction to focal? we are assumming this for at least the personal beliefs.
node_results
# save results


# this seems reasonable
# need to implement check that it sums to 100
soc_prompt = make_social_behavior_prompt(questions_answers)

with open('LLM/soc_prompt.txt', 'w') as f:
    f.write(soc_prompt)

social_response = call_openai(SocialBehaviorList, soc_prompt, model_name=mdl)
social_results = social_response.model_dump()['results']
social_results  

# now try to predict social pressure on each belief 
# but predict this such that it can be none as well
# this overall seems pretty good actually. 
personal_nodes = [node['attitude'] for node in node_results if node['type'] == "PERSONAL"]
soc_node_prompt = make_social_node_prompt(questions_answers, personal_nodes)

with open('LLM/soc_node_prompt.txt', 'w') as f:
    f.write(soc_node_prompt)

soc_node_response = call_openai(SocialNodesList, soc_node_prompt, model_name=mdl)
soc_node_results = soc_node_response.model_dump()['results']  # this is a list of SocialNodeModel
soc_node_results

# run over models and store results
results = {}
for model in models:
    print(f"Running model: {model}")
    start_time = time.time()

    try:
        response = call_openai(NodeModelList, node_prompt, model_name=model)
        stance_list = response.results  # this is a list of NodeModel
    except Exception as e:
        stance_list = []
        response = {"results": [{"stance": f"ERROR: {str(e)}", "importance": "LOW"}]}

    elapsed = time.time() - start_time

    results[model] = {
        "response": response,
        "time_seconds": elapsed,
        "num_stances": len(stance_list),
    }
    
# Convert all custom response models to dictionaries
serializable_results = {
    model: {
        "response": data["response"].model_dump(),  # Converts NodeModelList to dict
        "time_seconds": data["time_seconds"],
        "num_stances": len(data["response"].results),
    }
    for model, data in results.items()
}

# Save full JSON
json_path = Path("LLM/models_2.json")
with open(json_path, "w") as f:
    json.dump(serializable_results, f, indent=2)
    
# Save human-readable summary
txt_path = Path("LLM/model_summary_2.txt")
with open(txt_path, "w") as f:
    f.write("### PROMPT USED ###\n")
    f.write(node_prompt + "\n\n")

    for model, data in results.items():
        f.write(f"## Model: {model} | Stances Found: {data['num_stances']} | Time: {data['time_seconds']:.2f} sec\n")
        for item in data["response"].results:
            f.write(f"- {item.stance} [{item.importance}]\n")

        f.write("\n")

''' NOTES ON MODELS 
- Reasoning models (o3, o4) are much slower (~15 seconds vs. ~5 seconds).
- Still could be more precise and concise, but generally pretty good. 
'''

### try connections ### 
model = 'gpt-4o-mini'
response = call_openai(NodeModelList, node_prompt, model_name=model)
response_clean = [
    (node.stance.replace("I agree with the following: ", "").strip(), node.importance)
    for node in response.results
]
stance_list = [x for x, y in response_clean]

# make edge prompt
edge_prompt = make_edge_prompt(questions_answers, stance_list)
with open('LLM/edge_prompt.txt', 'w') as f: 
    f.write(edge_prompt)

# okay get edges then 
response = call_openai(EdgeModelList, edge_prompt, model_name=model)

coupling_dict = {
    f"coupling_{i+1}": {
        "stance_1": edge.stance_1,
        "stance_2": edge.stance_2,
        "direction": edge.direction,
        "strength": edge.strength
    }
    for i, edge in enumerate(response.results)
}

## test moderation ##
response, moderation = call_openai_moderation(NodeModelList, node_prompt)
response = call_openai(NodeModelList, node_prompt)

## test moderation with pydantic ## 
'''
This feels clearly slower. 
'''
test = call_openai(NodeModelValidateList, node_prompt)
from llm_utils import *
import time
import json
from pathlib import Path

questions_answers = {
    'How do you place yourself politically? Would you call yourself a conservative or a liberal or something else? What does this mean to you?': 'In an American context I would call myself a liberal or a progressive probably; I mostly hold progressive or left-wing views--e.g., I am concerned about rising economic inequality, about growing anti-democratic and anti-immigration sentiments (generally populism and right-wing extremism). I am globally oriented, and believe that the most important challenges that we have (e.g., climate change is one of them) needs to be solved in supernational fora. Generally I am liberal, and believe that people should be able to live their lives the way that they want, as long as they do not infringe on the freedom of other people: for instance, I believe that most drugs should be legal, and I believe that LGBTQ people should have similar rights as more heteronormative people do.',
    'What are some things that concern you in the political domain? Feel free to mention things that are important to you personally, or more long-term concerns or challenges for your country': 'Currently I am very concerned about the rise of extreme-right parties and populism globally. Of course Donald Trump in the US is the most clear example of this, but I am also concerned about the rapid rise of extreme right-wing parties in many european countries (e.g., Sweden, Germany, Austria). I am also concerned about economics right now, given that the global system is being shaken by both protectionistic and anti-globalist policies from the Trump administration and the war in Ukraine. More long-term I am concerned about climate change, which I see as one of the key challenges of my generation, and I am concerned about the future of Europe and the EU given that our economic growth is terrible, and that much of the key innovation (e.g., in AI, advanced chip manufacturing, etc.) is happening in the US and in China (and not in Europe).',
    'Are there things about your country that make you feel proud or ashamed? Feel free to write about any features or events that come to mind': 'Proud might not be exactly the right word to describe this, but I am generally very happy about the way that the Danish society and system is structured. It is one of the least corrupt, most happy countries in the world. It is more egalitarian than most countries, offering generous unemployment benefits, free (you even get paid) education, and good universal health care coverage. Besides maybe taxes (where we pay more in Denmark) I think that Denmark is really a much more free country than the for instance the US: for instance, I had the freedom (or opportunity) to do a long education even though my parents do not make a lot of money, which would maybe not have been possible in many other countries.',
    'Are there any political questions where you feel dissonance or conflict? Maybe something that is salient for you personally, or is discussed among your social contacts or in the media': 'I just had a very intense discussion recently with a good friend about whether (and when) to state your pronouns. For instance, on social media, twitter, work emails, in zoom calls etc. I do not think that we actually fundamentally agree on identity, gender, and LGBTQ+ questions (we are both leaning clearly progressive) but I feel mixed about putting this everywhere. I do think that the friend had a good point about this being important, and did add this in a few places (e.g., on twitter, work email). I think what bothers me a little bit about this is that I feel that the left is too focused on identity (gender, race, sex) and in general I think that class is a more fundamental and important axis that the progressive/left has emphasized too little.',
    'Are there any more things that are important to you politically that we have not yet discussed? Feel free to write about anything that comes to mind': 'Maybe we have not talked so much about immigration, which is a tricky topic for me. Mostly, my politics align with left-wing parties, e.g., on LGBTQ, feminism, economic inequality, climate change, etc., but on immigration I am really split between different concerns. I am very much in favor of economic immigration and mobility broadly, but I do think that there are limits to the number of refugees and immigrants from culturally very dissimilar places that we can integrate. This places me somewhere weird in the middle between the proper left-wing, and the right wing, and is also one of the clashes that I have with my party (Radikale Venstre). Probably, again in a Danish context, I am more of a social democrat on this point.'
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


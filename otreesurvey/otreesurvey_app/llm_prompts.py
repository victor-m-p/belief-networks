


from llm_utils import *
d = {'What do you think about DEI policy': 'Think it can be justified to correct historical bias, but can create dangerous backlash...'}
prompt = make_node_prompt(d)
res = call_openai(NodeModelList, prompt)
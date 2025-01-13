import re 
import ast 

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
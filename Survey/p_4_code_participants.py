import textwrap 
import os 
import json 

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
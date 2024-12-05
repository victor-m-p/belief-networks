import numpy as np
import pandas as pd 
import os 

# load ANES data
anes_df = pd.read_csv('../ANES/data/anes_data.csv')

# take a smaller part of the data 
questions = ['gay', 'imm']
anes_sub = anes_df[anes_df['question'].isin(questions)]
anes_sub.groupby(['question', 'answer']).size()

# just 2016 for now
df_2016 = anes_sub[anes_sub['year'] == 2016]
df_2016_wide = df_2016.pivot(index='ID', columns='question', values='answer')
df_2016_dummies = pd.get_dummies(df_2016_wide).reset_index(drop=True)

# code False=0, True=1
df_2016_dummies = df_2016_dummies.astype(int)

# save to mpf 
def write_to_mpf(df, output_folder, output_filename, weights=1.0): 
    columns = df.columns.tolist()
    n_obs = df.shape[0]
    n_nodes = len(columns)
    df['weight'] = weights
    formatted_rows = df.apply(
        lambda row: f"{''.join(map(str, row[columns].astype(int).tolist()))} {row['weight']:.2f}",
        axis=1
    )
    # save 
    output = f"{n_obs}\n{n_nodes}\n" + '\n'.join(formatted_rows)
    with open(os.path.join(output_folder, output_filename), 'w') as f: 
        f.write(output)
        
write_to_mpf(
    df_2016_dummies,
    'ANES', 
    'anes_2016.txt')

df_2016_dummies.to_csv('ANES/anes_2016.csv', index=False)
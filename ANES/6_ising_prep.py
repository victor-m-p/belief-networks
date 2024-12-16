import pandas as pd 
import os 

# load data  
anes_data = pd.read_csv('data/anes_complete.csv')
questions = ['gay', 'imm', 'temp', 'abort', 'tax', 'church']

# could do something smarter for binarization maybe
anes_data = anes_data[anes_data['question'].isin(questions)]

# binarize based on 2016
anes_baseline = anes_data[anes_data['year']==2016]
anes_baseline.groupby(['question', 'answer', 'value']).size()

def build_binarization_mapping(df, question_col="question", value_col="value"):
    """
    For each question, finds the best cutoff to split ordinal levels [1..4]
    into two classes (0/1), attempting to balance class counts.
    Returns a DataFrame with columns [question, value, value_binarized] 
    that acts as a lookup table.
    
    This is intended for baseline data. You can then merge or join this 
    lookup table onto other DataFrames to apply the same binarization.
    """

    mappings = []  # list of small DataFrames, each with (question, value, value_binarized)

    # Group by question
    for question, subdf in df.groupby(question_col):
        # Unique levels in ascending order
        levels = subdf[value_col].sort_values().unique()

        # If <=2 unique levels, binarize trivially:
        if len(levels) <= 2:
            # If exactly 2, define cutoff after the lower level
            if len(levels) == 2:
                cutoff = levels[0]  # e.g. 1 vs 2
                # Build a small DataFrame mapping each level
                tmp = pd.DataFrame({
                    question_col: question,
                    value_col: levels
                })
                tmp["value_binarized"] = (tmp[value_col] > cutoff).astype(int)
            
            else:  # only 1 level
                # Everything is 0
                tmp = pd.DataFrame({
                    question_col: question,
                    value_col: levels,
                    "value_binarized": 0
                })
            
            mappings.append(tmp)
            continue

        # More than 2 levels => find best single cutoff that balances class sizes
        freq = subdf[value_col].value_counts(sort=False)

        best_cutoff = None
        best_diff = None

        # Potential cutoffs are "between" each adjacent pair of levels
        for i in range(len(levels) - 1):
            cutoff_candidate = levels[i]  # split after this
            left_count = freq[levels[: i+1]].sum()
            right_count = freq[levels[i+1 :]].sum()
            diff = abs(left_count - right_count)
            
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_cutoff = cutoff_candidate
        
        # Now build the mapping for *all* unique levels
        tmp = pd.DataFrame({
            question_col: question,
            value_col: levels
        })
        tmp["value_binarized"] = (tmp[value_col] > best_cutoff).astype(int)
        
        mappings.append(tmp)

    # Combine all partial DataFrames into one
    bin_map_df = pd.concat(mappings, ignore_index=True)
    return bin_map_df

binary_map = build_binarization_mapping(anes_baseline)

# great now apply this to all years # 
anes_bin = anes_data.merge(binary_map, on=['question', 'value'], how = 'inner')

# for each year ... 
anes_2016 = anes_bin[anes_bin['year']==2016]
anes_2020 = anes_bin[anes_bin['year']==2020]

anes_2016_wide = anes_2016.pivot(index='ID', columns='question', values='value_binarized')
anes_2020_wide = anes_2020.pivot(index='ID', columns='question', values='value_binarized')

# maybe for now just take not na
anes_2016_wide = anes_2016_wide.dropna()
anes_2020_wide = anes_2020_wide.dropna()

# and only the ID that are in both
idx = anes_2016_wide.index.intersection(anes_2020_wide.index)
anes_2016_wide = anes_2016_wide.loc[idx]
anes_2020_wide = anes_2020_wide.loc[idx]

anes_2016_wide[questions] = anes_2016_wide[questions].astype(int)
anes_2020_wide[questions] = anes_2020_wide[questions].astype(int)

# save the wide formats as well
anes_2016_wide.to_csv('mpf/anes_2016_wide.csv')
anes_2020_wide.to_csv('mpf/anes_2020_wide.csv')

# okay now we can send this to .mpf
from fun import write_to_mpf
        
write_to_mpf(anes_2016_wide, 'mpf', 'anes_2016.txt')
write_to_mpf(anes_2020_wide, 'mpf', 'anes_2020.txt')
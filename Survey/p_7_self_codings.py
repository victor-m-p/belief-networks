import numpy as np 
import pandas as pd 

# participant 16
dict_nodes_16 = {
    # label, node, importance
    (0, 'Consume meat', 'MISSING'),
    (1, 'Health (protein, B12)', 'LOW'),
    (2, 'Nice alternatives', 'LOW'),
    (3, 'Animals have miserable life', 'MEDIUM'),
    (4, 'Not moral to kill', 'MEDIUM'),
    (5, 'Animal rights important', 'HIGH'),
    (6, 'Harm to environment', 'HIGH'),
    (7, 'Situational pressure / culture', 'LOW'),
    (8, 'Climate impact', 'HIGH'),
    (9, 'Friends judge high meat eating', 'HIGH')
}

dict_edges_16 = {
    (0, 1, 'POSITIVE'),
    (0, 2, 'NEGATIVE'),
    (0, 5, 'NEGATIVE'),
    (0, 6, 'NEGATIVE'),
    (0, 7, 'POSITIVE'),
    (0, 8, 'NEGATIVE'),
    (0, 9, 'NEGATIVE'),
    (1, 2, 'NEGATIVE'),
    (2, 5, 'POSITIVE'),
    (2, 6, 'POSITIVE'),
    (3, 5, 'POSITIVE'),
    (4, 5, 'POSITIVE'),
    (5, 6, 'POSITIVE'),
    (5, 8, 'POSITIVE'),
    (5, 9, 'POSITIVE'),
    (6, 8, 'POSITIVE'),
    (7, 8, 'NEGATIVE'),
    (7, 9, 'NEGATIVE'),
    (8, 9, 'POSITIVE')
}

df_nodes_16 = pd.DataFrame(dict_nodes_16, columns=['label', 'node', 'importance'])
df_edges_16 = pd.DataFrame(dict_edges_16, columns=['label_x', 'label_y', 'direction'])

# save this
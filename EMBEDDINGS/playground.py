import numpy as np
from sentence_transformers import SentenceTransformer 
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances

# load the model # 
model_path = "raw/full_data/roberta-base_idx0_epoch3"
model = SentenceTransformer(model_path)

# sentences
sentences = [
    'Trump is the savior of the world',
    'Factory farming is cruel',
    'The earth is flat',
    'Global warming is an existential threat'
]

# embed them
embeddings = model.encode(sentences)

# look at distances between them # 
# which is reasonable 
cos_sim_matrix = cosine_similarity(embeddings)
euc_dist_matrix = euclidean_distances(embeddings)
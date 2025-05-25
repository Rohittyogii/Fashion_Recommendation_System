from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

def get_similar_images(query_vector, feature_df, top_k=5):
    similarities = cosine_similarity([query_vector], list(feature_df['features']))[0]
    top_indices = similarities.argsort()[-top_k:][::-1]
    return feature_df.iloc[top_indices]

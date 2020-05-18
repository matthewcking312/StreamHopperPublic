import spacy
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from search import compute_similarity_search


def test_compute_similarity_search():
    '''
    TEST: Compute the similarity scores between starter items and rest of the
    catalog
    '''
    test_db = pd.read_csv("test_db.csv")
    test_search = test_db.sample(1)
    x_df = compute_similarity_search(test_search, test_db)
    search_title = test_search['title'].iloc[0]
    top_recommendation = x_df['title_y'].iloc[0]
    assert search_title == top_recommendation
    x_df.to_csv("test_recommendations.csv")
    return "Test recommendations saved in test_recommendations.csv"

import pandas as pd
import numpy as np
from kmodes.kmodes import KModes
import pickle
import os


def make_dummy_with_max(df, col, max_val=3):
    """
    Rather than make dummies, I need to specifiy the max value
    This makes this function repeatable
    This also wont break unless questions are renamed
    """
    for val in range(max_val):
        new_col = col + '_v' + str(val + 1)
        df[new_col] = df[col]\
            .apply(lambda x: 1 if x == 'v' + str(val + 1) else 0)
    df.drop(col, axis=1, inplace=True)


def multiple_option_cols(df):
    """
    Helper funciton to cluster_predict_on_questionare
    Takes in a dataframe of one user questionnaire
    Returns it in the format that cluster_v1 wants
    """
    # Steraming Service Creation
    services = ['Amazon Prime', 'Hulu', 'Netflix',
                'HBO', 'Disney+', 'Other', 'None']
    genre_options = ['v1', 'v2', 'v3', 'v4',
                     'v5', 'v6', 'v7']

    for service in services:
        df[service] = 0.0

    for i, option in enumerate(genre_options):
        df.loc[(df.q1.str.contains(option)), services[i]] = 1.0

    # Genre Creation
    genres = ['Action', 'Animation', 'Comedy',
              'Documentary', 'Drama', 'Fantasy',
              'Horror', 'Romance',
              'Science Fiction', 'Thriller']
    genre_options = ['v1', 'v2', 'v3', 'v4', 'v5',
                     'v6', 'v7', 'v8', 'v9', 'v10']

    for genre in genres:
        df[genre] = 0.0

    for i, option in enumerate(genre_options):
        df.loc[(df.q7.str.contains(option)), genres[i]] = 1.0
        df.loc[(df.q8.str.contains(option)), genres[i]] = -1.0

    # Drop used up columns
    df = df.drop(['q1', 'q7', 'q8'], axis=1)

    return df


# Make sure that the filepathway is the full pathway!
def cluster_prediction_v2(row, model_path='models/km_v2.pkl'):
    """
    Only function which should be called in routes
    Takes in a single row (as a df)
    Encodes, predicts, and returns persona number
    """
    qs = ['q2', 'q3', 'q4', 'q5', 'q9', 'q10', 'q11', 'q12', 'q13']
    max_options = [3, 4, 4, 3, 7, 5, 4, 4, 2]
    for i, q in enumerate(qs):
        make_dummy_with_max(df=row, col=q, max_val=max_options[i])
    row_encoded = multiple_option_cols(row)
    row_encoded = row_encoded.drop('username', axis=1)
    with open(model_path, 'rb') as f:
        km = pickle.load(f)

    return km.predict(row_encoded)[0]

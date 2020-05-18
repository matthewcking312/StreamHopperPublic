import pickle
from kmodes.kmodes import KModes
import pandas as pd


def create_dataframe(row):
    '''Creates a dataframe for the questionnaire results'''
    header = ['username', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7',
              'q8', 'q9', 'q10', 'q11', 'q12', 'q13']
    df = pd.DataFrame(row, columns=header)
    df.q6 = df.q6.replace('', 0.0)
    df = df.replace('', 'v1')
    return df


def cluster_predict_on_questionare(response,
                                   model_path='app/models/km_v1.pkl'):
    """
    This functioun takes in a questionnaire response
    loads a model which predicts off that
    Currently working on the label encoded data from 'Questionnaire.csv'
    Output is an int

    Note: Input must be as a 1-row pandas dataframe with columns:
    ['username', 'q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9',
       'q10', 'q11', 'q12', 'q13']
    """

    # Uses a helper function to format the data
    df = cluster_v1_data_convert(response)

    with open(model_path, 'rb') as f:
        km = pickle.load(f)

    return km.predict(df)[0]


def cluster_v1_data_convert(df):
    """
    Helper funciton to cluster_predict_on_questionare
    Takes in a dataframe of one user questionnaire
    Returns it in the format that cluster_v1 wants
    """
    # Steraming Service Creation
    services = ['Amazon Prime', 'Hulu', 'Netflix', 'HBO',
                'Disney+', 'Other', 'None']
    genre_options = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7']

    for service in services:
        df[service] = 0.0

    for i, option in enumerate(genre_options):
        df.loc[(df.q1.str.contains(option)), services[i]] = 1.0

    # Genre Creation
    genres = ['Action', 'Animation', 'Comedy', 'Documentary', 'Drama',
              'Fantasy', 'Horror', 'Romance',
              'Science Fiction', 'Thriller']
    genre_options = ['v1', 'v2', 'v3', 'v4', 'v5',
                     'v6', 'v7', 'v8', 'v9', 'v10']

    for genre in genres:
        df[genre] = 0.0

    for i, option in enumerate(genre_options):
        df.loc[(df.q7.str.contains(option)), genres[i]] = 1.0
        df.loc[(df.q8.str.contains(option)), genres[i]] = -1.0

    # Replace v options with 0 - v-1
    v_map = {option: i for i, option in enumerate(genre_options)}
    cols_to_map = ['q2', 'q3', 'q4', 'q5', 'q9', 'q10', 'q11', 'q12', 'q13']

    for col in cols_to_map:
        df[col] = df[col].map(v_map)

    # Drop used up columns
    df = df.drop(['username', 'q1', 'q7', 'q8'], axis=1)

    # Rename Columns
    df.columns = ['Q2', 'Q3', 'Q4', 'Q5', 'Q6', 'Q9', 'Q10', 'Q11',
                  'Q12', 'Q13', 'Amazon Prime', 'Hulu', 'Netflix',
                  'HBO', 'Disney+', 'Other', 'None', 'Action', 'Animation',
                  'Comedy', 'Documentary', 'Drama', 'Fantasy', 'Horror',
                  'Romance', 'Science Fiction', 'Thriller']
    return df

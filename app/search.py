import spacy
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

#
def compute_similarity_search(search_meta: pd.DataFrame,
                              shows_meta: pd.DataFrame,
                              show_type='movie'):
    '''
    Compute the similarity scores between starter items and rest of the
    catalog
    '''
    x_df = cross_join(search_meta, shows_meta)
    if show_type == 'movie':
        crews = ['content_cast', 'writers', 'producers',
                 'directors', 'composers', 'casting_directors']
    elif show_type == 'tv':
        crews = ['content_cast', 'writers', 'producers']
    x_df['genre_score'] = x_df.apply(lambda x:
                                     compute_genre_similarity(
                                         x['genres_x'],
                                         x['genres_y']),
                                     axis=1)
    x_df['rating_score'] = x_df['rating_y'] / 10.0
    x_df['votes_score'] = np.log10(x_df['votes_y'])

    x_df['votes_score'] = x_df['votes_score'] / x_df['votes_score'].max()

    for crew_type in crews:
        x_df[f'{crew_type}_score'] = x_df.apply(lambda x:
                                                compute_crew_similarity(
                                                    x[f'{crew_type}_x'],
                                                    x[f'{crew_type}_y']),
                                                axis=1)

    x_df['plot_score'] = get_plot_scores(search_meta, shows_meta)
    if show_type == 'movie':
        x_df['avg_score'] = x_df[['rating_score', 'genre_score',
                                  'votes_score', 'directors_score',
                                  'content_cast_score', 'writers_score',
                                  'producers_score',
                                  'casting_directors_score', 'composers_score',
                                  'plot_score']].mean(axis=1)
    else:
        x_df['avg_score'] = x_df[['rating_score', 'genre_score',
                                  'content_cast_score', 'writers_score',
                                  'producers_score',
                                  'plot_score']].mean(axis=1)
    x_df = (x_df.sort_values('avg_score', ascending=False)
                .drop_duplicates(subset=['title_y', 'platform_y'])
                .iloc[:50][['title_y', 'type_y', 'cover_url_y', 'platform_y',
                            'platform_logo_y', 'avg_score']])
    return x_df


def get_plot_scores(starter_meta_df: pd.DataFrame, merged_df: pd.DataFrame):
    '''
    Compute the similarity score between plots using TFIDF
    '''
    # TFIDF
    tfidf = TfidfVectorizer(stop_words='english')
    meta_tfidf = tfidf.fit_transform(merged_df['plot'])
    starter_tfidf = tfidf.transform(starter_meta_df['plot'])
    plot_scores = cosine_similarity(starter_tfidf, meta_tfidf)
    plot_scores /= (plot_scores.max(axis=1, keepdims=True) + 1e-8)
    return plot_scores.flatten()


def compute_rating_similarity(rating_a, rating_b):
    '''Divides rating_b by 10'''
    return rating_b / 10.0


def compute_votes_similarity(votes_a, votes_b):
    '''Log base 10 transforms votes_b'''
    return np.log10(votes_b)


def get_info(imdb_id: int, df: pd.DataFrame, info: str):
    '''Returns the "info" column from df row with imdb_id'''
    return df.loc[df.imdb_id == imdb_id][info].values[0]


def compute_crew_similarity(crew_a, crew_b):
    """This function computes the intersection between the crew members
    of two shows"""
    if crew_a and crew_b:
        crew_a = set(crew_a.split(','))
        crew_b = set(crew_b.split(','))
        return len(crew_a & crew_b) / (len(crew_a)+1e-8)
    return 0.


def compute_genre_similarity(genre_a, genre_b):
    """This function computes the interesection between the genres of
    two shows"""
    if type(genre_b) != str:
        return 0.
    genre_a = set(genre_a)
    genre_b = set(genre_b)
    return len(genre_a & genre_b) / (len(genre_a)+1e-3)


def cross_join(df1, df2):
    """This function performs cross join between two dataframes."""
    df1['key'] = 0
    df2['key'] = 0
    return df1.merge(df2, how='outer', on='key')

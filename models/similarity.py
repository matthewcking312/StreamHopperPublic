import numpy as np
import pandas as pd
from collections import Counter
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from path import Path
import pathmagic  # noqa
from api.imdb_query import collect_metadata, acquire_imdb_data_search
from api.imdb_query import collect_text_data
# !/usr/bin/env python
# coding: utf-8


# TODO:
# * write function to compute weighted average of individual scores
# * those scores are human-designed features, use them in future ML
#   models once user data gets collected (labels)
# * add `test_*` files
# * PEP8

# import sys
# sys.path.append('../')
# import numpy as np
# import pandas as pd
# from collections import Counter
# from api.imdb_query import collect_metadata,
# acquire_imdb_data, collect_text_data
# from path import Path
# # import torch
# # import torch.nn as nn
# # import torch.nn.functional as F
#
# import spacy
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity

nlp = spacy.load('en_core_web_sm')


def get_recommendations_per_persona(df: pd.DataFrame, shows: list, top_n=50):
    ans = (df.loc[(df['starter_title'].isin(shows))
                  & (~df['other_title'].isin(shows))]
             .drop_duplicates(subset=['starter_title', 'other_title']))

    ans = (ans.groupby('other_title')
           .agg(mod=('platform', lambda x: x.value_counts().index[0]),
                avg=('avg_score', 'mean')))

    return (ans.sort_values('avg', ascending=False).reset_index()
               .drop_duplicates(subset=['other_title'])
               .iloc[1:top_n])


def get_recommendations_per_show(df: pd.DataFrame, show: str, top_n=50):
    test = (df.loc[(df['starter_title'] == show)]
            .drop_duplicates(subset=['other_title']))
    return (test.sort_values('avg_score', ascending=False)
            .drop_duplicates(subset=['other_title'])
            .iloc[1:top_n])


def compute_similarity_scores(starter_meta_df: pd.DataFrame,
                              merged_df: pd.DataFrame,
                              imgs_df: pd.DataFrame,
                              show_type='movie'):

    x_df = cross_join(starter_meta_df, merged_df)
    if show_type == 'movie':
        crews = ['cast', 'writers', 'producers', 'directors',
                 'composers', 'casting directors']
    elif show_type == 'tv':
        crews = ['cast', 'writers', 'producers']
    temp = x_df.apply(lambda x: compute_genre_similarity(x['genres_x'],
                                                         x['genres_y']),
                      axis=1)
    x_df['genre_score'] = temp
    temp = x_df.apply(lambda x: compute_genre_similarity(x['rating_x'],
                                                         x['rating_y']),
                      axis=1)
    x_df['rating_score'] = temp
    temp = x_df.apply(lambda x: compute_genre_similarity(x['votes_x'],
                                                         x['votes_y']),
                      axis=1)

    x_df['votes_score'] = temp
    x_df['votes_score'] = x_df['votes_score'] / x_df['votes_score'].max()
    for crew_type in crews:
        crew_x = f'{crew_type}_x'
        crew_y = f'{crew_type}_y'
        temp = x_df.apply(lambda x: compute_crew_similarity(x[crew_x],
                                                            x[crew_y]),
                          axis=1)
        x_df[f'{crew_type}_score'] = temp
    x_df['plot_score'] = get_plot_scores(starter_meta_df, merged_df)

    if show_type == 'tv':

        final_df = x_df[['imdb_id', 'title', 'id', 'title_y',
                         'platform', 'persona', 'genre_score',
                         'rating_score', 'votes_score',
                         'cast_score', 'writers_score',
                         'producers_score', 'plot_score']]
        final_df = load_img_metadata(final_df, imgs_df)
        final_df = final_df[['persona', 'imdb_id', 'title',
                             'id_x', 'title_y', 'platform',
                             'genre_score', 'rating_score',
                             'votes_score', 'cast_score',
                             'writers_score', 'producers_score', 'plot_score',
                             'cover url', 'full cover url']]
        final_df.columns = ['persona', 'starter_id', 'starter_title',
                            'other_id', 'other_title', 'platform',
                            'genre_score', 'rating_score',
                            'votes_score', 'cast_score',
                            'writers_score', 'producers_score',
                            'plot_score', 'cover url', 'full cover url']
        return final_df

    elif show_type == 'movie':

        final_df = x_df[['imdb_id', 'title', 'id', 'title_y',
                         'platform', 'persona', 'genre_score',
                         'rating_score', 'votes_score',
                         'cast_score', 'writers_score',
                         'producers_score', 'directors_score',
                         'composers_score',
                         'casting directors_score', 'plot_score']]
        final_df = load_img_metadata(final_df, imgs_df)
        final_df = final_df[['persona', 'imdb_id', 'title', 'id_x',
                             'title_y', 'platform',
                             'genre_score', 'rating_score',
                             'votes_score', 'cast_score',
                             'writers_score', 'producers_score',
                             'directors_score', 'composers_score',
                             'casting directors_score', 'plot_score',
                             'cover url', 'full cover url']]
        final_df.columns = ['persona', 'starter_id', 'starter_title',
                            'other_id', 'other_title', 'platform',
                            'genre_score', 'rating_score',
                            'votes_score', 'cast_score',
                            'writers_score', 'producers_score',
                            'directors_score', 'composers_score',
                            'casting directors_score',
                            'plot_score', 'cover url', 'full cover url']
        return final_df


def get_starter_metadata(starter_items: pd.DataFrame, show_type: str):
    """
    This function returns meta data (fresh from IMDB)
    of the given `starter` items
    INPUTS:
    starter_items:
            Pandas dataframe of starter items (see test_starter_items.csv)
    OUTPUTS:
    all_starter_meta_df:
                Pandas dataframe of metadata, including text e.g. plots
    """
    all_starter_meta_dfs = pd.DataFrame()
    all_starter_text_dfs = pd.DataFrame()
    num_start = [1, 2, 3, 4, 5]
    for persona, starter_ids in starter_items.iterrows():
        if show_type == 'tv':
            show_ids = [f'show_id{i}' for i in num_start]
            starter_ids = starter_ids[show_ids].values.tolist()
        elif show_type == 'movie':
            movie_ids = [f'movie_id{i}' for i in num_start]
            starter_ids = starter_ids[movie_ids].values.tolist()
        starter_meta_info = acquire_imdb_data_search(starter_ids)
        starter_meta_df = collect_metadata(starter_meta_info, show_type)
        starter_meta_df['persona'] = persona
        all_starter_meta_dfs = all_starter_meta_dfs.append(starter_meta_df)
        starter_text_df = collect_text_data(starter_meta_info)
        all_starter_text_dfs = all_starter_text_dfs.append(starter_text_df)
    all_starter_meta_dfs.reset_index(drop=True, inplace=True)
    all_starter_text_dfs.reset_index(drop=True, inplace=True)
    all_starter_text_dfs.drop_duplicates(subset=['id'], inplace=True)
    all_starter_meta_dfs['id'] = all_starter_meta_dfs['id'].astype(float)
    all_starter_text_dfs['id'] = all_starter_text_dfs['id'].astype(float)
    all_starter_meta_df = all_starter_meta_dfs .merge(all_starter_text_dfs,
                                                      on='id', how='inner')
    return all_starter_meta_df


def compute_rating_similarity(rating_a, rating_b):
    return rating_b / 10.0


def compute_votes_similarity(votes_a, votes_b):
    return np.log10(votes_b)


def get_info(imdb_id: int, df: pd.DataFrame, info: str):
    return df.loc[df.imdb_id == imdb_id][info].values[0]


def preprocess_text(df: pd.DataFrame):
    df['plot'] = df['plot'].replace("\[|\]", '', regex=True)
    df['plot'] = df['plot'].replace("::", ' ', regex=True)
    df['plot'] = df['plot'].replace(" ", '_', regex=True)
    df['plot'] = df['plot'].replace("[^a-zA-Z0-9_-]+", '', regex=True)
    df['plot'] = df['plot'].replace('_', ' ', regex=True)
    df['plot'] = df['plot'].replace('-', ' ', regex=True)
    df['plot'].fillna('', inplace=True)
    return df


def remove_NER(value):
    doc = nlp(value)
    ents = [str(token) for token in doc.ents]
    ents = ' '.join(ents).split(' ')
    plot = [token for token in value.split(' ') if token not in ents]
    return ' '.join(plot)


def list_to_str(plots):
    if type(plots) == list:
        return str(plots[1:-1])
    else:
        return plots


def get_plot_scores(starter_meta_df: pd.DataFrame, merged_df: pd.DataFrame):
    merged_df = preprocess_text(merged_df)
    merged_df['plot'] = merged_df['plot'].apply(remove_NER)

    starter_meta_df['plot'] = starter_meta_df['plot'].apply(list_to_str)
    starter_meta_df = preprocess_text(starter_meta_df)
    starter_meta_df['plot'] = starter_meta_df['plot'].apply(remove_NER)

    # TFIDF
    tfidf = TfidfVectorizer(stop_words='english')
    meta_tfidf = tfidf.fit_transform(merged_df['plot'])
    starter_tfidf = tfidf.transform(starter_meta_df['plot'])
    plot_scores = cosine_similarity(starter_tfidf, meta_tfidf)
    plot_scores /= (plot_scores.max(axis=1, keepdims=True) + 1e-8)
    return plot_scores.flatten()


def load_img_metadata(meta_df: pd.DataFrame, imgs_df: pd.DataFrame):
    imgs_df['id'] = imgs_df['id'].astype(int)
    imgs_df.drop_duplicates(subset=['cover url'], inplace=True)
    ans = meta_df.merge(imgs_df, left_on='imdb_id', right_on='id', how='inner')
    return ans


def compute_crew_similarity(crew_a, crew_b):
    """This function computes the intersection between the crew members
    of two shows"""
    if type(crew_a) != str or type(crew_b) != str:
        return 0
    crew_a = set(crew_a.split(','))
    crew_b = set(crew_b.split(','))
    if len(crew_a) > 0:
        return len(crew_a & crew_b) / len(crew_a)
    else:
        return 0.


def compute_genre_similarity(genre_a, genre_b):
    """This function computes the interesection between the genres of
    two shows"""
    if type(genre_b) != str:
        return 0
    genre_a = set(genre_a)
    genre_b = set(eval(genre_b))
    if len(genre_a) > 0:
        return len(genre_a & genre_b) / len(genre_a)
    else:
        return 0.


def cross_join(df1, df2):
    """This function performs cross join between two dataframes."""
    df1['key'] = 0
    df2['key'] = 0
    return df1.merge(df2, how='outer', on='key')


def load_plot_metadata(meta_df: pd.DataFrame, plots_df: pd.DataFrame):
    """This function adds the plots for shows to a metadata frame"""
    meta_df['imdb_id'] = meta_df['imdb_id'].astype(int)
    meta_df.drop_duplicates(subset=['title'], inplace=True)
    plots_df['id'] = plots_df['id'].astype(int)
    plots_df.drop_duplicates(subset=['plot'], inplace=True)
    return meta_df.merge(plots_df, left_on='imdb_id',
                         right_on='id', how='inner')


def compare_titles(title_a, title_b):
    if type(title_a) != str or type(title_b) != str:
        return False
    if (title_a.lower() in title_b.lower()) or \
       (title_b.lower() in title_a.lower()):
        return True
    return False


if __name__ == "__main__":

    data_path = Path('/Users/alaa/data/stream-hopper/imdb_data_v2/')

    starter_df = pd.read_csv(data_path/'starter_items_v2.csv')

    # guidebox data
    gb_df = pd.read_csv(data_path/'tv.csv')
    print(gb_df.shape)
    gb_df.head()

    meta_df = pd.read_csv(data_path/'tv-meta.csv')
    print(meta_df.shape)
    meta_df.head()

    plots_df = pd.read_csv(data_path/'tv-text.csv')

    meta_df = load_plot_metadata(meta_df, plots_df)

    merged_df = gb_df.merge(meta_df, how='inner', on='imdb_id')

    # TODO: go through this and make sure the shows are the same! DATA CLEANING
    # titles_comparisons = merged_df.apply(lambda x:
    #                compare_titles(x.title_x, x.title_y), axis=1)
    # merged_df[titles_comparisons == False][['title_x', 'title_y']]

    starter_meta_df = get_starter_metadata(starter_df)
    f = "/Users/alaa/data/stream-hopper/imdb_data_v2/tv-imgs.csv"
    imgs_df = pd.read_csv(f)

    x_df = compute_similarity_scores(starter_meta_df, merged_df, imgs_df, 'tv')

    # TODO: save to file
    x_df.to_csv("similarity_scores.csv", index=False)
    s = "Similarity scores have been computed for the given starter items. Bye"
    print(s)

from collections import defaultdict
import sys
import pandas as pd
import numpy as np

from imdb import IMDb
from tqdm import tqdm


"""
This script can be used to collect metadata about shows that were
acquired from guidebox (after using guidebox_query.py).

USAGE: python imdb_query.py [guidebox_data.csv] [show_type]

guidebox_data.csv needs to contain a column named 'imdb_id' that contains the
IMDB ID for each show.
show_type can be 'movie' or 'tv'.
"""


SHOW_TYPES = ['movie', 'tv']


def process_imdb_ids(imdb_ids):
    '''
    This function removes missing and/or repeated IMDB IDs
    :param imdb_ids: Pandas Series containing IMDB IDs for shows
    '''
    imdb_ids = imdb_ids.dropna()
    imdb_ids = imdb_ids.unique()
    return imdb_ids


def acquire_imdb_data(imdb_ids):
    '''
    This function acquires raw IMDB data using IMDB API for each show
    :param imdb_ids: Pandas Series containing IMDB IDs for shows
    '''
    ia = IMDb()
    n = len(imdb_ids)
    with tqdm(total=n) as pbar:
        all_shows_info = []
        for i, show_id in enumerate(imdb_ids):
            show_id = int(''.join(filter(str.isdigit, show_id)))
            show = ia.get_movie(show_id)
            show_id = show.getID()
            show_items = show.items()
            show_info = get_dict_from_items(show_id, show_items)
            all_shows_info.append(show_info)
            pbar.update(1)
    return all_shows_info


def acquire_imdb_data_search(imdb_ids):
    '''
    This function acquires raw IMDB data using IMDB API for each show
    :param imdb_ids: Pandas Series containing IMDB IDs for shows
    '''
    ia = IMDb()
    n = len(imdb_ids)
    with tqdm(total=n) as pbar:
        all_shows_info = []
        for i, show_id in enumerate(imdb_ids):
            show_id = int(show_id)
            show = ia.get_movie(show_id)
            show_id = show.getID()
            show_items = show.items()
            show_info = get_dict_from_items(show_id, show_items)
            all_shows_info.append(show_info)
            pbar.update(1)
    return all_shows_info


def get_dict_from_items(show_id, show_items):
    '''
    This function creates a Python dictionary of the raw IMDB data
    for a given show
    :param show_id: IMDB ID for the show
    :param show_items: list of key-value tuples for the show where key is the
    metadata type (e.g. genre) and value is the metadata info (e.g. action)
    '''
    info_dict = {}
    info_dict['id'] = show_id
    for item in show_items:
        info_dict[item[0]] = item[1]
    return info_dict


def collect_metadata(all_shows_info, show_type):
    '''
    This function collects required metadata from the raw IMDB data and outputs
    them in a Pandas DataFrame
    :param all_shows_info: list of dicts containing raw metadata for all shows
    :param show_type: string specifying type of show.
    Options are 'tv' or 'movie'
    '''
    shows_dict = defaultdict(list)
    if show_type == 'movie':
        for i, show in enumerate(all_shows_info):
            shows_dict = get_movie_info(shows_dict, show)
    elif show_type == 'tv':
        for i, show in enumerate(all_shows_info):
            shows_dict = get_tv_info(shows_dict, show)
    return pd.DataFrame.from_dict(shows_dict)


def get_movie_info(shows_dict, show_info):
    '''
    This function fetches metadata information for a movie and updates the
    dictionary containing metadata information for all the movies
    :param shows_dict: dictionary containing metadata on each movie
    :param show_info: dictionary containing metadata on a single movie
    '''
    shows_dict['id'].append(get_info(show_info, 'id'))
    shows_dict['title'].append(get_info(show_info, 'title'))
    shows_dict['year'].append(get_info(show_info, 'year'))

    show_cast = get_ids(show_info)
    shows_dict['cast'].append(show_cast)
    show_writers = get_ids(show_info, id_type='writer')
    shows_dict['writers'].append(show_writers)
    show_directors = get_ids(show_info, id_type='directors')
    shows_dict['directors'].append(show_directors)
    show_cast_dirs = get_ids(show_info, id_type='casting directors')
    shows_dict['casting directors'].append(show_cast_dirs)
    show_producers = get_ids(show_info, id_type='producers')
    shows_dict['producers'].append(show_producers)
    show_composers = get_ids(show_info, id_type='composers')
    shows_dict['composers'].append(show_composers)

    shows_dict['genres'].append(get_info(show_info, 'genres'))
    shows_dict['kind'].append(get_info(show_info, 'kind'))
    shows_dict['runtimes'].append(get_info(show_info, 'runtimes'))

    shows_dict['rating'].append(get_info(show_info, 'rating'))
    shows_dict['votes'].append(get_info(show_info, 'votes'))
    shows_dict['box_office'].append(get_info(show_info, 'box office'))
    return shows_dict


def get_tv_info(shows_dict, show_info):
    '''
    This function fetches metadata information for a tv show and updates the
    dictionary containing metadata information for all the tv shows
    :param shows_dict: dictionary containing metadata on each tv show
    :param show_info: dictionary containing metadata on a single tv show
    '''
    shows_dict['id'].append(get_info(show_info, 'id'))
    shows_dict['title'].append(get_info(show_info, 'title'))
    shows_dict['year'].append(get_info(show_info, 'year'))

    show_cast = get_ids(show_info, id_type='cast')
    shows_dict['cast'].append(show_cast)
    show_writers = get_ids(show_info, id_type='writer')
    shows_dict['writers'].append(show_writers)
    show_producers = get_ids(show_info, id_type='production companies')
    shows_dict['producers'].append(show_producers)

    shows_dict['genres'].append(get_info(show_info, 'genres'))
    shows_dict['kind'].append(get_info(show_info, 'kind'))
    shows_dict['seasons'].append(get_info(show_info, 'seasons'))
    shows_dict['runtimes'].append(get_info(show_info, 'runtimes'))
    shows_dict['series years'].append(get_info(show_info, 'series years'))

    shows_dict['rating'].append(get_info(show_info, 'rating'))
    shows_dict['votes'].append(get_info(show_info, 'votes'))
    return shows_dict


def get_ids(show_info, id_type='cast', max_num=7):
    '''
    This function fetches the IDs of each member working for a specific crew
    for a specific show
    :param show_info: dictionary containing metadata on a single show
    :param id_type: string specifying the specific team e.g. cast, directors
    :param max_num: integer specifying the maximum number of members to collect
                    info from the crew. Default is 7.
    '''
    if id_type not in show_info.keys():
        return 'NaN', 'NaN'
    ids = show_info[id_type]
    ids_strung = ','.join([entity.getID() for entity in ids[:7]])
    return ids_strung


def get_info(show_info, info_key):
    '''
    This fetches metadata information for a given show for a given key
    e.g. genre
    :param show_info: dictionary containing metadata on a single show
    :param info_key: string containing the type of metadata e.g. genre
    '''
    if info_key not in show_info.keys():
        return 'NaN'
    else:
        return show_info[info_key]


def create_crew_df(all_shows_info, crew_type, max_cast_num=7):
    '''
    This function creates a Pandas dataframe of each crew member's ID and
    corresponding name.
    :param all_shows_info: list of dicts containing raw metadata for all shows
    :param crew_type: string specifying the specific team e.g. cast, directors
                      e.g. cast, writers, directors, producers.
    :param max_cast_num: integer specifying the maximum number of members to
                         collect info from the crew. Default is 7.
    '''
    crew = {}
    for show_info in all_shows_info:
        crew_ids, crew_names = get_crew_info(show_info, crew_type=crew_type,
                                             max_num=max_cast_num)
        for i, idx in enumerate(crew_ids.split(',')):
            crew[idx] = crew_names.split(',')[i]
    return pd.DataFrame(data=crew.items(), columns=['id', 'name'])


def get_crew_info(show_info, crew_type, max_num=7):
    '''
    This function fetches the IDs and names of each member working on a show
    in a certain crew e.g. cast members
    :param show_info: dictionary containing metadata on a single show
    :param crew_type: string specifying the specific team e.g. cast, directors
                      e.g. cast, writers, directors, producers.
    :param max_num: integer specifying the maximum number of members to collect
                    info from the crew. Default is 7.
    '''
    if crew_type not in show_info.keys():
        return 'NaN', 'NaN'
    crew = show_info[crew_type]
    crew_ids = ','.join([human.getID() for human in crew[:7]])
    crew_names = ','.join([human.data['name'] for human in crew[:7]])
    return crew_ids, crew_names


def collect_image_data(all_shows_info):
    '''
    This function creates a dataframe of each show's ID and corresponding
    image URLs.
    :param all_shows_info: list of dicts containing raw metadata for all shows
    '''
    shows_dict = defaultdict(list)
    for i, show in enumerate(all_shows_info):
        shows_id = get_info(show, 'id')
        shows_dict['id'].append(shows_id)
        shows_img1 = get_info(show, 'full-size cover url')
        shows_dict['full cover url'].append(shows_img1)
        shows_img2 = get_info(show, 'cover url')
        shows_dict['cover url'].append(shows_img2)
    return pd.DataFrame.from_dict(shows_dict)


def collect_text_data(all_shows_info):
    '''
    This function creates a dataframe of each show's ID and
    corresponding text metadata.
    :param all_shows_info: list of dicts containing raw metadata for all shows
    '''
    shows_dict = defaultdict(list)
    for i, show in enumerate(all_shows_info):
        shows_id = get_info(show, 'id')
        shows_dict['id'].append(shows_id)
        shows_txt1 = get_info(show, 'plot outline')
        shows_dict['outline'].append(shows_txt1)
        shows_txt2 = get_info(show, 'plot')
        shows_dict['plot'].append(shows_txt2)
    return pd.DataFrame.from_dict(shows_dict)


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Too few/many arguments passed! Aborting"
    shows_filepath = str(sys.argv[1])
    shows_type = str(sys.argv[2])
    assert shows_type in SHOW_TYPES, "Incorrectly specified show type.Aborting"

    shows_df = pd.read_csv(shows_filepath, index_col=0)
    imdb_ids = process_imdb_ids(shows_df['imdb_id'])
    print("Acquiring raw data from IMDB...")
#     ia = IMDb()
    all_shows_info = acquire_imdb_data(imdb_ids)
    metadata_df = collect_metadata(all_shows_info, shows_type)
    print("Meta Data Collection and Assembly Completed")
    shows_meta_filepath = shows_filepath.split('.')[0] + '-meta.csv'
    metadata_df.to_csv(shows_meta_filepath)
    print(f"Meta Data Saved in {shows_meta_filepath}")

    if shows_type == 'movie':
        crew_types = ['cast', 'writer', 'director', 'producers',
                      'casting directors', 'composers']
    elif shows_type == 'tv':
        crew_types = ['cast', 'writer', 'production companies']

    print("Collecting metadata about crew members...")
    for crew_type in crew_types:
        crew_df = create_crew_df(all_shows_info, crew_type)
        crew_filepath = shows_filepath.split('.')[0] + f'-{crew_type}.csv'
        crew_df.to_csv(crew_filepath)
        print(f"{crew_type} metadata saved in {crew_filepath}")

    imgs_df = collect_image_data(all_shows_info)
    imgs_filepath = shows_filepath.split('.')[0] + '-imgs.csv'
    imgs_df.to_csv(imgs_filepath)
    print(f"Images metadata saved in {imgs_filepath}")
    text_df = collect_text_data(all_shows_info)
    text_filepath = shows_filepath.split('.')[0] + '-text.csv'
    text_df.to_csv(text_filepath)
    print(f"Text metadata saved in {text_filepath}")

    print("Metdata Acquisition, Collection, and Storage has been successful")

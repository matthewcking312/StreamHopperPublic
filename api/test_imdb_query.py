from imdb import IMDb


def test_movies():
    '''Test that the IMDB IDs for movie titles have not changed'''
    ia = IMDb()
    title1 = get_info(ia.get_movie('0480249').items(), 'title')
    assert title1 == 'I Am Legend'
    title2 = get_info(ia.get_movie('7784604').items(), 'title')
    assert title2 == 'Hereditary'
    title3 = get_info(ia.get_movie('3774802').items(), 'title')
    assert title3 == 'Pandemic'


def test_tv():
    '''Test that the IMDB IDs for tv shows have not changed'''
    ia = IMDb()
    title1 = get_info(ia.get_movie('0386676').items(), 'title')
    assert title1 == 'The Office'
    title2 = get_info(ia.get_movie('0285403').items(), 'title')
    assert title2 == 'Scrubs'
    title3 = get_info(ia.get_movie('11823076').items(), 'title')
    assert title3 == 'Tiger King'


def get_info(show_items, info_type):
    '''Helper function to get the required info from IMDB API'''
    for key_val in show_items:
        if key_val[0] == info_type:
            info = key_val[1]
            return info
    return None

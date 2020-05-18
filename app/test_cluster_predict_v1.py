import pandas as pd
from .cluster_predict_v1 import cluster_v1_data_convert
from .cluster_predict_v1 import cluster_predict_on_questionare
from .cluster_predict_v1 import create_dataframe


def test_create_dataframe():
    """Tests that input can be created into desired format"""
    row = [['<User 1>', "['v1', 'v2']", 'v1', 'v2', 'v3',
            'v2', 'v2', "['v1', 'v4', 'v5']", "['v1', 'v4', 'v5']",
            'v1', 'v2', 'v2', 'v3', 'v2']]

    assert type(create_dataframe(row)) == pd.DataFrame
    assert create_dataframe(row). shape[0] == 1


def test_cluster_predict_on_questionare():
    """
    Tests edge cases
    Tests only work for model v1
    """

    blank_row = [['<User X>', "[]", '', '', '', '', '',
                  "[]", "[]", '', '', '', '', '']]
    blank_df = create_dataframe(blank_row)
    assert cluster_predict_on_questionare(blank_df) == 2

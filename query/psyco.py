import pandas as pd
import pandas.io.sql as sqlio
import psycopg2


user = 'service'
pw = 'streamer'
host_url = "stream.csgvua23atk1.us-west-2.rds.amazonaws.com"
dbname = 'postgres'


def connect(user, pw, host_url, dbname):
    """
    This function will connect to our database if it is provided username,
    password, dbname, and host url. It will return a connection object that
    can be used to run a query from the database.
    """
    try:
        conn_s = f"dbname={dbname} user={user} host={host_url} password={pw}"
        conn = psycopg2.connect(conn_s)
    except ConnectionError:
        print("I am unable to connect to the database")

    return conn


conn = connect(user, pw, host_url, dbname)


def query_to_df(query, conn):
    """
    Given a query and a connection object, this funcion will return the data
    retrieved from the query as a pandas dataframe.
    """
    return sqlio.read_sql_query(query, conn)

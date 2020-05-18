import pandas as pd
import pandas.io.sql as sqlio
import psycopg2

user = user_name
pw = user_pw
host_url = host_url
dbname = db_name


def connect(user, pw, host_url, dbname):
    """
    This function will connect to our database if it is provided username,
    password, dbname, and host url. It will return a connection object that
    can be used to run a query from the database.
    """
    try:
        s = f"dbname={dbname} user={user} host={host_url} password={pw}"
        conn = psycopg2.connect(s)
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


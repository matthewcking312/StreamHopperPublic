import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    # + os.path.join(basedir, 'streamhopper.db')
    s = 'postgresql://postgres:5'
    s += 'ti92C5SoZfB@stream.csgvua23atk1.us-west-2.rds.amazonaws.com/postgres'
    SQLALCHEMY_DATABASE_URI = s
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)

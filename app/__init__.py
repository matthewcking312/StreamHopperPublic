from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


application = Flask(__name__)
application.config.from_object(Config)
Bootstrap(application)

db = SQLAlchemy(application)
db.create_all()
db.session.commit()

login_manager = LoginManager()
login_manager.init_app(application)

# Added at the bottom to avoid circular dependencies.
# (Altough it violates PEP8 standards)
from app import classes
from app import routes

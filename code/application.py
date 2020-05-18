import datetime
from flask import Flask
from flask import render_template, render_template_string, redirect
import simplejson
import urllib.request
import boto3
import time

application = Flask(__name__)


@application.route('/', methods=['GET', 'POST'])
def home():
    '''Renders the home page html'''
    return render_template('home.html')


if __name__ == '__main__':
    application.jinja_env.auto_reload = True
    application.config['TEMPLATES_AUTO_RELOAD'] = True
    application.debug = True
    application.run()

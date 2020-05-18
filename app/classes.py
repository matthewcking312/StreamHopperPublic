from flask_login import UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import (DateField, IntegerField, PasswordField, SelectField,
                     StringField, SubmitField, RadioField, SelectMultipleField,
                     widgets)
from wtforms.validators import DataRequired, InputRequired
from app import db, login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_email(self):
        return self.email


class Questionnaire(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    q1 = db.Column(db.String(80), nullable=False)
    q2 = db.Column(db.String(120), nullable=False)
    q3 = db.Column(db.String(120), nullable=False)
    q4 = db.Column(db.String(120), nullable=False)
    q5 = db.Column(db.String(120), nullable=False)
    q6 = db.Column(db.String(120), nullable=False)
    q7 = db.Column(db.String(120), nullable=False)
    q8 = db.Column(db.String(120), nullable=False)
    q9 = db.Column(db.String(120), nullable=False)
    q10 = db.Column(db.String(120), nullable=False)
    q11 = db.Column(db.String(120), nullable=False)
    q12 = db.Column(db.String(120), nullable=False)
    q13 = db.Column(db.String(120), nullable=False)

    def __init__(self, username, q1, q2, q3, q4, q5, q6, q7,
                 q8, q9, q10, q11, q12, q13):
        self.username = username
        self.q1 = q1
        self.q2 = q2
        self.q3 = q3
        self.q4 = q4
        self.q5 = q5
        self.q6 = q6
        self.q7 = q7
        self.q8 = q8
        self.q9 = q9
        self.q10 = q10
        self.q11 = q11
        self.q12 = q12
        self.q13 = q13


class UserPersona(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    persona = db.Column(db.Integer, nullable=False)

    def __init__(self, username, persona):
        self.username = username
        self.persona = persona


class QuestionnaireMovie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    imdb_id = db.Column(db.String(80), unique=False, nullable=False)

    def __init__(self, username, imdb_id):
        self.username = username
        self.imdb_id = imdb_id


class QuestionnaireShows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    imdb_id = db.Column(db.String(80), unique=False, nullable=False)

    def __init__(self, username, imdb_id):
        self.username = username
        self.imdb_id = imdb_id


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class LogInForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class ProjectForm(FlaskForm):
    name = StringField('Project Name:', validators=[DataRequired()])
    organization = StringField('Organization:', validators=[DataRequired()])
    start_date = StringField('Start Date:', validators=[DataRequired()])
    end_date = StringField('End Date:', validators=[DataRequired()])
    details = StringField('Details:', validators=[DataRequired()])
    submit = SubmitField('Enter')


class MultiCheckboxField(SelectMultipleField):
    """Class for checkbox field"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class QuestionForm(FlaskForm):
    """Class for questionnaire"""
    q1 = MultiCheckboxField('question1', choices=[('v1', 'Amazon Prime'),
                                                  ('v2', 'Hulu'),
                                                  ('v3', 'Netflix'),
                                                  ('v4', 'HBO'),
                                                  ('v5', 'Disney+'),
                                                  ('v6', 'Other'),
                                                  ('v7', 'None')],
                            validators=[InputRequired()])
    q2 = RadioField('question2', choices=[('v1', 'Movies'),
                                          ('v2', 'TV Shows'),
                                          ('v3', 'No Preference')])
    q3 = RadioField('question3', choices=[('v1', '1-3 hours'),
                                          ('v2', '4-7 hours'),
                                          ('v3', '8-11 hours'),
                                          ('v4', '11+ hours')])
    q4 = RadioField('question4', choices=[('v1', 'Single'),
                                          ('v2', 'Married'),
                                          ('v3', 'In a relationship'),
                                          ('v4', "It's complicated")])
    q5 = RadioField('question5', choices=[('v1', 'Male'),
                                          ('v2', 'Female'),
                                          ('v3', 'Other')])
    q6 = IntegerField('age', validators=[InputRequired()])
    q7 = MultiCheckboxField('question7', choices=[('v1', 'Action'),
                                                  ('v2', 'Animation'),
                                                  ('v3', 'Comedy'),
                                                  ('v4', 'Documentary'),
                                                  ('v5', 'Drama'),
                                                  ('v6', 'Fantasy'),
                                                  ('v7', 'Horror'),
                                                  ('v8', 'Romance'),
                                                  ('v9', 'Science Fiction'),
                                                  ('v10', 'Thriller'),
                                                  ('v11', 'Other')])
    q8 = MultiCheckboxField('question8', choices=[('v1', 'Action'),
                                                  ('v2', 'Animation'),
                                                  ('v3', 'Comedy'),
                                                  ('v4', 'Documentary'),
                                                  ('v5', 'Drama'),
                                                  ('v6', 'Fantasy'),
                                                  ('v7', 'Horror'),
                                                  ('v8', 'Romance'),
                                                  ('v9', 'Science Fiction'),
                                                  ('v10', 'Thriller'),
                                                  ('v11', 'Other')])
    q9 = RadioField('question9', choices=[('v1', 'Road Trip'),
                                          ('v2', 'Exercise/ Play Sports'),
                                          ('v3', 'Shopping'),
                                          ('v4', 'Go to the beach'),
                                          ('v5', 'Bar Hop'),
                                          ('v6', 'Try a new restaurant'),
                                          ('v7', 'Relax at home')])
    q10 = RadioField('question10', choices=[('v1', 'Friends'),
                                            ('v2', 'Solo'),
                                            ('v3', 'Kids'),
                                            ('v4', 'Significant Other'),
                                            ('v5', 'Other')])
    q11 = RadioField('question11', choices=[('v1', 'Northeast'),
                                            ('v2', 'Midwest'),
                                            ('v3', 'South'),
                                            ('v4', 'West')])
    q12 = RadioField('question12', choices=[('v1', 'Often'),
                                            ('v2', 'Occasionally'),
                                            ('v3', 'Rarely'),
                                            ('v4', 'Never')])
    q13 = RadioField('question13', choices=[('v1', 'Yes'),
                                            ('v2', 'No')])
    submit = SubmitField('Submit')


@login_manager.user_loader
def load_user(id):
    '''Function to help login/load a user'''
    return User.query.get(int(id))


db.create_all()
db.session.commit()

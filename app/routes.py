from app import application, classes, db
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, login_required, logout_user
from app.cluster_predict_v1 import create_dataframe
from app.cluster_predict_v2 import cluster_prediction_v2
from psyco import connect, query_to_df
import re
from app.search import compute_similarity_search


@application.route('/index')
@application.route('/')
def index():
    """ Render the landing page. """
    return render_template('index.html',
                           authenticated_user=current_user.is_authenticated)


@application.route('/about')
def about():
    """ Render the about us page. """
    return render_template('about.html',
                           authenticated_user=current_user.is_authenticated)


@application.route('/register', methods=('GET', 'POST'))
def register():
    """
    Create a new user in the database (username, email, pw) if does not
    already exist. If succesful, render questionnaire page.
    """
    registration_form = classes.RegistrationForm()
    if registration_form.validate_on_submit():
        username = registration_form.username.data
        password = registration_form.password.data
        email = registration_form.email.data

        user_count = classes.User.query.filter_by(username=username).count()
        email_count = classes.User.query.filter_by(email=email).count()
        if user_count > 0:
            flash(f'Username \'{username}\' already taken.')
        elif email_count > 0:
            flash(f'Email \'{email}\' already registered.')
        else:
            user = classes.User(username, email, password)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('questionnaire'))
    return render_template('register.html', form=registration_form)


@application.route('/login', methods=['GET', 'POST'])
def login():
    """
    Takes a username and password, if password is validated,
    render user dashboard.
    """
    login_form = classes.LogInForm()
    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user = classes.User.query.filter_by(username=username).first()

        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Incorrect username or password.')
            return redirect(url_for('login'))
    return render_template('login.html', form=login_form)


@application.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    """
    This function renders the user dashboard, passing in
    recommendation results to load on that tab.
    """
    if not current_user.is_authenticated:
        print('get outta here')
        return redirect(url_for('login'))
    user = current_user

    user_count = classes.Questionnaire.query\
        .filter_by(username=current_user.username).count()
    if user_count == 0:
        return redirect(url_for('questionnaire'))
    persona = classes.UserPersona.query\
        .filter_by(username=current_user.username).first().persona

    questionnaire = classes.Questionnaire.query\
        .filter_by(username=current_user.username).first()

    user = user_name
    pw = user_pw
    host_url = host_url
    dbname = db_names

    conn = connect(db_user, pw, host_url, dbname)
    streaming_query = "select lhs.*, rhs.logo_url\
     from public.streaming_predictions as lhs\
     left join services.platforms as rhs\
     on lhs.service = rhs.platform\
      where persona={}".format(persona)

    streaming_df = query_to_df(streaming_query, conn)

    service = streaming_df.service.values[0]
    service_url = streaming_df.service_url.values[0]
    price = streaming_df.price.values[0]
    rec_movie1 = streaming_df.item1.values[0]
    rec_movie2 = streaming_df.item2.values[0]
    rec_show1 = streaming_df.item3.values[0]
    rec_show2 = streaming_df.item4.values[0]

    service_logo = streaming_df.logo_url.values[0]
    rec_movie1_image = streaming_df.item1_image_link.values[0]
    rec_movie2_image = streaming_df.item2_image_link.values[0]
    rec_show1_image = streaming_df.item3_image_link.values[0]
    rec_show2_image = streaming_df.item4_image_link.values[0]

    return render_template('user_dashboard.html', user=user, q=questionnaire,
                           service=service, price=price, rec_movie1=rec_movie1,
                           rec_movie2=rec_movie2, rec_show1=rec_show1,
                           rec_show2=rec_show2, persona=persona,
                           service_url=service_url, service_logo=service_logo,
                           rec_movie1_image=rec_movie1_image,
                           rec_movie2_image=rec_movie2_image,
                           rec_show1_image=rec_show1_image,
                           rec_show2_image=rec_show2_image,
                           authenticated_user=current_user.is_authenticated)


@application.route('/search_result', methods=['GET', 'POST'])
@login_required
def search_result():
    """
    This function queries the db and renders search result page.
    """
    title = request.args.get('title')
    title = re.sub(r'\W+', '', title).lower()

    user = user_name
    pw = user_pw
    host_url = host_url
    dbname = db_names

    conn = connect(db_user, pw, host_url, dbname)

    # Get the title argument from the URL that was entered
    search_query = f'''SELECT * FROM public.search_new
                       WHERE search_title ilike '%{title}%'
                       ORDER BY char_length(search_title)
                       LIMIT 1'''
    search_result = query_to_df(search_query, conn)
    if search_result.shape[0] == 0:
        content = []
        curr_user_auth = current_user.is_authenticated
        return render_template('search.html', content=content,
                               authenticated_user=curr_user_auth)
    show_type = search_result['type'].values[0].lower()
    if show_type == 'movie':
        search_query = """SELECT *
                        FROM movie_search;"""
        search_db = query_to_df(search_query, conn)
    else:
        show_type = 'tv'
        search_query = """SELECT *
                        FROM tv_search;"""
        search_db = query_to_df(search_query, conn)
    if title is None:
        return render_template('search.html')
    else:
        ans = compute_similarity_search(search_result, search_db, show_type)
        ans = ans.sort_values('avg_score', ascending=False)
        content = list(zip(ans['title_y'], ans['platform_y'], ans['type_y'],
                           ans['platform_logo_y'], ans['cover_url_y']))
        curr_user_auth = current_user.is_authenticated
        return render_template('search.html', content=content,
                               authenticated_user=curr_user_auth)


@application.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    """Submit answers from a client machine."""
    file = classes.QuestionForm()  # file : UploadFileForm class instance
    if file.validate_on_submit():
        user = str(current_user.username)
        q1 = str(file.q1.data)
        q2 = str(file.q2.data)
        q3 = str(file.q3.data)
        q4 = str(file.q4.data)
        q5 = str(file.q5.data)
        q6 = str(file.q6.data)
        q7 = str(file.q7.data)
        q8 = str(file.q8.data)
        q9 = str(file.q9.data)
        q10 = str(file.q10.data)
        q11 = str(file.q11.data)
        q12 = str(file.q12.data)
        q13 = str(file.q13.data)

        answer_row = [[user, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10,
                       q11, q12, q13]]

        df = create_dataframe(answer_row)

        persona_val = cluster_prediction_v2(df)
        persona = classes.UserPersona(user, int(persona_val))

        questionnaire = classes.Questionnaire(user, q1, q2, q3, q4, q5, q6, q7,
                                              q8, q9, q10, q11, q12, q13)

        user_count = (classes.Questionnaire.query.
                      filter_by(username=current_user.username).count())
        if user_count > 0:
            old_submission = classes.Questionnaire.query.filter_by(
                username=current_user.username).first()
            old_persona = classes.UserPersona.query.filter_by(
                username=current_user.username).first()

            db.session.delete(old_submission)
            db.session.delete(old_persona)
            db.session.commit()

        db.session.add(persona)
        db.session.add(questionnaire)
        db.session.commit()
        return redirect(url_for('questionnaire_content'))  # Redirect
    return render_template('questionnaire.html', form=file)


@application.route("/questionnaire_content", methods=['GET', 'POST'])
@login_required
def questionnaire_content():
    """
    This is the second questionnaire of our user registration period.
    """
    user = user_name
    pw = user_pw
    host_url = host_url
    dbname = db_names

    conn = connect(user, pw, host_url, dbname)
    movie_query = "select * from movie_questionnaires"
    movies_df = query_to_df(movie_query, conn)

    tv_query = "select * from tv_questionnaires"
    tv_df = query_to_df(tv_query, conn)

    movie_list = list(zip(movies_df.imdb_id, movies_df.cover_url))
    tv_list = list(zip(tv_df.imdb_id, tv_df.cover_url))

    return render_template('questionnaire_content.html', movie_list=movie_list,
                           tv_list=tv_list)


@application.route("/update_content", methods=['GET', 'POST'])
def update_content():
    """
    This function receives the data of the movies that the user has clicked on.
    """
    data = request.get_json(force=True)
    user = current_user

    movies = data["movies"].split(",")
    shows = data["shows"].split(",")

    # Check to see if there are any existing users in the table.
    # If so, delete their old entries when they submit.
    user_count = (classes.QuestionnaireMovie.query.filter_by(
        username=current_user.username).count() +
        classes.QuestionnaireShows.query.filter_by(
            username=current_user.username).count())
    if user_count > 0:
        deleted_movies = classes.QuestionnaireMovie.query.filter_by(
            username=current_user.username).delete()
        deleted_shows = classes.QuestionnaireShows.query.filter_by(
            username=current_user.username).delete()
        db.session.commit()

    for movie_id in movies:
        movie_questionnaire = classes.QuestionnaireMovie(user.username,
                                                         movie_id)

        db.session.add(movie_questionnaire)
        db.session.commit()

    for show_id in shows:
        shows_questionnaire = classes.QuestionnaireShows(user.username,
                                                         show_id)

        db.session.add(shows_questionnaire)
        db.session.commit()

    return "completed"


@application.route('/logout')
@login_required
def logout():
    '''Logout a user that is logged in'''
    logout_user()
    return redirect(url_for('index'))


@application.errorhandler(401)
def re_route(e):
    '''Generate the url to the login page'''
    return redirect(url_for('login'))

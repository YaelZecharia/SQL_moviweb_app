from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from datamanager.sql_data_manager import SQLiteDataManager, db, Movie, User, UserNotFoundError, UserAlreadyExists, MovieNotFound, \
    WrongPassword
from datamanager.user_data_manager import User

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Get the secret key from environment variable
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize the data manager object
db_path = os.path.join(os.path.dirname(__file__), "data", "database_file.db")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
data_manager = SQLiteDataManager(app)


# Set flash message duration
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}


@login_manager.user_loader
def loader_user(user_id):
    """
    Creating user object from a user in the json file to use for the flask_login
    """
    users = data_manager.get_all_users()
    user_data = data_manager.get_userinfo_by_id(user_id)
    if user_data:
        return User(user_id, user_data)


# Define route for the home page
@app.route('/')
def home():
    users = data_manager.get_all_users()
    return render_template('index.html')


# Define route for the list of users
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()  # Get all users
    return render_template('users.html', users=users)


# Define route for user movies, allowing both GET and POST requests
@app.route('/users/<int:user_id>', methods=["POST", "GET"])
@login_required
def user_movies(user_id):
    # Check if the logged-in user's id matches the user_id for this route
    if str(current_user.get_id()) != str(user_id):
        flash("Unauthorized!")
        return redirect(url_for("home"))
    try:
        # If it's a POST request, try to add a new movie
        if request.method == "POST":
            try:
                title = request.form['name']  # Get movie title from the form data
                data_manager.add_movie(str(user_id), title)
                return redirect(url_for("user_movies", user_id=user_id))
            except Exception as e:
                flash(f"{e}")
                return redirect(url_for("user_movies", user_id=user_id))

        # If it's a GET request, display the user's movies
        username = data_manager.get_username_by_id(user_id)
        movies = data_manager.get_user_movies(str(user_id))
        return render_template('movies.html', movies=movies, username=username, user_id=user_id)
    except UserNotFoundError as e:
        flash(f"{e}")
        return redirect(url_for("list_users"))


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=["POST", "GET"])
@login_required
def update_movie(user_id, movie_id):
    # If it's a POST request, try to update the movie
    if request.method == "POST":
        # Get the movie info
        movie_info = data_manager.get_movie_by_id(user_id, movie_id)
        # Define the updated movie data
        updated_movie_data = {
            'name': request.form['name'],
            'year': request.form['year'],
            'rating': request.form['rating'],
            'director': request.form['director'],
            'poster': movie_info['poster']
        }
        try:
            data_manager.update_movie(user_id, movie_id, updated_movie_data)
            return redirect(url_for("user_movies", user_id=user_id))
        except UserNotFoundError as e:
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))
    # If it's a GET request, display the form to update the movie
    else:
        try:
            movie_info = data_manager.get_movie_by_id(user_id, movie_id)
            return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie_info=movie_info)
        except UserNotFoundError as e:
            # Handle the case when the user or movie is not found
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))


# Define route for deleting a movie
@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=["POST"])
@login_required
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(str(user_id), str(movie_id))
        return redirect(url_for("user_movies", user_id=user_id))
    except MovieNotFound as e:
        # Handle the case when the movie is not found
        flash(f"{e}")
        return redirect(url_for("user_movies", user_id=user_id))


# Define error handler for 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/login/<int:user_id>', methods=["GET", "POST"])
def login(user_id):
    """
    Checking the hashed password with password the user entered on the web site
    Creating user object for session authentication with flask_login.
    If no exception happen - login the user to the session using 'login_user'
    """
    user = data_manager.get_userinfo_by_id(user_id)

    if user is not None:
        user_name = user["name"]
    else:
        user_name = None
    if str(current_user.get_id()) != str(user_id):
        try:
            if request.method == 'POST':
                login_password = request.form.get('password')
                hashed_pass = user['password']
                data_manager.authenticate_user(login_password, hashed_pass)
                user_obj = User(user_id, user)
                login_user(user_obj)
                return redirect(url_for("user_movies", user_id=user_id))
            return render_template("login.html", user_id=user_id, user_name=user_name)
        except WrongPassword:
            flash('Incorrect password!')
            return render_template('login.html', user_id=user_id, user_name=user_name)
    else:
        return redirect(url_for("user_movies", user_id=user_id))


@app.route('/add_user', methods=['GET', 'POST'])
def new_user():
    """
    A web page for adding a user, getting name,password, confirmed_password from the user
     and give the user a unique id.
     Handling exception in case of password or user problems
    """
    try:
        if request.method == 'POST':
            user_name = request.form.get('name')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm-password')
            data_manager.add_user(user_name, password, confirm_password)
            return redirect(url_for("list_users"))
        return render_template('add_user.html')
    except UserAlreadyExists:
        flash("User Already Exists!")
        return render_template('add_user.html')
    except WrongPassword:
        flash("Password needs to be at least 8 characters")
        return render_template('add_user.html')


@app.route('/logout')
@login_required
def logout():
    # Log out the user and clear the session
    logout_user()
    flash('Logged out successfully!')
    return redirect(url_for('home'))


@app.route('/users/<user_id>/add_review/<movie_id>', methods=["POST", "GET"])
@login_required
def add_review_route(user_id, movie_id):
    # If it's a POST request, try to add the review
    if request.method == "POST":
        review_text = request.form['review_text']
        rating = request.form['rating']

        try:
            data_manager.add_review(user_id, movie_id, review_text, rating)
            flash("Review added successfully!")
            return redirect(url_for("user_movies", user_id=user_id))
        except (UserNotFoundError, MovieNotFound) as e:
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))

    # If it's a GET request, display the form to add a review
    else:
        try:
            movie_info = data_manager.get_movie_by_id(user_id, movie_id)
            return render_template('add_review.html', user_id=user_id, movie_id=movie_id, movie_info=movie_info)
        except (UserNotFoundError, MovieNotFound) as e:
            # Handle the case when the user or movie is not found
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))


@app.route('/movie_reviews/<int:movie_id>', methods=['GET'])
def movie_reviews(movie_id):
    # Fetch the movie from the database using the movie_id
    movie = Movie.query.get(movie_id)

    if not movie:
        # Handle the case where the movie doesn't exist
        flash("Movie not found!")
        return redirect(url_for('home'))

    # Access the associated reviews
    reviews = movie.reviews

    return render_template('movie_reviews.html', movie=movie, reviews=reviews)


# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)

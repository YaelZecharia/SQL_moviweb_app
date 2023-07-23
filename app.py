from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.json_data_manager import JSONDataManager, UserNotFoundError, UserAlreadyExists, MovieNotFound
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")  # Get the secret key from environment variable

# Initialize the data manager object
data_manager = JSONDataManager('users_data.json')

# Set flash message duration
app.config['MESSAGE_FLASHING_OPTIONS'] = {'duration': 5}


# Define route for the home page
@app.route('/')
def home():
    return render_template('index.html')


# Define route for the list of users
@app.route('/users')
def list_users():
    users = data_manager.get_all_users()  # Get all users
    return render_template('users.html', users=users)


# Define route for user movies, allowing both GET and POST requests
@app.route('/users/<int:user_id>', methods=["POST", "GET"])
def user_movies(user_id):
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


# Define route for adding a new user, allowing both GET and POST requests
@app.route('/add_user', methods=["POST", "GET"])
def new_user():
    # If it's a POST request, try to add the new user
    if request.method == "POST":
        user_name = request.form['name']  # Get username from the form data
        try:
            data_manager.add_user(user_name)
            return redirect(url_for("list_users"))
        except UserAlreadyExists as e:
            flash(f"{e}")
            return redirect(url_for("new_user"))
    # If it's a GET request, display the form to add a new user
    else:
        return render_template('add_user.html')


# Define route for updating a movie, allowing both GET and POST requests
@app.route('/users/<user_id>/update_movie/<movie_id>', methods=["POST", "GET"])
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
            data_manager.update_movie(str(user_id), str(movie_id), updated_movie_data)
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


# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.json_data_manager import JSONDataManager, UserNotFoundError, UserAlreadyExists, MovieNotFound
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
data_manager = JSONDataManager('users_data.json')  # creating a data_manager object


@app.route('/')
def home():
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    try:
        username = data_manager.get_username_by_id(user_id)
        movies = data_manager.get_user_movies(str(user_id))
        return render_template('movies.html', movies=movies, username=username, user_id=user_id)
    except UserNotFoundError as e:
        flash(f"{e}")
        return redirect(url_for("list_users"))


@app.route('/add_user', methods=["POST", "GET"])
def new_user():
    if request.method == "POST":
        user_name = request.form['name']
        try:
            data_manager.add_user(user_name)
            return redirect(url_for("list_users"))
        except UserAlreadyExists as e:
            flash(f"{e}")
            return redirect(url_for("new_user"))
    else:
        return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=["POST", "GET"])
def add_movie(user_id):
    if request.method == "POST":
        try:
            title = request.form['name']
            data_manager.add_movie(str(user_id), title)
            return redirect(url_for("user_movies", user_id=user_id))
        except Exception as e:
            flash(f"{e}")
            return redirect(url_for("add_movie", user_id=user_id))
    else:
        return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=["POST", "GET"])
def update_movie(user_id, movie_id):
    if request.method == "POST":
        updated_movie_data = {
            'name': request.form['name'],
            'year': request.form['year'],
            'rating': request.form['rating'],
            'director': request.form['director']
        }
        try:
            data_manager.update_movie(str(user_id), str(movie_id), updated_movie_data)
            return redirect(url_for("user_movies", user_id=user_id))
        except UserNotFoundError as e:
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))
    else:
        try:
            movie_info = data_manager.get_movie_by_id(user_id, movie_id)
            return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie_info=movie_info)
        except UserNotFoundError as e:
            # Handle the case when the user or movie is not found
            flash(f"{e}")
            return redirect(url_for("user_movies", user_id=user_id))


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=["POST"])
def delete_movie(user_id, movie_id):
    try:
        data_manager.delete_movie(str(user_id), str(movie_id))
        return redirect(url_for("user_movies", user_id=user_id))
    except MovieNotFound as e:
        # Handle the case when the movie is not found
        flash(f"{e}")
        return redirect(url_for("user_movies", user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)

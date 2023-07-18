from flask import Flask, render_template, request, redirect, url_for
from datamanager.json_data_manager import JSONDataManager

app = Flask(__name__)
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
    users = data_manager.get_all_users()
    username = users[str(user_id)]['name']
    movies = data_manager.get_user_movies(str(user_id))
    return render_template('movies.html', movies=movies, username=username, user_id=user_id)


@app.route('/add_user', methods=["POST", "GET"])
def new_user():
    if request.method == "POST":
        user_name = request.form['name']
        data_manager.add_user(user_name)
        return redirect(url_for("list_users"))
    else:
        return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=["POST", "GET"])
def add_movie(user_id):
    if request.method == "POST":
        title = request.form['name']
        data_manager.add_movie(str(user_id), title)
        return redirect(url_for("user_movies", user_id=user_id))
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
        data_manager.update_movie(str(user_id), str(movie_id), updated_movie_data)
        return redirect(url_for("user_movies", user_id=user_id))
    else:
        movie_info = data_manager.get_movie_by_id(user_id, movie_id)
        return render_template('update_movie.html', user_id=user_id, movie_id=movie_id, movie_info=movie_info)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=["POST"])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(str(user_id), str(movie_id))
    return redirect(url_for("user_movies", user_id=user_id))


if __name__ == '__main__':
    app.run(debug=True)

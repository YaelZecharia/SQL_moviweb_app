from flask import Blueprint, jsonify


api = Blueprint('api', __name__)


@api.route('/users', methods=['GET'])
def get_users():
    """
    getting a list of all the users in the database
    """
    from app import data_manager
    users = [{"username": user.name, "id": user.id} for user in data_manager.get_all_users()]

    return jsonify(users)


@api.route('/users/<user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """
    getting a list of all the movies of the user
    """
    from app import data_manager
    user_movies = data_manager.get_user_movies(user_id)
    movie_names = [movie_info['name'] for movie_info in user_movies.values()]

    return jsonify(movie_names)


@api.route('/movies', methods=["GET"])
def get_movies():
    """
    getting a list of all the movies in the database
    """
    from app import data_manager
    movies = [{"title": movie.title, "id": movie.id} for movie in data_manager.get_all_movies()]

    return jsonify(movies)


@api.route('/movies/<movie_id>/reviews', methods=["GET"])
def get_movie_reviews(movie_id):
    from app import data_manager
    reviews = data_manager.get_movie_reviews(movie_id)

    return jsonify(reviews)

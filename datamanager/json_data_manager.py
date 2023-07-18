import json
import os
from .data_manager_interface import DataManagerInterface
from helpers.api_helpers import MovieAPI

movie_api = MovieAPI


class JSONDataManager(DataManagerInterface):
    def __init__(self, filename):
        self.filename = filename

    def get_all_users(self):
        """ Input: This method takes no arguments
        Output: returns a list of dictionaries representing users """
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)

        with open(file_path, "r") as file:
            users_data = json.load(file)

        return users_data

    def save_new_data(self, users_data):
        """ Input: This method takes no arguments
        Output: returns a list of dictionaries representing users """
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)
        with open(file_path, 'w') as file:
            json.dump(users_data, file, indent=4)

        return users_data

    def get_user_movies(self, user_id):
        """ Input: This method takes one argument: user_id.
         Output: This method returns a list of movies for the given user.
         Each movie should be a dictionary with details about the movie. """
        users_data = self.get_all_users()

        user_info = users_data.get(user_id)
        if user_info is None:
            return {}
        movies = user_info.get("movies", {})

        return movies

    def get_movie_by_id(self, user_id, movie_id):
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            return f"User ID {user_id} does not exist"
        movies = self.get_user_movies(user_id)
        movie_info = movies[str(movie_id)]
        return movie_info

    def add_user(self, user_name):  # should this function be separated to 2 functions? what should it return?
        users_data = self.get_all_users()

        # Find the next free ID for the new user
        existing_ids = [int(user_id) for user_id in users_data.keys()]
        next_id = max(existing_ids) + 1 if existing_ids else 1

        new_user_info = {
            "name": user_name,
            "movies": {}
        }

        # Add the new user to the dictionary
        users_data[str(next_id)] = new_user_info

        self.save_new_data(users_data)

        return users_data

    def add_movie(self, user_id, title):
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            return f"User ID {user_id} does not exist"
        movies = self.get_user_movies(user_id)

        for movie_id, movie_info in movies.items():
            if movie_info.get("name") == title:
                # Movie already exists in the user's movie list
                return "Movie already exists"

        # Fetch movie info from the API
        movie_info = MovieAPI.fetch_movie_info(title)

        if movie_info is None:
            raise RuntimeError("There was a problem fetching movie info")

        # Find the next free ID for the new movie
        existing_ids = [int(movie_id) for movie_id in movies.keys()]
        if existing_ids:
            next_id = max(existing_ids) + 1
        else:
            next_id = 1

        # adding movie to movies
        movies[str(next_id)] = movie_info
        # updating user movies
        users_data[str(user_id)]["movies"] = movies
        self.save_new_data(users_data)

        return users_data

    def update_movie(self, user_id, movie_id, updated_movie_data):
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            return f"User ID {user_id} does not exist"
        movies = self.get_user_movies(user_id)
        movies[movie_id] = updated_movie_data
        users_data[str(user_id)]["movies"] = movies
        self.save_new_data(users_data)

        return users_data

    def delete_movie(self, user_id, movie_id):
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            return f"User ID {user_id} does not exist"
        movies = self.get_user_movies(user_id)
        del movies[movie_id]
        users_data[str(user_id)]["movies"] = movies
        self.save_new_data(users_data)

        return users_data

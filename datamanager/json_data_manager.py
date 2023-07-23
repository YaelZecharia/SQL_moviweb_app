import json
import os
from .data_manager_interface import DataManagerInterface
from helpers.api_helpers import MovieAPI

movie_api = MovieAPI


# Define our custom Exceptions
class UserNotFoundError(Exception):
    pass


class UserAlreadyExists(Exception):
    pass


class MovieAlreadyExists(Exception):
    pass


class ProblemFetchingInfo(Exception):
    pass


class MovieNotFound(Exception):
    pass


# JSONDataManager class inheriting from the DataManagerInterface
class JSONDataManager(DataManagerInterface):

    def __init__(self, filename):
        """Initializes the JSONDataManager with the filename of the data"""
        self.filename = filename

    def get_all_users(self):
        """
        Retrieves all users from the JSON data file.

        Returns:
            users_data (dict): All user data.
        """
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)

        with open(file_path, "r") as file:
            users_data = json.load(file)

        return users_data

    def save_new_data(self, users_data):
        """
        Saves the provided user data to the JSON data file.

        Args:
            users_data (dict): The user data to save.

        Returns:
            users_data (dict): The same user data that was provided.
        """
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)

        with open(file_path, 'w') as file:
            json.dump(users_data, file, indent=4)

        return users_data

    def get_username_by_id(self, user_id):
        """
        Retrieve the username associated with a specific user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            str: The username associated with the user ID.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
        """
        users_data = self.get_all_users()
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        user_info = users_data.get(str(user_id))
        if user_info:
            return user_info.get("name")

    def get_user_movies(self, user_id):
        """
        Retrieve the movies associated with a specific user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: The movies associated with the user ID.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
        """
        users_data = self.get_all_users()
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        user_info = users_data.get(user_id)
        if user_info is None:
            return {}
        movies = user_info.get("movies", {})

        return movies

    def get_movie_by_id(self, user_id, movie_id):
        """
        Retrieve movie info by movie ID for a specific user.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.

        Returns:
            movie_info (dict): Movie details.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieNotFound: If no movie is associated with the movie ID.
        """
        users_data = self.get_all_users()
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        movies = self.get_user_movies(user_id)
        if str(movie_id) not in movies:
            raise UserNotFoundError(f"Movie ID {movie_id} does not exist")
        movie_info = movies[str(movie_id)]
        return movie_info

    def add_user(self, user_name):
        """
        Add a new user.

        Args:
            user_name (str): The name of the new user.

        Returns:
            users_data (dict): All user data after the addition of the new user.

        Raises:
            UserAlreadyExists: If the username already exists.
        """
        users_data = self.get_all_users()

        # Check if the username already exists in users_data
        for user_id, user_info in users_data.items():
            if user_info["name"] == user_name:
                raise UserAlreadyExists("Username already exists. Please choose a different username.")

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
        """
        Add a new movie for a specific user.

        Args:
            user_id (str): The ID of the user.
            title (str): The title of the movie.

        Returns:
            users_data (dict): All user data after the addition of the new movie.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieAlreadyExists: If the movie already exists in the user's movie list.
            ProblemFetchingInfo: If there is a problem fetching movie info from the API.
        """
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        movies = self.get_user_movies(user_id)

        for movie_id, movie_info in movies.items():
            if movie_info.get("name") == title:
                # Movie already exists in the user's movie list
                raise MovieAlreadyExists(f"Movie {title} already exists")

        # Fetch movie info from the API
        movie_info = MovieAPI.fetch_movie_info(title)

        if movie_info is None:
            raise ProblemFetchingInfo("There was a problem fetching movie info")

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
        """
        Update a movie's details for a specific user.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.
            updated_movie_data (dict): The updated movie details.

        Returns:
            users_data (dict): All user data after updating the movie.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
        """
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        movies = self.get_user_movies(user_id)
        movies[movie_id] = updated_movie_data
        users_data[str(user_id)]["movies"] = movies
        self.save_new_data(users_data)

        return users_data

    def delete_movie(self, user_id, movie_id):
        """
        Delete a movie from a specific user's list.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.

        Returns:
            users_data (dict): All user data after deleting the movie.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieNotFound: If the movie is not found in the user's movie list.
        """
        users_data = self.get_all_users()
        # Check if user_id exists in users_data
        if str(user_id) not in users_data:
            raise UserNotFoundError(f"User ID {user_id} does not exist")
        movies = self.get_user_movies(user_id)
        if not movies[movie_id]:
            raise MovieNotFound("This movie does not exist")
        del movies[movie_id]
        users_data[str(user_id)]["movies"] = movies
        self.save_new_data(users_data)

        return users_data

import json
import os
from .data_manager_interface import DataManagerInterface
from helpers.api_helpers import MovieAPI
import bcrypt

movie_api = MovieAPI


# Define our custom Exceptions
class UserNotFoundError(Exception):
    pass


class WrongPassword(Exception):
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

        users_list = [{"id": user_id, "name": data["name"]} for user_id, data in users_data.items()]
        return users_list

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
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)

        with open(file_path, "r") as file:
            users_data = json.load(file)

        user = users_data.get(str(user_id))
        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        return user['name']

    def get_userinfo_by_id(self, user_id):
        """
        Retrieve the userinfo associated with a specific user ID.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: The user info associated with the user ID.
        """
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)
        with open(file_path, 'r') as file:
            users_info = json.load(file)

        user_info = users_info.get(str(user_id))
        return user_info

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
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        file_path = os.path.join(data_dir, self.filename)
        with open(file_path, 'r') as file:
            users_info = json.load(file)

        user = users_info.get(str(user_id))
        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        return user.get('movies', {})

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

    @staticmethod
    def create_user_password(password, confirm_password):
        """
        Checking that password is at least 8 characters and same as confirm_password
         Then hashing the password.
         return the hashed password
        """
        salt = bcrypt.gensalt()
        if password != confirm_password:
            raise TypeError("passwords don't match!")
        if len(password) < 8:
            raise WrongPassword("Password needs to be at least 8 characters")
        password = password.encode("utf-8")
        hashed_password = bcrypt.hashpw(password, salt).decode("utf-8")
        return hashed_password

    def add_user(self, user_name, password, confirm_password):
        """
        Add a new user.

        Args:
            user_name (str): The name of the new user.
            password (str): The users password
            confirm_password (str): Confirmation of password

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

        hashed_pass = self.create_user_password(password, confirm_password)

        new_user_info = {
            "name": user_name,
            "password": hashed_pass,
            "movies": {}
        }

        # Add the new user to the dictionary
        users_data[str(next_id)] = new_user_info

        self.save_new_data(users_data)

        return users_data

    @staticmethod
    def authenticate_user(user_pass, hashed_pass):
        """
        Checks that the password the user entered on the website
        matches the password that is stored in the json file
        """
        if bcrypt.checkpw(user_pass.encode("utf-8"), hashed_pass.encode("utf-8")):
            return
        else:
            raise WrongPassword

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

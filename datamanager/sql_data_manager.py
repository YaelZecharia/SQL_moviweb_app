from flask_sqlalchemy import SQLAlchemy
import os
from .data_manager_interface import DataManagerInterface
from helpers.api_helpers import MovieAPI
from helpers.sql_models import *
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


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app):
        db.init_app(app)

    def get_all_users(self):
        """
        Retrieves all users from the SQL.
        """
        users = db.session.query(User).all()

        # Return the list of User objects
        return users

    def get_all_movies(self):
        """
        Retrieves all movies from the SQL.
        """
        movies = db.session.query(Movie).all()

        # Return the list of Movie objects
        return movies

    def get_username_by_id(self, user_id):
        """
        Retrieve the username associated with a specific user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            str: The username associated with the user ID.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
        """

        # Query the User model by ID
        user = db.session.query(User).filter_by(id=user_id).first()

        # Check if the user was found
        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        return user.name

    def get_userinfo_by_id(self, user_id):
        """
        Retrieve the userinfo associated with a specific user ID.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: The user info associated with the user ID.
        """

        # Query the User model by ID
        user = db.session.query(User).filter_by(id=user_id).first()

        # Check if the user was found
        if not user:
            return None

        # Convert the user object into a dictionary
        user_info = {
            "id": user.id,
            "name": user.name,
            "password": user.password
        }

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

        # Query the User model by ID
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        movies_dict = {}
        for movie in user.favorite_movies:
            user_movie_review = self.get_user_review_for_movie(user_id, movie.id)
            review_text = user_movie_review.review_text if user_movie_review else None
            my_rating = user_movie_review.rating if user_movie_review else None
            movies_dict[movie.id] = {
                "name": movie.title,
                "director": movie.director,
                "year": movie.year,
                "rating": movie.rating,
                "poster": movie.poster,
                "review": review_text,
                "my_rating": my_rating
            }

        return movies_dict

    def get_movie_by_id(self, user_id, movie_id):
        """
        Retrieve movie info by movie ID for a specific user.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie.

        Returns:
            movie_info (dict): Movie details.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieNotFound: If no movie is associated with the movie ID.
        """

        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        matching_movie = None
        for movie in user.favorite_movies:
            if movie.id == int(movie_id):
                matching_movie = movie
                break

        if not matching_movie:
            raise MovieNotFound(f"Movie ID {movie_id} does not exist for user {user_id}")

        user_movie_review = self.get_user_review_for_movie(user_id, movie_id)
        review_text = user_movie_review.review_text if user_movie_review else None
        my_rating = user_movie_review.rating if user_movie_review else None

        # Extract movie details into a dictionary
        movie_info = {
            "id": movie.id,
            "name": movie.title,
            "director": movie.director,
            "year": movie.year,
            "rating": movie.rating,
            "poster": movie.poster,
            "review": review_text,
            "my_rating": my_rating
        }

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
        for user in users_data:
            if user.name == user_name:
                raise UserAlreadyExists("Username already exists. Please choose a different username.")

        hashed_pass = self.create_user_password(password, confirm_password)

        new_user_info = User(name=user_name, password=hashed_pass)
        db.session.add(new_user_info)
        db.session.commit()

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

    def get_user_review_for_movie(self, user_id, movie_id):
        return Review.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    def add_movie(self, user_id, title):
        """
        Add a new movie for a specific user.

        Args:
            user_id (str): The ID of the user.
            title (str): The title of the movie.

        Returns:
            None.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieAlreadyExists: If the movie already exists in the user's movie list.
            ProblemFetchingInfo: If there is a problem fetching movie info from the API.
        """

        # Query the User model by ID
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        # Check if the movie already exists in the Movie table
        existing_movie = db.session.query(Movie).filter_by(title=title).first()

        if existing_movie:
            # If the movie already exists, just link it to the user (if not already linked)
            if existing_movie not in user.favorite_movies:
                user.favorite_movies.append(existing_movie)
                db.session.commit()
            return

        # If the movie does not exist, fetch its info from the API and add it
        movie_info_from_api = MovieAPI.fetch_movie_info(title)

        if movie_info_from_api is None:
            raise ProblemFetchingInfo("There was a problem fetching movie info")

        # Create a new movie object
        new_movie = Movie(
            title=title,
            director=movie_info_from_api.get("director", ""),
            year=movie_info_from_api.get("year"),
            rating=movie_info_from_api.get("rating"),
            poster=movie_info_from_api.get("poster", ""),
        )

        # Add movie to the session and commit
        db.session.add(new_movie)
        db.session.commit()

        # Associate the movie with the user as a favorite
        user.favorite_movies.append(new_movie)
        db.session.commit()

    def add_review(self, user_id, movie_id, review_text, rating):
        # Query for the specific user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        # Query for the specific movie linked to that user
        movie = db.session.query(Movie).filter_by(id=movie_id).first()
        if not movie or movie not in user.favorite_movies:
            raise MovieNotFound(f"Movie ID {movie_id} does not exist for User ID {user_id}")

        # Check if the review already exists
        existing_review = db.session.query(Review).filter_by(user_id=user_id, movie_id=movie_id).first()

        if existing_review:
            # Update the existing review
            existing_review.review_text = review_text
            existing_review.rating = rating
        else:
            # Create a new review object
            new_review = Review(
                user_id=user_id,
                movie_id=movie_id,
                review_text=review_text,
                rating=rating
            )

            # Add review to the session
            db.session.add(new_review)

            # Associate the movie with the user as a favorite
            user.reviews.append(new_review)
            movie.reviews.append(new_review)

        # Commit the changes
        db.session.commit()

    def update_movie(self, user_id, movie_id, updated_movie_data):
        """
        Update a movie's details for a specific user.

        Args:
            user_id (int): The ID of the user.
            movie_id (int): The ID of the movie.
            updated_movie_data (dict): The updated movie details.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieNotFound: If the movie is not associated with the user.
        """

        # Query for the specific user
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        # Query for the specific movie linked to that user
        movie = db.session.query(Movie).filter_by(id=movie_id).first()
        if not movie or movie not in user.favorite_movies:
            raise MovieNotFound(f"Movie ID {movie_id} does not exist for User ID {user_id}")

        # Update the movie attributes
        movie.title = updated_movie_data.get('name', movie.title)
        movie.year = updated_movie_data.get('year', movie.year)
        movie.rating = updated_movie_data.get('rating', movie.rating)
        movie.director = updated_movie_data.get('director', movie.director)
        movie.poster = updated_movie_data.get('poster', movie.poster)

        # Commit the changes to the database
        db.session.commit()

    def delete_movie(self, user_id, movie_id):
        """
        Delete a movie from a specific user's list.

        Args:
            user_id (str): The ID of the user.
            movie_id (str): The ID of the movie.

        Raises:
            UserNotFoundError: If no user is associated with the user ID.
            MovieNotFound: If the movie is not found in the user's movie list.
        """

        # Query the User model by ID
        # user = self.db.User.filter_by(id=user_id).first()
        user = db.session.query(User).filter_by(id=user_id).first()

        if not user:
            raise UserNotFoundError(f"User ID {user_id} does not exist")

        movie = db.session.query(Movie).filter_by(id=movie_id).first()

        if not movie or movie not in user.favorite_movies:
            raise MovieNotFound(f"Movie ID {movie_id} does not exist for user {user_id}")

        # Delete movie from user's favorite movies
        user.favorite_movies.remove(movie)
        db.session.commit()

    def get_movie_reviews(self, movie_id):
        """
        Retrieve all reviews for a specific movie.

        Args:
            movie_id (int): The ID of the movie.

        Returns:
            list[dict]: A list of dictionaries, each representing a review for the movie.
        """

        # Query the Movie model by ID
        movie = db.session.query(Movie).filter_by(id=movie_id).first()

        # Ensure the movie exists
        if not movie:
            raise MovieNotFound(f"Movie ID {movie_id} does not exist")

        # Fetch all reviews associated with this movie
        reviews_for_movie = movie.reviews

        # Convert each review object to a dictionary for easier use in the template
        reviews_list = []
        for review in reviews_for_movie:
            user = db.session.query(User).filter_by(id=review.user_id).first()
            reviews_list.append({
                'user_name': user.name,
                'rating': review.rating,
                'review_text': review.review_text
            })

        return reviews_list

from abc import ABC, abstractmethod


class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        """ Input: This method takes no arguments
         Output: returns a list of dictionaries representing users"""
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        """ Input: This method takes one argument: user_id.
        Output: This method returns a list of movies for the given user.
        Each movie should be a dictionary with details about the movie. """
        pass

    @abstractmethod
    def add_user(self, user_name, password, confirm_password):
        # Input: This method takes one argument: user_name.
        pass

    @abstractmethod
    def add_movie(self, user_id, title):
        pass

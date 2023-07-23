import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from the .env file

API_KEY = os.getenv("API_KEY")
REQUEST_URL = os.getenv("REQUEST_URL")


class MovieAPI:
    @staticmethod
    def fetch_movie_info(title):
        """ this function takes a title of a movie and fetches its info from the API.
        it returns a dictionary with the info of the movie. """
        try:
            params = {
                "t": title,
                "apikey": API_KEY
            }
            response = requests.get(REQUEST_URL, params=params)

            if response.status_code == 200:
                movie_data = response.json()
                if movie_data["Response"] == "False":
                    return None
                movie_title = movie_data["Title"]
                year = movie_data["Year"]
                rating = movie_data["imdbRating"]
                director = movie_data["Director"]
                poster = movie_data["Poster"]

                new_movie = {
                    "name": movie_title,
                    "director": director,
                    "year": year,
                    "rating": rating,
                    "poster": poster
                }
                return new_movie
            else:
                return None
        except requests.exceptions.RequestException:
            return None

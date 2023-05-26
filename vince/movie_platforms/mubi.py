import requests
import time
import string

from bs4 import BeautifulSoup

from .movie_platform import MoviePlatform

class MubiMoviePlatform(MoviePlatform):
    MAX_RETRIES = 2

    def __init__(self):
        super().__init__()

    def search_movie(self, movie):
        movie_url_name = "".join([x.lower() for x in movie.name if x in string.ascii_letters + "0123456789 "])
        movie_url_name = "-".join(movie_url_name.split(" "))
        request_url = f"https://api.mubi.com/v3/films/{movie_url_name}/film_groups"
        response = requests.get(request_url, headers={"Client-Country": "IL", "Client": "web", "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36"})

        if "404" in response.text:
            return None

        if len(response.json()["film_groups"]) == 0:
            return None
        
        return f"https://mubi.com/films/{movie_url_name}"

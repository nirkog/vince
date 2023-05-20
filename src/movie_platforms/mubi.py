import requests
import time

from .movie_platform import MoviePlatform

class MubiMoviePlatform(MoviePlatform):
    def __init__(self):
        super().__init__()

    def search_movie(self, movie):
        while True:
            request_url = f"https://api.mubi.com/v3/search/films?query={movie.name}&playable=true"
            response = requests.get(request_url, headers={"Client-Country": "IL", "Client": "web", "User-Agent": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Chrome/W.X.Y.Z Safari/537.36"})
            if "Retry" in response.text:
                time.sleep(2)
                continue
            break
        films = response.json()["films"]

        if len(films) > 10:
            return None

        for film in films:
            if abs(int(film["year"]) - int(movie.year)) < 2:
                return film["web_url"]

        return None

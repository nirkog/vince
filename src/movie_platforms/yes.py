import requests

from .movie_platform import MoviePlatform

class YesMoviePlatform(MoviePlatform):
    def __init__(self):
        super().__init__()

    def search_movie(self, movie):
        request_url = f"https://www.yes.co.il/result?q={movie.name}"
        response = requests.get(request_url).text

        if not "/content/movies" in response:
            return None

        start = response.index("/content/movies")
        end = response.index('"', start)

        return "https://www.yes.co.il" + response[start:end]

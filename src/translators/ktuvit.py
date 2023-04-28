import requests
import json
import re

from .translator import Translator
from .translator import TranslationException

class KtuvitTranslator(Translator):
    def __init__(self):
        super().__init__()

    def translate_movie_name(self, movie):
        request_url = "https://www.ktuvit.me/Services/ContentProvider.svc/GetSearchForecast"
        response = requests.post(request_url, json={"request":{"SearchString":movie.name,"SearchType":"Film"}})
        response = json.loads(response.json()["d"])
        possible_movies = response["Items"]
        possible_movies = [m for m in possible_movies if str(movie.year) in m["HebName"]]

        if len(possible_movies) > 1:
            raise TranslationException("Ambigious name")

        if len(possible_movies) == 0:
            raise TranslationException("Movie not found")

        translation = possible_movies[0]["HebName"]
        translation = re.split("\(\d{4}\)", translation)[0]

        return translation

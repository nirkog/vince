import csv
import requests
import math
from threading import Thread
from bs4 import BeautifulSoup

from translators.translator import TranslationException
from .watchlist import Watchlist
from movie import Movie

class LetterboxdCsvWatchlist(Watchlist):
    def __init__(self, args):
        super().__init__(args)

        self.filename = args.letterboxd_csv_filename

    def load(self):
        with open(self.filename, newline='') as f:
            # self.raw_data = f.read()
            reader = csv.reader(f, delimiter=',', quotechar='"')
        
            self._movies = []
            for row in list(reader)[1:]:
                try:
                    movie_name = row[1]
                    movie_date = int(row[2])
                    self._movies.append(Movie(movie_name, movie_date))
                except IndexError:
                    pass

    @property
    def movies(self):
        return self._movies

class LetterboxdWatchlist(Watchlist):
    def __init__(self, args):
        super().__init__(args)

        self.username = args.letterboxd_username

    def _get_movie_from_link(self, link):
        request_url = f"https://letterboxd.com{link}"
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "html.parser")
        header = soup.find(id="featured-film-header")
        name = header.h1.text
        date = header.p.small.a.text
        self._movies.append(Movie(name, date))

    def _get_movies_from_page(self, page_number):
        request_url = f"https://letterboxd.com/{self.username}/watchlist/page/{page_number + 1}"
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "html.parser")
        posters = soup.find_all("div", "poster")
        film_links = [poster["data-target-link"] for poster in posters]

        threads = []
        for link in film_links:
            threads.append(Thread(target=LetterboxdWatchlist._get_movie_from_link, args=(self, link)))
            threads[-1].start()
        for thread in threads:
            thread.join()

    def load(self):
        request_url = f"https://letterboxd.com/{self.username}/watchlist/"
        response = requests.get(request_url)
        soup = BeautifulSoup(response.text, "html.parser")
        film_count = int(soup.find_all("div", "js-watchlist-content")[0]["data-num-entries"])
        page_count = math.ceil(film_count / 28)
        self._movies = []

        for i in range(page_count):
            self._get_movies_from_page(i)
    
        self._movies = sorted(self._movies, key=lambda movie: movie.name)
    
    @property
    def movies(self):
        return self._movies

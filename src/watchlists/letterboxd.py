import csv

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

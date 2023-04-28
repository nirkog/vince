from abc import ABC, abstractmethod
from threading import Thread

class SearchThread(Thread):
    def __init__(self, platform, movie):
        super().__init__()

        self.platform = platform
        self.movie = movie

    def run(self):
        self.result = self.platform.search_movie(self.movie)

    def join(self):
        super().join()

        return self.result

class MoviePlatform(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def search_movie(self, movie):
        pass

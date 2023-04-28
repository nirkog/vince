from abc import ABC, abstractmethod
from threading import Thread

class TranslationException(Exception):
    pass

class TranslateThread(Thread):
    def __init__(self, translator, movie):
        super().__init__()

        self.translator = translator
        self.movie = movie

    def run(self):
        self.result = None

        try:
            self.result = self.translator.translate_movie_name(self.movie)
        except TranslationException:
            pass

    def join(self):
        super().join()

        return self.result

class Translator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def translate_movie_name(self, original_movie_name):
        pass

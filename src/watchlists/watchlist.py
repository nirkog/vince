from abc import ABC, abstractmethod

class Watchlist(ABC):
    def __init__(self, args):
        pass

    @abstractmethod
    def load(self):
        pass

    @property
    @abstractmethod
    def movies(self):
        pass


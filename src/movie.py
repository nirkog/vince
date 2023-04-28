from dataclasses import dataclass

@dataclass
class Movie:
    name: str
    year: int
    translations: dict = None
    available_platforms: dict = None

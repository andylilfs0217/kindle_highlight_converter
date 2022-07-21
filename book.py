from typing import List


class Highlight:
    def __init__(self, content: str = '', time: int = 0, location: int = 0) -> None:
        self.time = time
        self.location = location
        self.content = content


class Bookmark:
    def __init__(self, location: int = 0, time: int = 0) -> None:
        self.time = time
        self.location = location


class Note:
    def __init__(self, content: str = '', time: int = 0,  location: int = 0) -> None:
        self.location = location
        self.time = time
        self.content = content


class Book:
    def __init__(self,
                 title: str = '',
                 highlights: List[Highlight] = list(),
                 bookmarks: List[Bookmark] = list(),
                 notes: List[Note] = list()) -> None:
        self.title = title
        self.highlights = highlights
        self.bookmarks = bookmarks
        self.notes = notes

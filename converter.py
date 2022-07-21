import csv
from datetime import datetime
from enum import Enum
import re
import string
from typing import List
from book import Book, Bookmark, Highlight, Note


class HighlightPosition(Enum):
    TITLE = 1
    INFO = 2
    CONTENT = 3


class HighlightType(Enum):
    NONE = 0
    HIGHLIGHT = 1
    BOOKMARK = 2
    NOTE = 3


class Converter():
    def __init__(self, books: List[Book] = []) -> None:
        self.fileName = 'My Clippings.txt'
        self.books = books

    def getHighlights(self) -> None:
        with open(self.fileName) as f:
            lines = f.readlines()
        position = HighlightPosition.TITLE
        book_map = {}
        book = Book()
        type = HighlightType.NONE
        contents = []
        location = 0
        timestamp = 0
        for line in lines:
            line = line.replace('\ufeff', '')
            line = line.replace('\n', '')
            if line == '':
                continue
            elif line == '==========':
                content = ' '.join(contents)
                if type == HighlightType.HIGHLIGHT:
                    highlight = Highlight(
                        content, timestamp, location)
                    book.highlights.append(highlight)
                elif type == HighlightType.BOOKMARK:
                    bookmark = Bookmark(location, timestamp)
                    book.bookmarks.append(bookmark)
                elif type == HighlightType.NOTE:
                    note = Note(content, timestamp, location)
                    book.notes.append(note)
                book_map[book.title] = book
                position = HighlightPosition.TITLE
            elif position == HighlightPosition.TITLE:
                contents = []
                book = book_map.get(line, Book(
                    highlights=[], bookmarks=[], notes=[]))
                book.title = line
                position = HighlightPosition.INFO
            elif position == HighlightPosition.INFO:
                match = re.search('on Location (\d+)', line)
                location = int(match.group(1))
                time_string = line.partition('Added on ')[2]
                time = datetime.strptime(
                    time_string, '%A, %B %d, %Y %I:%M:%S %p')
                timestamp = int(time.timestamp())
                if line.startswith('- Your Highlight'):
                    type = HighlightType.HIGHLIGHT
                elif line.startswith('- Your Note'):
                    type = HighlightType.NOTE
                elif line.startswith('- Your Bookmark'):
                    type = HighlightType.BOOKMARK
                position = HighlightPosition.CONTENT
            elif position == HighlightPosition.CONTENT:
                contents.append(line)
        for book in book_map.values():
            self.books.append(book)

    def outputHighlight(self) -> None:
        for book in self.books:
            with open(f'output/{book.title}.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['Content', 'Type', 'Location', 'Time'])
                for highlight in book.highlights:
                    writer.writerow(
                        [highlight.content, 'Highlight', highlight.location, highlight.time])
                for note in book.notes:
                    writer.writerow(
                        [note.content, 'Note', note.location, note.time, ])
                for bookmark in book.bookmarks:
                    writer.writerow(
                        ['', 'Bookmark', bookmark.location,  bookmark.time])

            with open(f'output/{book.title}.txt', 'w') as f:
                for highlight in book.highlights:
                    f.write(f'- {highlight.content}\n')
                for note in book.notes:
                    f.write(f'- {note.content}\n')

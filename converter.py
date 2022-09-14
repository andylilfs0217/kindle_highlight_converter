import csv
from datetime import datetime
from enum import Enum
import glob
import re
from typing import List
from book import Book, Bookmark, Highlight, Note
from io_converter import HighlightInput
from bs4 import BeautifulSoup


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
    INPUT_DIR = 'input'

    def __init__(self, books: List[Book] = []) -> None:
        self.books = books

    def getHighlights(self, highlight_input: HighlightInput):
        """
        Get highlights by input.
        """
        input_source_folder = str(highlight_input).split('.')[1]
        match highlight_input:
            case HighlightInput.none:
                pass
            case HighlightInput.clippings:
                self.getHighlightFromClippings(input_source_folder)
            case HighlightInput.html:
                self.getHighlightFromHTML(input_source_folder)

    def getHighlightFromHTML(self, input_folder: str) -> None:
        """
        Read all highlights in `html` folder and convert to [books].
        """
        directory = f"{self.INPUT_DIR}/{input_folder}"

        # For each file in the input source folder
        for filename in glob.iglob(f'{directory}/*'):
            with open(filename) as fp:
                # Parse the HTML file to BeautifulSoup structure
                soup = BeautifulSoup(fp, 'html.parser')

                # HTML Tags
                BOOK_TITLE = 'bookTitle'
                BOOK_AUTHORS = 'authors'
                HIGHLIGHT_INFO = 'noteHeading'
                HIGHLIGHT_CONTENT = 'noteText'

                # Read the title
                book_title = soup.find(class_=BOOK_TITLE).string.strip()
                # Read the authors
                book_authors = soup.find(class_=BOOK_AUTHORS).string.strip()
                # Create a book object
                book = Book(f"{book_title} ({book_authors})")
                # TODO: For each highlight html tag, parse it to Highlight object and append to list
                highlight_infos = [info.text.strip()
                                   for info in soup.find_all(class_=HIGHLIGHT_INFO)]
                highlights = [highlight.text.strip()
                              for highlight in soup.find_all(class_=HIGHLIGHT_CONTENT)]
                for i in range(len(highlight_infos)):
                    info, highlight = highlight_infos[i], highlights[i]
                    time = 0
                    location = 0
                    highlight_obj = Highlight(highlight, time, location)
                    book.highlights.append(highlight_obj)
                # TODO: For each note html tag, parse it to Note object and append to list
                # TODO: For each bookmark html tag, parse it to Bookmark object and append to list
                pass
        pass

    def getHighlightFromClippings(self, input_folder: str) -> None:
        """
        Read all highlights from `My Clippings.txt` and convert to [books]
        """
        file_name = 'My Clippings.txt'

        directory = f"{self.INPUT_DIR}/{input_folder}/{file_name}"

        with open(directory) as f:
            lines = f.readlines()
        position = HighlightPosition.TITLE
        book_map = {}
        book = Book()
        type = HighlightType.NONE
        contents = []
        location = 0
        timestamp = 0
        for line in lines:
            # Replace invisible characters
            line = line.replace('\ufeff', '')
            line = line.replace('\n', '')
            if line == '':
                continue
            elif line == '==========':
                # Start of highlights
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
                # Get the title of the highlight
                contents = []
                book = book_map.get(line, Book(
                    highlights=[], bookmarks=[], notes=[]))
                book.title = line
                position = HighlightPosition.INFO
            elif position == HighlightPosition.INFO:
                # Get the info of the highlight
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
                # Get the content of the highlight
                contents.append(line)
        for book in book_map.values():
            # Save the highlights of each book
            self.books.append(book)

    def outputHighlight(self) -> None:
        """
        Output all highlights in [books] to output folder.
        """
        OUTPUT_DIR = 'output'

        for book in self.books:
            # Output the book highlights as a csv file
            with open(f'{OUTPUT_DIR}/{book.title}.csv', 'w') as f:
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

            # Output the book highlights as a txt file
            with open(f'{OUTPUT_DIR}/{book.title}.txt', 'w') as f:
                f.write('# Book highlights\n')
                f.write('## Highlights\n')
                for highlight in book.highlights:
                    f.write(f'- {highlight.content} ({highlight.location})\n')
                f.write('## Notes\n')
                for note in book.notes:
                    f.write(f'- {note.content} ({note.location})\n')
                f.write('## Bookmarks\n')
                for bookmark in book.bookmarks:
                    f.write(f'- Bookmark ({bookmark.location})\n')

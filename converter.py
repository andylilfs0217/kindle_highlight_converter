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
    # Clippings
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
        if highlight_input == HighlightInput.all or \
                highlight_input == HighlightInput.clippings:
            self.getHighlightFromClippings()
        if highlight_input == HighlightInput.all or \
                highlight_input == HighlightInput.kindle_html:
            self.getHighlightFromKindleHTML()
        if highlight_input == HighlightInput.all or \
                highlight_input == HighlightInput.apple_book:
            self.getHighlightFromAppleBook()

    def getHighlightFromAppleBook(self):
        """
        Read all highlights from Apple Book note export.
        """
        input_folder = 'apple_book'
        directory = f"{self.INPUT_DIR}/{input_folder}"

        # For each file in the input source folder
        for filename in glob.iglob(f'{directory}/*'):
            with open(filename) as fp:
                file = filename.split('/')[-1]
                file = file.split('.')[0]
                # Get book title
                book_title = file.split('-')[0]
                # Get book author
                book_authors = file.split('-')[1]
                # Create book object
                book = Book(f"{book_title} {book_authors}")
                # Read all lines
                lines = fp.readlines()
                # Get book highlights
                i = 0
                while i < len(lines):
                    line = lines[i]
                    # Replace invisible characters
                    line = line.replace('\ufeff', '')
                    line = line.replace('\n', '')
                    # Parse the date
                    time = int(datetime.strptime(
                        line, "%d %B %Y").timestamp())
                    # Skip to the content
                    i += 3
                    content_list = []
                    # Get all contents
                    end_of_content = False
                    while not end_of_content:
                        line = lines[i]
                        # Replace invisible characters
                        line = line.replace('\ufeff', '')
                        line = line.replace('\n', '')
                        line = line.replace('\u3000', '')
                        if line != 'Excerpt from:':
                            content_list.append(line)
                        else:
                            # Reach the end of content
                            end_of_content = True
                        i += 1
                    # Remove start quote and end quote
                    content_list = content_list[:-1]
                    content_list[0] = content_list[0][1:]
                    content_list[-1] = content_list[0][:-1]
                    # Combine the highlights
                    content = ''.join(content_list)
                    highlight = Highlight(content, time)
                    # Add the highlight to the book
                    book.highlights.append(highlight)
                    i += 3
                # TODO: Get book bookmarks
                # TODO: Get book notes
            # Save the book to the self object
            self.books.append(book)

    def getHighlightFromKindleHTML(self) -> None:
        """
        Read all highlights in `html` folder and convert to [books].
        """
        input_folder = 'kindle_html'
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
                HIGHLIGHT_TAG = re.compile('highlight_*')

                # Read the title
                book_title = soup.find(class_=BOOK_TITLE).string.strip()
                # Read the authors
                book_authors = soup.find(class_=BOOK_AUTHORS).string.strip()
                # Create a book object
                book = Book(f"{book_title} ({book_authors})")
                # For each highlight html tag, parse it to Highlight object and append to list
                highlight_infos = [info.text.strip()
                                   for info in soup.find_all(class_=HIGHLIGHT_INFO)]
                highlights = [highlight.text.strip()
                              for highlight in soup.find_all(class_=HIGHLIGHT_CONTENT)]
                highlight_tags = [highlight.text.strip()
                                  for highlight in soup.find_all(class_=HIGHLIGHT_TAG)]
                for i in range(len(highlight_infos)):
                    info, highlight, tag = highlight_infos[i], highlights[i], highlight_tags[i]
                    time = 0  # No time set, default 0
                    # Get highlight location
                    location_index = info.index('Location')
                    location = int(info[location_index+len('Location '):])
                    # Create highlight object
                    highlight_obj = Highlight(highlight, time, location, tag)
                    book.highlights.append(highlight_obj)
                # TODO: For each note html tag, parse it to Note object and append to list
                # TODO: For each bookmark html tag, parse it to Bookmark object and append to list
                self.books.append(book)
        pass

    def getHighlightFromClippings(self) -> None:
        """
        Read all highlights from `My Clippings.txt` and convert to [books]
        """
        input_folder = 'clippings'
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

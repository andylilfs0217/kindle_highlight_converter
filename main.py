from converter import Converter
from io_converter import HighlightInput, IOConverter


def main():
    converter = Converter()
    io_converter = IOConverter()

    # highlight_input = io_converter.askHighlightInput()
    highlight_input = HighlightInput.html  # For debug only

    converter.getHighlights(highlight_input)

    converter.outputHighlight()


if __name__ == "__main__":
    main()

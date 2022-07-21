import locale
from converter import Converter


def main():
    converter = Converter()
    converter.getHighlights()
    converter.outputHighlight()


if __name__ == "__main__":
    main()

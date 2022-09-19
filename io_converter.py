from enum import Enum


class HighlightInput(Enum):
    none = 0
    clippings = 1
    kindle_html = 2
    apple_book = 3
    all = 9


class IOConverter():
    def __init__(self) -> None:
        pass

    def askHighlightInput(self) -> HighlightInput:
        """
        Ask users for the highlight input source.
        """
        print("Please select your input source.")
        for i, inp in enumerate(HighlightInput):
            print(f"{i} = {str(inp).split('.')[1]}")
        highlight_input = int(input("Select: "))
        if highlight_input is not HighlightInput:
            highlight_input = 0
            print(
                f"Invalid input. Setting the source as {str(HighlightInput(highlight_input)).split('.')[1]}")
        highlight_input = HighlightInput(highlight_input)
        return highlight_input

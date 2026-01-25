from .board import Board
from .piece import Piece


class TermDisplay:
    PIECE_SYMBOLS = {
        "K": ("♚", "♔"),
        "Q": ("♛", "♕"),
        "R": ("♜", "♖"),
        "B": ("♝", "♗"),
        "N": ("♞", "♘"),
        "P": ("♟", "♙"),
    }

    def __init__(self, use_ascii: bool = True) -> None:
        self.use_ascii = use_ascii

    def get_symbol(self, piece: Piece) -> str:
        if self.use_ascii:
            symbol = piece.notation
            return symbol.lower() if piece.color else symbol
        else:
            return self.PIECE_SYMBOLS[piece.notation][piece.color]

    def show_board(self, board: Board, highlight: list[int] | None = None) -> None:
        if highlight is None:
            highlight = []

        highlight_set = set(highlight)

        LIGHT_BG = "\033[48;5;215m"
        DARK_BG = "\033[48;5;94m"
        HIGHLIGHT_BG = "\033[48;5;34m"
        BLACK_PIECE = "\033[38;5;16m"
        WHITE_PIECE = "\033[38;5;231m"
        RESET = "\033[0m"
        BOLD = "\033[1m"

        print("\n  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for rank in range(7, -1, -1):
            row = f"{rank + 1} ║"

            for file in range(8):
                loc = (file << 3) | rank
                piece = board.board[loc]

                is_light_square = (file + rank) % 2 == 0
                is_highlighted = loc in highlight_set

                if is_highlighted:
                    bg = HIGHLIGHT_BG
                    if piece is None:
                        symbol = "●"
                        color = "\033[38;5;22m"
                    else:
                        symbol = self.get_symbol(piece)
                        color = BLACK_PIECE if not piece.color else WHITE_PIECE
                else:
                    bg = LIGHT_BG if is_light_square else DARK_BG
                    if piece is None:
                        symbol = " "
                        color = ""
                    else:
                        symbol = self.get_symbol(piece)
                        color = BLACK_PIECE if piece.color else WHITE_PIECE

                row += f"{bg}{BOLD} {color}{symbol} {RESET}"

                if file < 7:
                    row += "│"

            row += "║"
            print(row)

            if rank > 0:
                print("  ╟───┼───┼───┼───┼───┼───┼───┼───╢")

        print("  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        print("    a   b   c   d   e   f   g   h\n")

from src.board import Board
from src.piece import Color, Piece

LIGHT_BG = "\033[48;5;215m"
DARK_BG = "\033[48;5;94m"
HIGHLIGHT_BG = "\033[48;5;34m"
HIGHLIGHT_DOT = "\033[38;5;22m"
BLACK_PIECE = "\033[38;5;16m"
WHITE_PIECE = "\033[38;5;231m"
ERROR_MSG = "\033[38;5;196m"
SUCCESS_MSG = "\033[38;5;82m"
RESET = "\033[0m"
BOLD = "\033[1m"

PIECE_SYMBOLS = {
    "K": ("♚", "♔"),
    "Q": ("♛", "♕"),
    "R": ("♜", "♖"),
    "B": ("♝", "♗"),
    "N": ("♞", "♘"),
    "P": ("♟", "♙"),
}


class TermDisplay:
    def __init__(self, use_ascii: bool = True) -> None:
        self.use_ascii = use_ascii

    def get_symbol(self, piece: Piece) -> str:
        if self.use_ascii:
            symbol = piece.notation
            return symbol.lower() if piece.color else symbol
        else:
            return PIECE_SYMBOLS[piece.notation][piece.color]

    def get_input(self, query: str) -> str:
        return input(query).strip()

    def show_err(self, message: str) -> None:
        print(f"{ERROR_MSG}{message}{RESET}")

    def show_end_result(self, message: str) -> None:
        print(f"{SUCCESS_MSG}{message}{RESET}")

    def show_board(
        self,
        board: Board,
        side: Color = Color.WHITE,
        highlight: list[int] | None = None,
    ) -> None:
        if highlight is None:
            highlight = []

        highlight_set = set(highlight)

        print("\n  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗")

        for r in range(7, -1, -1):
            rank = 7 - r if side == Color.BLACK else r
            row = f"{rank + 1} ║"

            for f in range(8):
                file = 7 - f if side == Color.BLACK else f
                loc = (file << 3) | rank
                piece = board.board[loc]

                is_light_square = (file + rank) % 2 == 0
                is_highlighted = loc in highlight_set

                if is_highlighted:
                    bg = HIGHLIGHT_BG
                    if piece is None:
                        symbol = "●"
                        color = HIGHLIGHT_DOT
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

                if f < 7:
                    row += "│"

            row += "║"
            print(row)

            if r > 0:
                print("  ╟───┼───┼───┼───┼───┼───┼───┼───╢")

        print("  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
        file_names = "abcdefgh"
        if side == Color.BLACK:
            file_names = file_names[::-1]
        print("   ", "   ".join(file_names))
        print()

from .board import Board


PIECE_SYMBOLS = {
    "K": ("♚", "♔"),  # King (black, white)
    "Q": ("♛", "♕"),  # Queen
    "R": ("♜", "♖"),  # Rook
    "B": ("♝", "♗"),  # Bishop
    "N": ("♞", "♘"),  # Knight
    "P": ("♟", "♙"),  # Pawn
}

USE_ASCII = True


def display_board(board: Board, highlight: list[int] | None = None) -> None:
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

    for rank in range(8):
        row = f"{8 - rank} ║"

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
                    if USE_ASCII:
                        symbol = (
                            piece.notation.lower() if piece.color else piece.notation
                        )
                    else:
                        symbol = PIECE_SYMBOLS[piece.notation][piece.color]
                    color = BLACK_PIECE if not piece.color else WHITE_PIECE
            else:
                bg = LIGHT_BG if is_light_square else DARK_BG
                if piece is None:
                    symbol = " "
                    color = ""
                else:
                    if USE_ASCII:
                        symbol = (
                            piece.notation.lower() if piece.color else piece.notation
                        )
                    else:
                        symbol = PIECE_SYMBOLS[piece.notation][piece.color]
                    color = BLACK_PIECE if piece.color else WHITE_PIECE

            row += f"{bg}{BOLD} {color}{symbol} {RESET}"

            if file < 7:
                row += "│"

        row += "║"
        print(row)

        if rank < 7:
            print("  ╟───┼───┼───┼───┼───┼───┼───┼───╢")

    print("  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝")
    print("    a   b   c   d   e   f   g   h\n")

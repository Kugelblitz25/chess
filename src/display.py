from .board import Board


def display_board(board: Board) -> None:
    for rank in range(8):
        row = f"{8 - rank} "
        for file in range(8):
            loc = (file << 3) | rank
            piece = board.board[loc]
            if piece is None:
                row += ". "
            else:
                row += piece.symbol[piece.color] + " "
        print(row)
    print("  a b c d e f g h")

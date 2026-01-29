from typing import Optional
from .board import Board
from .display import UI
from .piece import Color, Piece


class Game:
    def __init__(self, board: Board, display: UI, turn: Color = Color.WHITE) -> None:
        self.board = board
        self.display = display
        self.turn = turn

    @property
    def is_end(self) -> bool:
        return self.board.nmoves(self.turn) == 0

    def notation_to_loc(self, notation: str) -> int:
        file = ord(notation[0].lower()) - ord("a")
        rank = int(notation[1])
        return (file << 3) | (rank - 1)

    def index_to_notation(self, loc: int) -> str:
        file, rank = loc >> 3, loc & 7
        return f"{chr(file + ord('a'))}{rank + 1}"

    def get_file_and_rank(self) -> int:
        while True:
            loc = self.display.get_input("Enter position (e.g., e2): ").lower()
            if len(loc) == 2 and loc[0] in "abcdefgh" and loc[1] in "12345678":
                return self.notation_to_loc(loc)
            elif loc == "exit":
                return -1
            self.display.show_err(
                "Invalid input. Please enter a valid position like 'e2'."
            )

    def list_moves(self, loc: int) -> list[int]:
        piece = self.board.get_piece(loc)

        if piece is None:
            return []

        if piece.color != self.turn:
            self.display.show_err("It's not this piece's turn to move.")
            return []

        moves = self.board.list_moves(piece)
        if len(moves) == 0:
            return []

        return moves

    def get_board(self) -> Board:
        return self.board

    def get_turn(self) -> Color:
        return self.turn

    def run(self) -> None:
        self.display.show_board(self.board, self.turn)
        moves: list[int] = []
        cur_selected: Optional[Piece] = None

        while True:
            if self.is_end:
                self.display.show_success("Game over!")
                if self.board.is_in_check(self.board.get_king(self.turn)):
                    self.display.show_success("Checkmate!")
                    self.display.show_success(
                        f"{'White' if self.turn else 'Black'} wins!"
                    )
                else:
                    self.display.show_success("Stalemate!")
                    self.display.show_success("It's a draw!")
                break

            loc = self.get_file_and_rank()
            if loc < 0:
                break

            if len(moves) == 0:
                moves = self.list_moves(loc)
                if len(moves) > 0:
                    cur_selected = self.board.get_piece(loc)
                    assert cur_selected is not None
            else:
                if loc in moves:
                    assert cur_selected is not None
                    self.board.move_piece(cur_selected, loc)
                    self.turn = self.turn.switch()
                cur_selected = None
                moves = []

            self.display.show_board(self.board, self.turn, moves)

from typing import Optional

from .board import Board
from .display import UI
from .engine import Engine
from .piece import Color, Piece
from .square import Square


class Game:
    def __init__(self, board: Engine, display: UI, turn: Color = Color.WHITE) -> None:
        self.engine = board
        self.display = display
        self.turn = turn
        self.turn_init = turn

    def restart(self) -> None:
        self.engine.reset()
        self.turn = self.turn_init

    @property
    def is_end(self) -> bool:
        return self.engine.nmoves(self.turn) == 0

    def notation_to_loc(self, notation: str) -> Square:
        return Square.from_notation(notation)

    def index_to_notation(self, loc: Square) -> str:
        return str(loc)

    def get_file_and_rank(self) -> int:
        while True:
            loc = self.display.get_input("Enter position (e.g., e2): ").lower()
            if len(loc) == 2 and loc[0] in "abcdefgh" and loc[1] in "12345678":
                return self.notation_to_loc(loc)
            elif loc == "exit":
                return -1
            elif loc == "restart":
                return -2
            self.display.show_err(
                "Invalid input. Please enter a valid position like 'e2'."
            )

    def is_restart(self) -> bool:
        while True:
            cmd = self.display.get_input("Exit or Restart:").lower()
            if cmd == "exit":
                return False
            elif cmd == "restart":
                self.restart()
                return True
            else:
                self.display.show_err("Invalid input. Enter exit or restart")
                continue

    def list_moves(self, loc: Square) -> list[Square]:
        piece = self.engine.get_piece(loc)

        if piece is None:
            return []

        if piece.color != self.turn:
            self.display.show_err("It's not this piece's turn to move.")
            return []

        moves = self.engine.list_moves(piece)
        if len(moves) == 0:
            return []

        return moves

    def get_board(self) -> Board:
        return self.engine.board

    def get_turn(self) -> Color:
        return self.turn

    def run(self) -> None:
        self.display.show_board(self.engine.get_board(), self.turn)
        moves: list[Square] = []
        cur_selected: Optional[Piece] = None

        while True:
            if self.is_end:
                end_message: list[str] = ["Game over!"]
                if self.engine.is_in_check(self.turn):
                    end_message.append("Checkmate!")
                    end_message.append(f"{'White' if self.turn else 'Black'} wins!")
                else:
                    end_message.append("Stalemate!")
                    end_message.append("It's a draw!")
                self.display.show_board(self.engine.get_board(), self.turn)
                self.display.show_end_result("\n".join(end_message))
                moves = []
                cur_selected = None
                if self.is_restart():
                    self.display.show_board(self.engine.get_board(), self.turn)
                else:
                    break

            raw = self.get_file_and_rank()
            if raw == -1:
                break
            elif raw < -1:
                moves = []
                cur_selected = None
                self.display.show_err("Enter valid command.")
                continue

            loc = Square(raw)
            if len(moves) == 0:
                moves = self.list_moves(loc)
                if len(moves) > 0:
                    cur_selected = self.engine.get_piece(loc)
                    assert cur_selected is not None
            else:
                if loc in moves:
                    assert cur_selected is not None
                    self.engine.move_piece(cur_selected, loc)
                    self.turn = self.turn.other
                cur_selected = None
                moves = []

            self.display.show_board(self.engine.get_board(), self.turn, moves)

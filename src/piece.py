from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Iterator, Optional


type Board = list["Piece | None"]


@dataclass(eq=False)
class Piece(ABC):
    color: bool  # True for white, False for black
    loc: int
    notation: str = field(init=False)
    symbol: tuple[str, str] = field(init=False)
    ctrl_locs: list[int] = field(default_factory=list[int])
    captured: bool = False
    has_moved: bool = False
    navl_moves: int = 0

    @abstractmethod
    def gen_moves(self, board: Board) -> Iterator[int]:
        pass

    def validate_move(self, loc: int, board: Board) -> tuple[Optional[int], bool]:
        if not (0 <= loc < 64):
            return (None, True)
        target = board[loc]
        if target is None:
            return (loc, False)
        return (loc, True)


class Pawn(Piece):
    notation = "P"
    symbol = ("♟", "♙")

    def gen_moves(self, board: Board) -> Iterator[int]:
        direction = 1 if self.color else -1
        next_rank = (self.loc & 7) + direction
        file = self.loc >> 3

        if 0 <= next_rank < 8:
            next_loc = (file << 3) | next_rank
            if board[next_loc] is None:
                yield next_loc

            if not self.has_moved:
                double_loc = (file << 3) | (next_rank + direction)
                if board[double_loc] is None:
                    yield double_loc

            if file - 1 >= 0:
                left_loc = ((file - 1) << 3) | next_rank
                target = board[left_loc]
                if target is not None and target.color != self.color:
                    yield left_loc

            if file + 1 < 8:
                right_loc = ((file + 1) << 3) | next_rank
                target = board[right_loc]
                if target is not None and target.color != self.color:
                    yield right_loc


class Knight(Piece):
    notation = "N"
    symbol = ("♞", "♘")

    def gen_moves(self, board: Board) -> Iterator[int]:
        file = self.loc >> 3
        rank = self.loc & 7
        knight_offsets = [
            (2, 1),
            (2, -1),
            (-2, 1),
            (-2, -1),
            (1, 2),
            (1, -2),
            (-1, 2),
            (-1, -2),
        ]
        for df, dr in knight_offsets:
            f, r = file + df, rank + dr
            if 0 <= f < 8 and 0 <= r < 8:
                loc = (f << 3) | r
                yield loc


class Rook(Piece):
    notation = "R"
    symbol = ("♜", "♖")
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                loc = (f << 3) | r
                move, end = self.validate_move(loc, board)
                if move is not None:
                    yield move
                if end:
                    break


class Bishop(Piece):
    notation = "B"
    symbol = ("♝", "♗")
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3

        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                loc = (f << 3) | r
                move, end = self.validate_move(loc, board)
                if move is not None:
                    yield move
                if end:
                    break


class Queen(Piece):
    notation = "Q"
    symbol = ("♛", "♕")
    directions = Rook.directions + Bishop.directions

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                loc = (f << 3) | r
                move, end = self.validate_move(loc, board)
                if move is not None:
                    yield move
                if end:
                    break


class King(Piece):
    notation = "K"
    symbol = ("♚", "♔")
    directions = Queen.directions
    is_KCasteling: bool = False
    is_QCasteling: bool = False
    is_checked: bool = False
    checked_by: list[Piece] = field(default_factory=list[Piece])

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f = file + df
            r = rank + dr
            loc = (f << 3) | r
            move, _ = self.validate_move(loc, board)
            if move is not None:
                yield move


PIECE_MAP: dict[str, type[Piece]] = {
    "P": Pawn,
    "N": Knight,
    "B": Bishop,
    "R": Rook,
    "Q": Queen,
    "K": King,
}

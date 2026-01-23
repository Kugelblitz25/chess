from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Iterator, Optional


type Board = list[list["Piece | None"]]


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
    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        pass

    def validate_move(
        self, file: int, rank: int, board: Board
    ) -> tuple[Optional[tuple[int, int]], bool]:
        if not (0 <= file < 8 and 0 <= rank < 8):
            return (None, True)
        target = board[rank][file]
        if target is None:
            return ((file, rank), False)
        return ((file, rank), True)


class Pawn(Piece):
    notation = "P"
    symbol = ("♟", "♙")

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        direction = 1 if self.color else -1
        next_rank = (self.loc & 7) + direction
        file = self.loc >> 3
        if 0 <= next_rank < 8 and board[next_rank][file] is None:
            yield (file, next_rank)

            if not self.has_moved and board[next_rank + direction][file] is None:
                yield (file, next_rank + direction)

            if file - 1 >= 0:
                target = board[next_rank][file - 1]
                if target is not None and target.color != self.color:
                    yield (file - 1, next_rank)

            if file + 1 < 8:
                target = board[next_rank][file + 1]
                if target is not None and target.color != self.color:
                    yield (file + 1, next_rank)


class Knight(Piece):
    notation = "N"
    symbol = ("♞", "♘")

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        file = self.loc >> 3
        rank = self.loc & 7
        knight_moves = [
            (file + 2, rank + 1),
            (file + 2, rank - 1),
            (file - 2, rank + 1),
            (file - 2, rank - 1),
            (file + 1, rank + 2),
            (file + 1, rank - 2),
            (file - 1, rank + 2),
            (file - 1, rank - 2),
        ]
        for f, r in knight_moves:
            move, _ = self.validate_move(f, r, board)
            if move is not None:
                yield move


class Rook(Piece):
    notation = "R"
    symbol = ("♜", "♖")
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                move, end = self.validate_move(f, r, board)
                if move is not None:
                    yield move
                if end:
                    break


class Bishop(Piece):
    notation = "B"
    symbol = ("♝", "♗")
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        rank = self.loc & 7
        file = self.loc >> 3

        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                move, end = self.validate_move(f, r, board)
                if move is not None:
                    yield move
                if end:
                    break


class Queen(Piece):
    notation = "Q"
    symbol = ("♛", "♕")
    directions = Rook.directions + Bishop.directions

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                move, end = self.validate_move(f, r, board)
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

    def gen_moves(self, board: Board) -> Iterator[tuple[int, int]]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f = file + df
            r = rank + dr
            move, _ = self.validate_move(f, r, board)
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

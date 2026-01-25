from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional
from enum import IntEnum

type Board = list["Piece | None"]


class Color(IntEnum):
    WHITE = 0
    BLACK = 1

    def switch(self) -> "Color":
        return Color(self.value ^ 1)


class Type(IntEnum):
    PAWN = 2
    KNIGHT = 4
    BISHOP = 6
    ROOK = 8
    QUEEN = 10
    KING = 12


NOT_MAP: dict[str, type["Piece"]] = {}


@dataclass(eq=False)
class Piece(ABC):
    id: int
    loc: int
    notation: str = field(init=False)
    ctrl_locs: list[int] = field(default_factory=list[int])
    captured: bool = False
    has_moved: bool = False
    nmoves: int = field(init=False)
    is_checked: bool = False
    checked_by: list["Piece"] = field(default_factory=list["Piece"])
    direction: list[tuple[int, int]] = field(default_factory=list, init=False)

    @property
    def color(self) -> Color:
        return Color(self.id & 1)

    @property
    def type(self) -> Type:
        return Type(self.id & 14)

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        NOT_MAP[cls.notation] = cls

    @classmethod
    def from_notation(cls, notation: str, loc: int) -> "Piece":
        if notation.upper() not in NOT_MAP:
            raise ValueError("Invalid Notation")
        piece_class = NOT_MAP[notation.upper()]
        color = Color(notation.islower())
        ptype = Type[piece_class.__name__.upper()]
        return piece_class(ptype | color, loc)

    @abstractmethod
    def gen_moves(self, board: Board) -> Iterator[int]:
        pass

    def move(self, loc: int) -> None:
        self.loc = loc
        self.has_moved = True

    def validate_move(
        self, file: int, rank: int, board: Board
    ) -> tuple[Optional[int], bool]:
        if not (0 <= file < 8 and 0 <= rank < 8):
            return (None, True)
        loc = (file << 3) | rank
        target = board[loc]
        if target is None:
            return (loc, False)
        return (loc, True)


@dataclass(eq=False)
class Pawn(Piece):
    notation = "P"

    def __post_init__(self) -> None:
        rank = self.loc & 7
        if (self.color and rank == 6) or (not self.color and rank == 1):
            self.has_moved = False
        else:
            self.has_moved = True

    def gen_moves(self, board: Board) -> Iterator[int]:
        direction = -1 if self.color else 1
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
                yield left_loc

            if file + 1 < 8:
                right_loc = ((file + 1) << 3) | next_rank
                yield right_loc


@dataclass(eq=False)
class Knight(Piece):
    notation = "N"
    directions = [
        (2, 1),
        (2, -1),
        (-2, 1),
        (-2, -1),
        (1, 2),
        (1, -2),
        (-1, 2),
        (-1, -2),
    ]

    def gen_moves(self, board: Board) -> Iterator[int]:
        file = self.loc >> 3
        rank = self.loc & 7
        for df, dr in self.directions:
            f, r = file + df, rank + dr
            if 0 <= f < 8 and 0 <= r < 8:
                loc = (f << 3) | r
                yield loc


@dataclass(eq=False)
class Rook(Piece):
    notation = "R"
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
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


@dataclass(eq=False)
class Bishop(Piece):
    notation = "B"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
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


@dataclass(eq=False)
class Queen(Piece):
    notation = "Q"
    directions = Rook.directions + Bishop.directions

    def gen_moves(self, board: Board) -> Iterator[int]:
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


@dataclass(eq=False)
class King(Piece):
    notation = "K"
    directions = Queen.directions
    is_checked: bool = False
    checked_by: list[Piece] = field(default_factory=list[Piece])

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f = file + df
            r = rank + dr
            move, _ = self.validate_move(f, r, board)
            if move is not None:
                yield move

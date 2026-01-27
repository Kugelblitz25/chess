from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Iterator, Optional

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


def sign(n: int) -> int:
    return (n > 0) - (n < 0)


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
    directions: list[tuple[int, int]] = field(init=False)

    @property
    def color(self) -> Color:
        return Color(self.id & 1)

    @property
    def type(self) -> Type:
        return Type(self.id & 14)

    @property
    def is_sliding(self) -> bool:
        return self.type in (Type.BISHOP, Type.ROOK, Type.QUEEN)

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

    def is_in_dir(self, loc: int) -> Optional[tuple[int, int]]:
        dst_file, dst_rank = loc >> 3, loc & 7
        src_file, src_rank = self.loc >> 3, self.loc & 7
        dir = (sign(dst_file - src_file), sign(dst_rank - src_rank))
        if dir in self.directions:
            return dir
        return None

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

        direction = -1 if self.color else 1
        self.directions = [
            (0, direction),
            (0, 2 * direction),
            (-1, direction),
            (1, direction),
        ]

    def gen_moves(self, board: Board) -> Iterator[int]:
        direction = -1 if self.color else 1
        next_rank = (self.loc & 7) + direction
        file = self.loc >> 3

        move, end = self.validate_move(file, next_rank, board)
        if move is None:
            return None

        if not end:
            yield move

            if not self.has_moved:
                double_move, end = self.validate_move(
                    file, next_rank + direction, board
                )
                if not end and double_move is not None:
                    yield double_move

        left_loc, _ = self.validate_move(file - 1, next_rank, board)
        if left_loc is not None:
            yield left_loc

        right_loc, _ = self.validate_move(file + 1, next_rank, board)
        if right_loc is not None:
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

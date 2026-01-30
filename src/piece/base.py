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
    PAWN = 0
    KNIGHT = 2
    BISHOP = 4
    ROOK = 6
    QUEEN = 8
    KING = 10


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

    @property
    def nmoves(self) -> int:
        return len(self.ctrl_locs)

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        NOT_MAP[cls.notation] = cls

    @classmethod
    def get_type_from_notation(cls, notation: str) -> Type:
        pclass = NOT_MAP[notation.upper()]
        return Type[pclass.__name__.upper()]

    @classmethod
    def from_notation(cls, notation: str, loc: int) -> "Piece":
        if notation.upper() not in NOT_MAP:
            raise ValueError("Invalid Notation")
        piece_class = NOT_MAP[notation.upper()]
        color = Color(notation.islower())
        ptype = cls.get_type_from_notation(notation)
        return piece_class(ptype | color, loc)

    def to_notation(self) -> str:
        if self.color == Color.BLACK:
            return self.notation.lower()
        else:
            return self.notation.upper()

    @abstractmethod
    def gen_moves(self, board: Board) -> Iterator[int]:
        pass

    def move(self, loc: int) -> None:
        self.loc = loc
        self.has_moved = True

    def is_in_dir(self, loc: int) -> Optional[tuple[int, int]]:
        dst_file, dst_rank = loc >> 3, loc & 7
        src_file, src_rank = self.loc >> 3, self.loc & 7
        df, dr = dst_file - src_file, dst_rank - src_rank
        for f, r in self.directions:
            if f * dr - r * df == 0 and f * df + r * dr > 0:
                return (f, r)
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


from .pawn import Pawn
from .rook import Rook

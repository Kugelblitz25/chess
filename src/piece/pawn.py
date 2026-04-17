from dataclasses import dataclass
from typing import Generator, Optional

from ..square import Square
from .base import Piece


@dataclass(eq=False, slots=True)
class Pawn(Piece):
    notation = "P"

    def __post_init__(self) -> None:
        rank = self.loc.rank
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

    def gen_moves(self) -> Generator[Square, Optional[int], None]:
        direction = -1 if self.color else 1

        sq = self.loc.move_dir(0, direction)
        if sq is not None:
            yield sq

        if not self.has_moved:
            sq2 = self.loc.move_dir(0, 2 * direction)
            if sq2 is not None:
                yield sq2

        for df in (-1, 1):
            sq = self.loc.move_dir(df, direction)
            if sq is not None:
                yield sq

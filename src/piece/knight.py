from dataclasses import dataclass
from typing import Generator, Optional

from ..square import Square
from .base import Piece


@dataclass(eq=False, slots=True)
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

    def gen_moves(self) -> Generator[Square, Optional[bool], None]:
        for df, dr in self.directions:
            sq = Square.from_coords(self.loc.file + df, self.loc.rank + dr)
            if sq is not None:
                yield sq

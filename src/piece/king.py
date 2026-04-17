from dataclasses import dataclass
from typing import Generator, Optional

from ..square import Square
from .base import Piece


@dataclass(eq=False, slots=True)
class King(Piece):
    notation = "K"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self) -> Generator[Square, Optional[bool], None]:
        for df, dr in self.directions:
            sq = Square.from_coords(self.loc.file + df, self.loc.rank + dr)
            if sq is not None:
                yield sq

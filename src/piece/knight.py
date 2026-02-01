from dataclasses import dataclass
from typing import Generator, Optional

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

    def gen_moves(self) -> Generator[int, Optional[bool], None]:
        file = self.loc >> 3
        rank = self.loc & 7
        for df, dr in self.directions:
            f, r = file + df, rank + dr
            if self.is_in_bounds(f, r):
                loc = (f << 3) | r
                yield loc

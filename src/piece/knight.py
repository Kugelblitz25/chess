from dataclasses import dataclass
from typing import Iterator

from .base import Piece, Board


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

    def gen_moves(self, board: Board) -> Iterator[int]:
        file = self.loc >> 3
        rank = self.loc & 7
        for df, dr in self.directions:
            f, r = file + df, rank + dr
            if 0 <= f < 8 and 0 <= r < 8:
                loc = (f << 3) | r
                yield loc

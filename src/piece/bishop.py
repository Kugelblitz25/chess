from dataclasses import dataclass
from typing import Generator, Optional

from .base import Piece


@dataclass(eq=False, slots=True)
class Bishop(Piece):
    notation = "B"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

    def gen_moves(self) -> Generator[int, Optional[bool], None]:
        rank = self.loc & 7
        file = self.loc >> 3

        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                if not self.is_in_bounds(f, r):
                    break
                stp = yield (f << 3) | r
                if stp:
                    yield -1  # Quirk of Generator
                    break

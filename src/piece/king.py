from dataclasses import dataclass
from typing import Generator, Optional

from .base import Piece


@dataclass(eq=False, slots=True)
class King(Piece):
    notation = "K"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self) -> Generator[int, Optional[bool], None]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f = file + df
            r = rank + dr
            if self.is_in_bounds(f, r):
                yield (f << 3) | r

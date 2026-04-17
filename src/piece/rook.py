from dataclasses import dataclass
from typing import Generator, Optional

from ..square import Square
from .base import Piece


@dataclass(eq=False, slots=True)
class Rook(Piece):
    notation = "R"
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self) -> Generator[Square, Optional[bool], None]:
        for df, dr in self.directions:
            f, r = self.loc.file, self.loc.rank
            while True:
                f += df
                r += dr
                sq = Square.from_coords(f, r)
                if sq is None:
                    break
                stp = yield sq
                if stp:
                    yield Square(0)  # consumed by generator.send(); never seen by for-loop
                    break

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
            sq = self.loc.move_dir(df, dr)
            if sq is not None:
                yield sq

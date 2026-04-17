from dataclasses import dataclass
from typing import Generator, Optional

from ..square import Square
from .base import Piece


@dataclass(eq=False, slots=True)
class Queen(Piece):
    notation = "Q"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self) -> Generator[Square, Optional[bool], None]:
        for df, dr in self.directions:
            sq: Square = self.loc
            while (next_sq := sq.move_dir(df, dr)) is not None:
                stp = yield next_sq
                sq = next_sq
                if stp:
                    yield Square(0)  # consumed by generator.send(); never seen by for-loop
                    break

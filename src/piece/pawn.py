from dataclasses import dataclass
from typing import Generator, Optional

from .base import Piece


@dataclass(eq=False, slots=True)
class Pawn(Piece):
    notation = "P"

    def __post_init__(self) -> None:
        rank = self.loc & 7
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

    def gen_moves(self) -> Generator[int, Optional[int], None]:
        direction = -1 if self.color else 1
        next_rank = (self.loc & 7) + direction
        file = self.loc >> 3

        if self.is_in_bounds(file, next_rank):
            yield (file << 3) | next_rank

        if not self.has_moved:
            if self.is_in_bounds(file, next_rank + direction):
                yield (file << 3) | (next_rank + direction)

        if self.is_in_bounds(file - 1, next_rank):
            yield ((file - 1) << 3) | next_rank

        if self.is_in_bounds(file + 1, next_rank):
            yield ((file + 1) << 3) | next_rank

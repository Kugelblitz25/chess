from dataclasses import dataclass
from typing import Iterator

from .base import Piece, Board


@dataclass(eq=False, slots=True)
class King(Piece):
    notation = "K"
    directions = [(1, 1), (1, -1), (-1, 1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f = file + df
            r = rank + dr
            move, _ = self.validate_move(f, r, board)
            if move is not None:
                yield move

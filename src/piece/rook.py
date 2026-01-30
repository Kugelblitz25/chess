from dataclasses import dataclass
from typing import Iterator

from .base import Piece, Board


@dataclass(eq=False, slots=True)
class Rook(Piece):
    notation = "R"
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    def gen_moves(self, board: Board) -> Iterator[int]:
        rank = self.loc & 7
        file = self.loc >> 3
        for df, dr in self.directions:
            f, r = file, rank
            while True:
                f += df
                r += dr
                move, end = self.validate_move(f, r, board)
                if move is not None:
                    yield move
                if end:
                    break

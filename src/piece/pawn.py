from dataclasses import dataclass
from typing import Iterator

from .base import Board, Piece


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

    def gen_moves(self, board: Board) -> Iterator[int]:
        direction = -1 if self.color else 1
        next_rank = (self.loc & 7) + direction
        file = self.loc >> 3

        move, _ = self.validate_move(file, next_rank, board)
        if move is None:
            return None

        yield move

        if not self.has_moved:
            double_move, _ = self.validate_move(file, next_rank + direction, board)
            if double_move is not None:
                yield double_move

        left_loc, _ = self.validate_move(file - 1, next_rank, board)
        if left_loc is not None:
            yield left_loc

        right_loc, _ = self.validate_move(file + 1, next_rank, board)
        if right_loc is not None:
            yield right_loc

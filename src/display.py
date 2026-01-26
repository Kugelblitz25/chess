from typing import Protocol

from .board import Board
from .piece import Color


class UI(Protocol):
    def show_board(
        self, board: Board, side: Color, highlight: list[int] | None = None
    ) -> None: ...

from typing import Protocol

from .piece import Color

from .board import Board


class UI(Protocol):
    def show_board(
        self, board: Board, side: Color, highlight: list[int] | None = None
    ) -> None: ...

from typing import Protocol

from .board import Board


class Display(Protocol):
    def show_board(self, board: Board, highlight: list[int] | None = None) -> None: ...

from typing import Protocol

from src.board import Board
from src.piece import Color


class UI(Protocol):
    def show_board(
        self, board: Board, side: Color, highlight: list[int] | None = None
    ) -> None: ...

    def get_input(self, query: str) -> str: ...

    def show_err(self, message: str) -> None: ...

    def show_end_result(self, message: str) -> None: ...

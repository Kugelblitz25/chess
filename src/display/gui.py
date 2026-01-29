import tkinter as tk
from typing import Optional

from src.board import Board
from src.piece import Color, Piece


LIGHT_SQUARE = "#F0D9B5"
DARK_SQUARE = "#B58863"
HIGHLIGHT_COLOR = "#90EE90"
DOT_COLOR = "#228B22"
SQUARE_SIZE = 80
LABEL_SIZE = 30


class TkDisplay:
    def __init__(self) -> None:
        self.board_widget: Optional[Board] = None
        self.side = Color.WHITE
        self.highlight: list[int] = []
        self.input_queue: list[str] = []
        self.waiting_for_input = False

        self.root = tk.Tk()
        self.root.title("Chess Engine")

        board_size = 8 * SQUARE_SIZE

        disp_frame = tk.Frame(
            self.root, width=board_size + LABEL_SIZE, height=board_size + LABEL_SIZE
        )
        disp_frame.pack(padx=10, pady=(10, 5))

        self.rank_canvas = tk.Canvas(disp_frame, width=LABEL_SIZE, height=board_size)
        self.rank_canvas.grid(row=0, column=0)

        self.canvas = tk.Canvas(
            disp_frame, width=board_size, height=board_size, bg=LIGHT_SQUARE
        )
        self.canvas.grid(row=0, column=1)

        self.file_canvas = tk.Canvas(disp_frame, width=board_size, height=LABEL_SIZE)
        self.file_canvas.grid(row=1, column=1)

        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.message_label = tk.Label(
            control_frame,
            text="",
            font=("Arial", 14),
            wraplength=board_size + 2 * LABEL_SIZE,
            justify=tk.CENTER,
            fg="black",
        )
        self.message_label.pack(anchor=tk.CENTER, pady=0)

        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.canvas.bind("<Button-1>", self._on_board_click)

    def _on_closing(self) -> None:
        self.root.destroy()
        self.input_queue.append("exit")

    def _get_piece_symbol(self, piece: Piece) -> str:
        symbols = {
            "K": ("♚", "♔"),
            "Q": ("♛", "♕"),
            "R": ("♜", "♖"),
            "B": ("♝", "♗"),
            "N": ("♞", "♘"),
            "P": ("♟", "♙"),
        }
        return symbols[piece.notation][piece.color]

    def _draw_board(self) -> None:
        self.canvas.delete("all")
        self.rank_canvas.delete("all")
        self.file_canvas.delete("all")

        if self.board_widget is None:
            return

        highlight_set = set(self.highlight)

        for r in range(8):
            for f in range(8):
                rank = 7 - r if self.side == Color.WHITE else r
                file = 7 - f if self.side == Color.BLACK else f
                loc = (file << 3) | rank

                x1 = f * SQUARE_SIZE
                y1 = r * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                is_light = (file + rank) % 2 == 0
                is_highlighted = loc in highlight_set

                if is_highlighted:
                    color = HIGHLIGHT_COLOR
                else:
                    color = LIGHT_SQUARE if is_light else DARK_SQUARE

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board_widget.board[loc]

                if is_highlighted and piece is None:
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    radius = SQUARE_SIZE / 6
                    self.canvas.create_oval(
                        cx - radius,
                        cy - radius,
                        cx + radius,
                        cy + radius,
                        fill=DOT_COLOR,
                        outline="",
                    )
                elif piece is not None:
                    symbol = self._get_piece_symbol(piece)
                    piece_color = "white" if piece.color == Color.WHITE else "black"

                    self.canvas.create_text(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        text=symbol,
                        font=("Arial", int(SQUARE_SIZE * 0.6)),
                        fill=piece_color,
                    )

        file_labels = "abcdefgh"
        if self.side == Color.BLACK:
            file_labels = file_labels[::-1]

        for i, label in enumerate(file_labels):
            self.file_canvas.create_text(
                (i + 0.5) * SQUARE_SIZE,
                LABEL_SIZE / 2,
                text=label,
                font=("Arial", 14),
            )

        for i in range(8):
            rank = i if self.side == Color.BLACK else 7 - i
            self.rank_canvas.create_text(
                LABEL_SIZE / 2,
                (i + 0.5) * SQUARE_SIZE,
                text=rank + 1,
                font=("Arial", 14),
            )

    def _on_board_click(self, event) -> None:
        self.message_label.config(text="")
        f = event.x // SQUARE_SIZE
        r = event.y // SQUARE_SIZE

        if not (0 <= f < 8 and 0 <= r < 8):
            return

        rank = 7 - r if self.side == Color.WHITE else r
        file = 7 - f if self.side == Color.BLACK else f

        value = f"{chr(file + ord('a'))}{rank + 1}"
        if self.waiting_for_input:
            self.input_queue.append(value)
            self.waiting_for_input = False

    def show_board(
        self,
        board: Board,
        side: Color,
        highlight: list[int] | None = None,
    ) -> None:
        self.board_widget = board
        self.side = side
        self.highlight = highlight if highlight is not None else []
        self._draw_board()
        self.root.update()

    def get_input(self, query: str) -> str:
        self.waiting_for_input = True

        while not self.input_queue:
            self.root.update()
            self.root.update_idletasks()

        result = self.input_queue.pop(0)
        return result

    def show_err(self, message: str) -> None:
        self.message_label.config(text=f"Error: {message}", fg="red")
        self.root.update()

    def show_success(self, message: str) -> None:
        self.message_label.config(text=message, fg="green")
        self.root.update()

    def run(self) -> None:
        self.root.mainloop()

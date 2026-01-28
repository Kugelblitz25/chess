from .board import Board
from .display import UI
from .piece import Color


class Game:
    def __init__(self, board: Board, display: UI, turn: Color = Color.WHITE) -> None:
        self.board = board
        self.display = display
        self.turn = turn

    @property
    def is_end(self) -> bool:
        return self.board.nmoves(self.turn) == 0

    def notation_to_loc(self, notation: str) -> int:
        file = ord(notation[0].lower()) - ord("a")
        rank = int(notation[1])
        return (file << 3) | (rank - 1)

    def index_to_notation(self, loc: int) -> str:
        file, rank = loc >> 3, loc & 7
        return f"{chr(file + ord('a'))}{rank + 1}"

    def get_file_and_rank(self) -> int:
        while True:
            loc = input("Enter position (e.g., e2): ").strip().lower()
            if not (len(loc) == 2 and loc[0] in "abcdefgh" and loc[1] in "12345678"):
                print("Invalid input. Please enter a valid position like 'e2'.")
                continue
            return self.notation_to_loc(loc)

    def list_moves(self) -> None:
        while True:
            loc = self.get_file_and_rank()
            piece = self.board.board[loc]
            if piece is None:
                print("No piece at the given location.")
                continue
            if piece.color != self.turn:
                print("It's not this piece's turn to move.")
                continue
            break
        moves = self.board.list_moves(piece)
        if len(moves) == 0:
            print("No valid moves for this piece.")
            return
        self.display.show_board(self.board, self.turn, moves)
        print()

    def move(self) -> None:
        while True:
            src = self.get_file_and_rank()
            piece = self.board.board[src]
            if piece is None:
                print("No piece at the given location. Choose another piece.")
                continue
            if piece.color != self.turn:
                print("It's not this piece's turn to move. Choose another piece.")
                continue
            moves = self.board.list_moves(piece)
            if len(moves) == 0:
                print("No valid moves for this piece. Choose another piece.")
                continue
            self.display.show_board(self.board, self.turn, moves)
            break

        while True:
            dst = self.get_file_and_rank()
            if self.board.is_own(piece, dst):
                print("Cannot capture your own piece.")
                continue
            if dst not in moves:
                print("Invalid move. Please choose a valid move.")
                continue
            break

        self.board.move_piece(piece, dst)
        self.turn = self.turn.switch()
        self.display.show_board(self.board, self.turn)

    def get_board(self) -> Board:
        return self.board

    def get_turn(self) -> Color:
        return self.turn

    def run(self) -> None:
        print("\nCurrent Board:")
        self.display.show_board(self.board, self.turn)
        while True:
            if self.is_end:
                print("Game over!")
                if self.board.is_in_check(self.board.get_king(self.turn)):
                    print("Checkmate!")
                    print(f"{'White' if self.turn else 'Black'} wins!")
                else:
                    print("Stalemate!")
                    print("It's a draw!")
                break

            cmd = input("cmd>> ").strip().lower()
            if cmd == "exit":
                break
            elif cmd == "move":
                self.move()
            elif cmd == "lmv":
                self.list_moves()
            else:
                print("Unknown command. Available commands: move, lmv, exit.")

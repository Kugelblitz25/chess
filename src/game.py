from .board import Board
from .piece import Piece
from .display import display_board


class Game:
    def __init__(self, board: Board, turn: bool = False) -> None:
        self.board = board
        self.turn = turn  # False for White, True for Black

    @property
    def is_end(self) -> bool:
        return self.board.navl_moves[self.turn] == 0

    def notation_to_loc(self, notation: str) -> int:
        file = ord(notation[0].lower()) - ord("a")
        rank = 8 - int(notation[1])
        return (file << 3) | rank

    def index_to_notation(self, loc: int) -> str:
        file, rank = loc >> 3, loc & 7
        return f"{chr(file + ord('a'))}{8 - rank}"

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
        print("Valid moves:")
        for move in moves:
            notation = self.index_to_notation(move)
            print(notation, end=" ")
        print()

    def move(self) -> bool:
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
            print("Valid moves:")
            for move in moves:
                notation = self.index_to_notation(move)
                print(notation, end=" ")
            print()
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
        self.turn = not self.turn

        if self.is_end:
            print("Game over!")
            if self.board.is_in_check(self.board.kings[self.turn]):
                print("Checkmate!")
                print(f"{'White' if self.turn else 'Black'} wins!")
            else:
                print("Stalemate!")
                print("It's a draw!")
            return False
        return True

    def get_board(self) -> Board:
        return self.board

    def get_turn(self) -> bool:
        return self.turn

    def run(self) -> None:
        while True:
            print("\nCurrent Board:")
            display_board(self.board)
            cmd = input("cmd>> ").strip().lower()
            if cmd == "exit":
                break
            elif cmd == "move":
                if not self.move():
                    break
            elif cmd == "lmv":
                self.list_moves()
            else:
                print("Unknown command. Available commands: move, lmv, exit.")

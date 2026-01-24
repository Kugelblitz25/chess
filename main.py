from src.board import Board
from src.game import Game
from src.term import TermDisplay


def main():
    print("Hello from chess-engine!")
    board = Board()
    display = TermDisplay()
    # board = Board("rnbqkbnr/1ppppppp/8/8/p1B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    game = Game(board, display)
    game.run()


if __name__ == "__main__":
    main()

from src.board import Board
from src.game import Game


def main():
    print("Hello from chess-engine!")
    board = Board()
    # board = Board("rnbqkbnr/1ppppppp/8/8/p1B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    game = Game(board)
    game.run()


if __name__ == "__main__":
    main()

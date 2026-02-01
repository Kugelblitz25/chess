from src.display.gui import TkDisplay
from src.engine import Engine
from src.game import Game

# from src.display.term import TermDisplay


def main() -> None:
    print("Hello from chess-engine!")
    engine = Engine()
    display = TkDisplay()
    # board = Board("rnbqkbnr/1ppppppp/8/8/p1B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 0 1")
    game = Game(engine, display)
    game.run()


if __name__ == "__main__":
    main()

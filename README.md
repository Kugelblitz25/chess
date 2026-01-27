<div align="center">

![Chess Banner](https://images.unsplash.com/photo-1586165368502-1bad197a6461?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80)

# Chess Engine

**A Python-based chess engine with a terminal interface for playing chess games.**

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg?style=for-the-badge)](https://github.com/)

</div>

---

## Features

**Full chess rules implementation including:**
* All piece movements (Pawn, Knight, Bishop, Rook, Queen, King)
* En passant captures
* Check and checkmate detection
* Pin detection and handling
* Legal move generation
* Terminal-based display with Unicode chess pieces
* FEN notation support for custom board positions
* Interactive command-line interface

---

## Installation

No external dependencies required. Uses Python standard library only.

---

## Usage

Run the game:

```bash
python main.py

```

### Available Commands

| Command | Description |
| --- | --- |
| `move` | Make a move (prompts for source and destination) |
| `lmv` | List valid moves for a piece |
| `exit` | Exit the game |

### Input Format

Positions are entered using standard chess notation (e.g., `e2`, `e4`):

* **Files:** a-h (columns)
* **Ranks:** 1-8 (rows)

### Example Game Flow

```bash

  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗
8 ║ r │ n │ b │ q │ k │ b │ n │ r ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
7 ║ p │ p │ p │ p │ p │ p │ p │ p ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
6 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
5 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
4 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
3 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
2 ║ P │ P │ P │ P │ P │ P │ P │ P ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
1 ║ R │ N │ B │ Q │ K │ B │ N │ R ║
  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝
    a   b   c   d   e   f   g   h
cmd>> move
Enter position (e.g., e2): e2

  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗
8 ║ r │ n │ b │ q │ k │ b │ n │ r ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
7 ║ p │ p │ p │ p │ p │ p │ p │ p ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
6 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
5 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
4 ║   │   │   │   │ ● │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
3 ║   │   │   │   │ ● │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
2 ║ P │ P │ P │ P │ P │ P │ P │ P ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
1 ║ R │ N │ B │ Q │ K │ B │ N │ R ║
  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝
    a   b   c   d   e   f   g   h
Enter position (e.g., e2): e4

  ╔═══╤═══╤═══╤═══╤═══╤═══╤═══╤═══╗
1 ║ R │ N │ B │ K │ Q │ B │ N │ R ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
2 ║ P │ P │ P │   │ P │ P │ P │ P ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
3 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
4 ║   │   │   │ P │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
5 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
6 ║   │   │   │   │   │   │   │   ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
7 ║ p │ p │ p │ p │ p │ p │ p │ p ║
  ╟───┼───┼───┼───┼───┼───┼───┼───╢
8 ║ r │ n │ b │ k │ q │ b │ n │ r ║
  ╚═══╧═══╧═══╧═══╧═══╧═══╧═══╧═══╝
    h   g   f   e   d   c   b   a
```

---

## Project Structure

```text
chess-engine/
├── main.py           # Entry point
├── src/
│   ├── __init__.py
│   ├── piece.py      # Piece classes and movement logic
│   ├── board.py      # Board state and move validation
│   ├── game.py       # Game loop and user interaction
│   ├── term.py       # Terminal display
│   ├── display.py    # Display protocol
│   └── engine.py     # Engine utilities (WIP)
└── README.md

```

---

## Technical Details

### Board Representation

* 64-element array with bitboard-style indexing
* **Location encoding:** `(file << 3) | rank`
* **Files:** 0-7 (a-h)
* **Ranks:** 0-7 (1-8)

### Move Generation

* Pre-calculated attack boards for efficient move validation
* Pin detection using directional analysis
* Check blocking and evasion logic
* En passant validation with pin consideration

### Color Coding

Piece IDs encode both type and color: `Type | Color`

**Color:**

| Color | Value |
| --- | --- |
| 0 | White |
| 1 | Black |

**Types:**

| Piece | Value |
| --- | --- |
| PAWN | 2 |
| KNIGHT | 4 |
| BISHOP | 6 |
| ROOK | 8 |
| QUEEN | 10 |
| KING | 12 |

### FEN Support

Load custom positions by passing a FEN string to the Board constructor:

```python
board = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

```

---

## Future Enhancements

- [ ] Castling implementation
- [ ] Pawn promotion
- [ ] Move history and undo
- [ ] AI opponent
- [ ] Time controls
- [ ] PGN export

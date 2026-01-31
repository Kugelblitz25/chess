from typing import Iterator, Optional

from .piece import Color, Piece, Type


class AttackBoard:
    def __init__(self, size: int) -> None:
        self.board: list[list[Piece]] = [[] for _ in range(size)]

    def get_attackers(self, color: Color, loc: int) -> Iterator[Piece]:
        for p in self.board[loc]:
            if p.color == color:
                yield p

    def get_pattackers(self, loc: int) -> Iterator[Piece]:
        for p in self.board[loc]:
            yield p

    def add_attacker(self, piece: Piece) -> None:
        for loc in Piece.bb_to_loc(piece.ctrls):
            self.board[loc].append(piece)

    def remove_attacker(self, piece: Piece) -> None:
        for loc in Piece.bb_to_loc(piece.ctrls):
            self.board[loc].remove(piece)


class Board:
    def __init__(self, size: int = 64) -> None:
        self.board: list[Piece | None] = [None] * size
        self.ep_candidate: Optional[Piece] = None
        self.pinned: list[Piece] = []
        self.pieces: list[list[Piece]] = [[] for _ in range(2 * max(Type))]

    def is_empty(self, loc: int):
        return self.board[loc] is None

    def put_piece(self, piece: Piece, loc: int) -> None:
        self.board[loc] = piece
        self.pieces[piece.id].append(piece)

    def remove_piece(self, piece: Piece) -> None:
        self.board[piece.loc] = None
        self.pieces[piece.id].remove(piece)

    def move_piece(self, piece: Piece, loc: int) -> None:
        self.board[piece.loc] = None
        self.board[loc] = piece
        piece.move(loc)

    def get_piece(self, loc: int) -> Optional[Piece]:
        return self.board[loc]

    def get_piece_from_SAN(
        self, notation: str, file: Optional[int] = None, rank: Optional[int] = None
    ) -> Piece:
        if not notation:
            raise ValueError("Invalid Notation: No such type of piece")
        color = Color.BLACK if notation.islower() else Color.WHITE
        ptype = Piece.get_type_from_notation(notation)

        if file is None and rank is None:
            if len(self.pieces[ptype | color]) == 1:
                return self.pieces[ptype | color][0]
            else:
                raise ValueError("Invalid Notation: Ambiguous notation")

        loc: Optional[int] = None

        if file is not None and rank is not None:
            loc = (file << 3) | rank

        piece: Optional[Piece] = None
        for p in self.pieces[ptype | color]:
            if loc is not None and p.loc == loc:
                if piece is None:
                    piece = p
                else:
                    raise ValueError("Invalid Notation: Ambiguous notation")
            elif file is not None and (p.loc >> 3) == file:
                if piece is None:
                    piece = p
                else:
                    raise ValueError("Invalid Notation: Ambiguous notation")

            elif rank is not None and (p.loc & 7) == rank:
                if piece is None:
                    piece = p
                else:
                    raise ValueError("Invalid Notation: Ambiguous notation")

        if piece is None:
            raise ValueError("Invalid Notation: No such piece found")

        return piece

    def get_all_pieces(self, color: Color) -> list[Piece]:
        pieces = []
        for t in Type:
            pieces += self.pieces[t | color]
        return pieces

    def get_king(self, color: Color) -> Piece:
        return self.pieces[Type.KING | color][0]

    def is_adj_file(self, loc1: int, loc2: int) -> bool:
        return abs((loc1 >> 3) - (loc2 >> 3)) == 1

    def capture(self, piece: Piece) -> None:
        piece.captured = True
        self.remove_piece(piece)

from typing import Optional

from .piece import PIECE_MAP, King, Pawn, Piece


class Board:
    def __init__(self, fen: Optional[str] = None, turn: bool = False) -> None:
        self.board: list[Piece | None] = [None] * 64
        self.fboard: list[set[Piece]] = [set() for _ in range(64)]
        self.ep_candidate: Optional[Piece] = None
        if fen:
            kings, pieces = self.load_fen(fen)
            self.turn = turn
        else:
            kings, pieces = self.setup_starting_position()
            self.turn = False  # White starts

        self.pieces = pieces
        if kings[0].color:
            self.kings = [kings[1], kings[0]]
        else:
            self.kings = [kings[0], kings[1]]

        for loc in range(64):
            piece = self.board[loc]
            if piece is None:
                continue
            self.recalc_fboard(piece)

    def load_fen(self, fen: str) -> tuple[list[King], list[list[Piece]]]:
        board_state = fen.split(" ")[0]
        rows = board_state.split("/")
        pieces: list[list[Piece]] = [[], []]
        kings: list[King] = []

        for r, row in enumerate(rows):
            file = 0
            for char in row:
                if char.isdigit():
                    file += int(char)
                else:
                    loc = (file << 3) | r
                    color = char.islower()
                    piece = PIECE_MAP[char.upper()](color, loc)
                    pieces[color].append(piece)
                    if isinstance(piece, King):
                        kings.append(piece)
                    self.board[loc] = piece
                    file += 1
        return kings, pieces

    def setup_starting_position(self) -> tuple[list[King], list[list[Piece]]]:
        return self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def nmoves(self, color: bool) -> int:
        return sum(p.nmoves for p in self.pieces[color])

    def is_adj_file(self, loc1: int, loc2: int) -> bool:
        return abs((loc1 >> 3) - (loc2 >> 3)) == 1

    def is_valid_pawn_move(self, piece: Pawn, loc: int) -> bool:
        if not self.is_adj_file(piece.loc, loc):
            return True
        if self.board[loc] is not None:
            return True

        if self.ep_candidate is None or abs(piece.loc - self.ep_candidate.loc) != 8:
            return False
        if (loc >> 3) != (self.ep_candidate.loc >> 3):
            return False
        return True

    def does_blocks_check(self, piece: Piece, to_loc: int) -> bool:
        king = self.kings[piece.color]

        if len(king.checked_by) != 1:
            return isinstance(piece, King)

        attacker = king.checked_by[0]
        if to_loc == attacker.loc:
            return True

        if to_loc not in attacker.ctrl_locs:
            return False

        df = (king.loc >> 3) - (attacker.loc >> 3)
        dr = (king.loc & 7) - (attacker.loc & 7)
        df_dest = (to_loc >> 3) - (attacker.loc >> 3)
        dr_dest = (to_loc & 7) - (attacker.loc & 7)

        if df * dr_dest != dr * df_dest:
            return False

        if df != 0:
            t = df_dest / df
        else:
            t = dr_dest / dr

        return 0 < t < 1

    def is_own(self, piece: Piece, loc: int) -> bool:
        target = self.board[loc]
        return target is not None and target.color == piece.color

    def is_threatened(self, piece: Piece, loc: int) -> bool:
        for attacker in self.fboard[loc]:
            if attacker.color != piece.color:
                if isinstance(attacker, Pawn):
                    return self.is_adj_file(attacker.loc, loc)
                else:
                    return True
        return False

    def calc_fboard_pawn(self, piece: Pawn) -> None:
        king = self.kings[piece.color]
        for loc in piece.gen_moves(self.board):
            if king.is_checked:
                if not self.is_valid_pawn_move(piece, loc):
                    continue
                if not self.does_blocks_check(piece, loc):
                    continue
            if not self.is_own(piece, loc) and self.is_valid_pawn_move(piece, loc):
                piece.nmoves += 1
            piece.ctrl_locs.append(loc)
            self.fboard[loc].add(piece)

    def recalc_fboard(self, piece: Piece) -> None:
        for loc in piece.ctrl_locs:
            self.fboard[loc].discard(piece)

        piece.ctrl_locs.clear()
        piece.nmoves = 0

        if piece.captured:
            return

        if isinstance(piece, Pawn):
            self.calc_fboard_pawn(piece)
            return

        king = self.kings[piece.color]
        for loc in piece.gen_moves(self.board):
            if king.is_checked and not self.does_blocks_check(piece, loc):
                continue
            if piece is king and self.is_threatened(piece, loc):
                continue
            piece.ctrl_locs.append(loc)
            self.fboard[loc].add(piece)
            if not self.is_own(piece, loc):
                piece.nmoves += 1

    def list_moves(self, piece: Piece) -> list[int]:
        moves = []
        for move in piece.ctrl_locs:
            if isinstance(piece, Pawn) and not self.is_valid_pawn_move(piece, move):
                continue

            if not self.is_own(piece, move):
                moves.append(move)
        return moves

    def is_in_check(self, king: King) -> bool:
        cheked_by: list[Piece] = []
        for attacker in self.fboard[king.loc]:
            if attacker.color != king.color:
                if isinstance(attacker, Pawn) and self.is_adj_file(
                    king.loc, attacker.loc
                ):
                    cheked_by.append(attacker)
                else:
                    cheked_by.append(attacker)
        king.checked_by = cheked_by
        if len(cheked_by) > 0:
            return True
        return False

    def capture(self, piece: Piece) -> None:
        piece.captured = True
        self.board[piece.loc] = None
        self.pieces[piece.color].remove(piece)
        self.recalc_fboard(piece)

    def move_piece(self, piece: Piece, loc: int) -> None:
        target = self.board[loc]

        recalc_targets = {
            piece,
        }

        self.ep_candidate = None
        if isinstance(piece, Pawn):
            if self.is_adj_file(piece.loc, loc) and self.board[loc] is None:
                ep_loc = (loc & 56) | (piece.loc & 7)
                ep_candidate = self.board[ep_loc]
                if ep_candidate:
                    self.capture(ep_candidate)
                    recalc_targets.update(self.fboard[ep_loc])

            if abs(piece.loc - loc) == 2:
                self.ep_candidate = piece

        recalc_targets.update(self.fboard[loc])
        recalc_targets.update(self.fboard[piece.loc])

        if target is not None:
            self.capture(target)

        self.board[loc] = piece
        self.board[piece.loc] = None
        piece.move(loc)

        for p in recalc_targets:
            self.recalc_fboard(p)

        king = self.kings[not piece.color]
        if king.is_checked != self.is_in_check(king):
            king.is_checked = not king.is_checked
            for p in self.pieces[king.color]:
                self.recalc_fboard(p)

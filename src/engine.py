from typing import Optional

from .board import Board
from .piece import Piece, Type, Color


class Engine:
    def __init__(self, board: Board) -> None:
        self.board = board
        self.fboard: list[list[Piece]] = [[] for _ in range(self.board.get_size())]
        self.ep_candidate: Optional[Piece] = None

    def calc_fboard(self, piece: Piece) -> None:
        pass

    def nmoves(self, color: Color) -> int:
        return sum(p.nmoves for p in self.board.get_all_pieces(color))

    def is_threatened(self, piece: Piece, loc: int) -> bool:
        for attacker in self.fboard[loc]:
            if attacker.color != piece.color:
                if attacker.type == Type.PAWN:
                    return self.board.is_adj_file(attacker.loc, loc)
                else:
                    return True
        return False

    def is_valid_pawn_move(self, piece: Piece, loc: int) -> bool:
        if not self.board.is_adj_file(piece.loc, loc):
            return True

        if self.board.get_piece(loc) is not None:
            return True

        if self.ep_candidate is None or abs(piece.loc - self.ep_candidate.loc) != 8:
            return False

        if (loc >> 3) != (self.ep_candidate.loc >> 3):
            return False

        # Check whether ep_candidate is can be taken without check
        for p in self.fboard[self.ep_candidate.loc]:
            if p.color != self.ep_candidate.color:
                continue
            if not p.is_sliding:
                continue

            dir1 = p.is_in_dir(self.board.get_king(piece.color).loc)
            if dir1 is None:
                continue

            dir2 = p.is_in_dir(self.ep_candidate.loc)
            if dir2 is None:
                raise ValueError("Invalid State")

            if dir1 == dir2:
                return False

        return True

    def does_blocks_check(self, piece: Piece, loc: int) -> bool:
        king = self.board.get_king(piece.color)

        if not king.is_checked:
            return True

        if len(king.checked_by) != 1:
            return piece.type == Type.KING and not self.is_threatened(piece, loc)

        if piece.type == Type.KING:
            return not self.is_threatened(piece, loc)

        if piece.type == Type.PAWN and not self.is_valid_pawn_move(piece, loc):
            return False

        attacker = king.checked_by[0]
        if loc == attacker.loc:
            return True

        if loc not in attacker.ctrl_locs:
            return False

        df = (king.loc >> 3) - (attacker.loc >> 3)
        dr = (king.loc & 7) - (attacker.loc & 7)
        df_dest = (loc >> 3) - (attacker.loc >> 3)
        dr_dest = (loc & 7) - (attacker.loc & 7)

        if df * dr_dest != dr * df_dest:
            return False

        if df != 0:
            t = df_dest / df
        else:
            t = dr_dest / dr

        return 0 < t < 1

    def does_handle_pin(self, piece: Piece, loc: int) -> bool:
        if piece.type == Type.KING:
            return True

        if not piece.is_checked:
            return True

        dir = piece.checked_by[0].is_in_dir(piece.loc)

        if dir is None:
            return True

        inv_dir = (dir[0] * -1, dir[1] * -1)

        move_dir = piece.is_in_dir(loc)

        if move_dir is None:
            return False

        return move_dir == dir or move_dir == inv_dir


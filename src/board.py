from .piece import Piece, PIECE_MAP, King

from typing import Optional


def loc_to_notation(loc: int) -> str:
    file = loc >> 3
    rank = loc & 7
    return f"{chr(file + ord('a'))}{8 - rank}"


class Board:
    def __init__(self, fen: Optional[str] = None, turn: bool = False) -> None:
        self.board: list[list[Piece | None]] = [
            [None] * 8 for _ in range(8)
        ]  # 8x8 chess board initialized with zeros
        self.fboard: list[list[set[Piece]]] = [
            [set() for _ in range(8)] for _ in range(8)
        ]
        if fen:
            kings, pieces = self.load_fen(fen)
            self.turn = turn
        else:
            kings, pieces = self.setup_starting_position()
            self.turn = False  # White starts

        self.navl_moves: list[int] = [0, 0]
        self.pieces = pieces
        if kings[0].color:
            self.kings = [kings[1], kings[0]]
        else:
            self.kings = [kings[0], kings[1]]

        for rank in range(8):
            for file in range(8):
                piece = self.board[rank][file]
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
                    self.board[r][file] = piece
                    file += 1
        return kings, pieces

    def setup_starting_position(self) -> tuple[list[King], list[list[Piece]]]:
        return self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def does_blocks_check(self, piece: Piece, to_file: int, to_rank: int) -> bool:
        king = self.kings[piece.color]
        king_file, king_rank = king.loc >> 3, king.loc & 7

        if len(king.checked_by) != 1:
            return isinstance(piece, King)

        attacker = king.checked_by[0]
        attacker_file, attacker_rank = attacker.loc >> 3, attacker.loc & 7
        if (attacker_file, attacker_rank) == (to_file, to_rank):
            return True

        df = king_file - attacker_file
        dr = king_rank - attacker_rank
        df_dest = to_file - attacker_file
        dr_dest = to_rank - attacker_rank

        if df * dr_dest != dr * df_dest:
            return False

        if df != 0:
            t = df_dest / df
        else:
            t = dr_dest / dr

        return 0 < t < 1

    def is_own(self, piece: Piece, file: int, rank: int) -> bool:
        target = self.board[rank][file]
        return target is not None and target.color == piece.color

    def is_threatened(self, piece: Piece, file: int, rank: int) -> bool:
        for attacker in self.fboard[rank][file]:
            if attacker.color != piece.color:
                return True
        return False

    def recalc_fboard(self, piece: Piece) -> None:
        for loc in piece.ctrl_locs:
            file = loc >> 3
            rank = loc & 7
            self.fboard[rank][file].discard(piece)
        self.navl_moves[piece.color] -= piece.navl_moves
        piece.ctrl_locs.clear()
        if piece.captured:
            return
        king = self.kings[piece.color]
        count = 0
        for file, rank in piece.gen_moves(self.board):
            if king.is_checked and not self.does_blocks_check(piece, file, rank):
                continue
            if piece is king and self.is_threatened(piece, file, rank):
                continue
            piece.ctrl_locs.append((file << 3) | rank)
            self.fboard[rank][file].add(piece)
            if self.is_own(piece, file, rank):
                count += 1
        self.navl_moves[piece.color] += count
        piece.navl_moves = count

    def list_moves(self, piece: Piece) -> list[tuple[int, int]]:
        moves = []
        for move in piece.ctrl_locs:
            move_file = move >> 3
            move_rank = move & 7
            if not self.is_own(piece, move_file, move_rank):
                moves.append((move_file, move_rank))
        return moves

    def is_in_check(self, king: King) -> bool:
        king_file, king_rank = king.loc >> 3, king.loc & 7
        cheked_by: list[Piece] = []
        for attacker in self.fboard[king_rank][king_file]:
            if attacker.color != king.color:
                cheked_by.append(attacker)
        king.checked_by = cheked_by
        if len(cheked_by) > 0:
            return True
        return False

    def move_piece(self, piece: Piece, to_file: int, to_rank: int) -> None:
        from_file, from_rank = piece.loc >> 3, piece.loc & 7
        target = self.board[to_rank][to_file]

        self.board[to_rank][to_file] = piece
        piece.loc = (to_file << 3) | to_rank
        piece.has_moved = True
        self.board[from_rank][from_file] = None

        dst_ctrls = self.fboard[to_rank][to_file].copy()
        src_ctrls = self.fboard[from_rank][from_file].copy()

        self.recalc_fboard(piece)
        if target is not None:
            target.captured = True
            self.pieces[target.color].remove(target)
            self.recalc_fboard(target)
        for piece in dst_ctrls:
            self.recalc_fboard(piece)
        for piece in src_ctrls:
            self.recalc_fboard(piece)

        king = self.kings[not piece.color]
        if king.is_checked != self.is_in_check(king):
            king.is_checked = not king.is_checked
            for p in self.pieces[king.color]:
                self.recalc_fboard(p)

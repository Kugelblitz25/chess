from typing import Iterator, Optional

from .piece import Color, Piece, Type


class Board:
    def __init__(self, fen: Optional[str] = None, turn: bool = False) -> None:
        self.board: list[Piece | None] = [None] * 64
        self.fboard: list[list[Piece]] = [[] for _ in range(64)]
        self.ep_candidate: Optional[Piece] = None
        self.pinned: list[Piece] = []

        if fen:
            self.pieces = self.load_fen(fen)
            self.turn = turn
        else:
            self.pieces = self.setup_starting_position()
            self.turn = False  # White starts

        for loc in range(64):
            piece = self.board[loc]
            if piece is None:
                continue
            self.recalc_fboard(piece)

    def get_size(self) -> int:
        return len(self.board)

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

    def load_fen(self, fen: str) -> list[list[Piece]]:
        board_state = fen.split(" ")[0]
        rows = board_state.split("/")
        pieces: list[list[Piece]] = [[] for _ in range(2 * max(Type))]

        for r, row in enumerate(rows):
            file = 0
            for char in row:
                if char.isdigit():
                    file += int(char)
                else:
                    loc = (file << 3) | (7 - r)
                    piece = Piece.from_notation(char, loc)
                    pieces[piece.id].append(piece)
                    self.board[loc] = piece
                    file += 1
        return pieces

    def setup_starting_position(self) -> list[list[Piece]]:
        return self.load_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def nmoves(self, color: Color) -> int:
        return sum(p.nmoves for p in self.get_all_pieces(color))

    def is_adj_file(self, loc1: int, loc2: int) -> bool:
        return abs((loc1 >> 3) - (loc2 >> 3)) == 1

    def _is_ep_pseudopinned(self, p1: Piece, p2: Piece, king: Piece) -> bool:
        for p in self.fboard[p1.loc]:
            if p.color != p1.color:
                continue
            if not p.is_sliding:
                continue

            dir1 = p.is_in_dir(king.loc)
            if dir1 is None:
                continue

            dir2 = p.is_in_dir(p1.loc)
            if dir2 is None:
                raise ValueError("Invalid State")

            if dir1 != dir2:
                continue

            ppin = True
            for i in self.iterate_between(p1, king):
                target = self.board[i]
                if target is not None and target != p2:
                    ppin = False
                    break
            if ppin:
                return True
        return False

    def is_valid_pawn_move(self, piece: Piece, loc: int) -> bool:
        if not self.is_adj_file(piece.loc, loc):
            return True

        if self.board[loc] is not None:
            return True

        if self.ep_candidate is None or abs(piece.loc - self.ep_candidate.loc) != 8:
            return False

        if (loc >> 3) != (self.ep_candidate.loc >> 3):
            return False

        # Check whether ep_candidate is can be taken without check
        king = self.get_king(piece.color)
        if self._is_ep_pseudopinned(self.ep_candidate, piece, king):
            return False
        if self._is_ep_pseudopinned(piece, self.ep_candidate, king):
            return False
        return True

    def does_blocks_check(self, piece: Piece, loc: int) -> bool:
        king = self.get_king(piece.color)

        if not king.is_checked:
            return True

        if len(king.checked_by) != 1:
            return piece.type == Type.KING and not self.is_threatened(piece, loc)

        if piece.type == Type.KING:
            return not self.is_threatened(piece, loc)

        attacker = king.checked_by[0]
        if loc == attacker.loc:
            return True

        if loc not in attacker.ctrl_locs:
            return False

        check_dir = attacker.is_in_dir(king.loc)
        if check_dir is None:
            raise ValueError("Invalid State.")
        move_dir = attacker.is_in_dir(loc)
        if move_dir is None:
            raise ValueError("Invalid State.")

        if move_dir != check_dir:
            return False

        if check_dir[0] != 0:
            t = ((loc >> 3) - (attacker.loc >> 3)) / (
                (king.loc >> 3) - (attacker.loc >> 3)
            )
        else:
            t = ((loc & 7) - (attacker.loc & 7)) / ((king.loc & 7) - (attacker.loc & 7))

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

    def is_own(self, piece: Piece, loc: int) -> bool:
        target = self.board[loc]
        return target is not None and target.color == piece.color

    def is_threatened(self, piece: Piece, loc: int) -> bool:
        for attacker in self.fboard[loc]:
            if attacker.color != piece.color:
                if attacker.type == Type.PAWN:
                    return self.is_adj_file(attacker.loc, loc)
                else:
                    return True
        return False

    def iterate_between(self, src: Piece, dst: Piece) -> Iterator[int]:
        dir = src.is_in_dir(dst.loc)
        if dir is None:
            return

        df, dr = dir
        f, r = src.loc >> 3, src.loc & 7
        while True:
            f += df
            r += dr
            if not (0 <= f < 8 and 0 <= f < 8):
                break
            loc = (f << 3) | r
            if dst.loc == loc:
                break
            yield loc

    def is_pinning(self, piece: Piece) -> Optional[Piece]:
        other_king = self.get_king(piece.color.switch())
        pinned: Optional[Piece] = None
        for loc in self.iterate_between(piece, other_king):
            if self.is_own(other_king, loc):
                if pinned is None:
                    pinned = self.board[loc]
                else:
                    return None
        return pinned

    def clear_moves(self, piece: Piece) -> None:
        for loc in piece.ctrl_locs:
            self.fboard[loc].remove(piece)

        piece.ctrl_locs.clear()

    def attcks(self, piece: Piece, loc: int) -> None:
        self.fboard[loc].append(piece)
        if piece.type == Type.PAWN and not self.is_valid_pawn_move(piece, loc):
            return

        if not self.is_own(piece, loc):
            piece.ctrl_locs.append(loc)

    def recalc_fboard(self, piece: Piece) -> None:
        self.clear_moves(piece)
        if piece.captured:
            return

        for loc in piece.gen_moves(self.board):
            if not self.does_blocks_check(piece, loc):
                continue
            if not self.does_handle_pin(piece, loc):
                continue
            self.attcks(piece, loc)

        if piece.is_sliding:
            pinned = self.is_pinning(piece)
            if pinned is None:
                return None
            self.add_pin(piece, pinned)

    def list_moves(self, piece: Piece) -> list[int]:
        return piece.ctrl_locs

    def is_in_check(self, king: Piece) -> bool:
        cheked_by: list[Piece] = []
        for attacker in self.fboard[king.loc]:
            if attacker.color != king.color:
                if attacker.type == Type.PAWN and self.is_adj_file(
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
        self.pieces[piece.id].remove(piece)
        self.recalc_fboard(piece)

    def add_pin(self, piece: Piece, pinned: Piece) -> None:
        if pinned.is_checked:
            return None
        pinned.is_checked = True
        pinned.checked_by.append(piece)
        self.pinned.append(pinned)
        self.recalc_fboard(pinned)
        self.recalc_fboard(self.get_king(piece.color))

    def remove_pin(self, piece: Piece, pinned: Piece) -> None:
        pinned.is_checked = False
        pinned.checked_by = []
        self.pinned.remove(pinned)
        self.recalc_fboard(pinned)
        self.recalc_fboard(self.get_king(piece.color))

    def filter_pins(self) -> None:
        for piece in self.pinned[:]:
            if piece.checked_by[0].captured:
                self.remove_pin(piece.checked_by[0], piece)
            pinned = self.is_pinning(piece.checked_by[0])
            if piece.is_checked and not pinned:
                self.remove_pin(piece.checked_by[0], piece)

    def handle_ep(self, piece: Piece, loc: int) -> set[Piece]:
        self.ep_candidate = None
        if piece.type != Type.PAWN:
            return set()

        recalc_targets: set[Piece] = set()

        if self.is_adj_file(piece.loc, loc) and self.board[loc] is None:
            ep_loc = (loc & 56) | (piece.loc & 7)
            ep_candidate = self.board[ep_loc]
            if ep_candidate:
                self.capture(ep_candidate)
                recalc_targets.update(self.fboard[ep_loc])

        if abs(piece.loc - loc) == 2:
            self.ep_candidate = piece
            file, rank = loc >> 3, loc & 7
            if 0 <= file - 1:
                target = self.board[((file - 1) << 3) | rank]
                if target is not None and target.id == Type.PAWN | piece.color.switch():
                    recalc_targets.add(target)
            if file + 1 < 8:
                target = self.board[((file + 1) << 3) | rank]
                if target is not None and target.id == Type.PAWN | piece.color.switch():
                    recalc_targets.add(target)

        return recalc_targets

    def handle_castel(self, piece: Piece, loc: int) -> list[Piece]:
        if piece.type != Type.KING:
            return []

        return []

    def handle_checks(self) -> None:
        for king in [self.get_king(Color.WHITE), self.get_king(Color.BLACK)]:
            if king.is_checked != self.is_in_check(king):
                king.is_checked = not king.is_checked
                for p in self.get_all_pieces(king.color):
                    self.recalc_fboard(p)

    def move_piece(self, piece: Piece, loc: int) -> None:
        target = self.board[loc]

        recalc_targets = {
            piece,
        }

        recalc_targets.update(self.handle_ep(piece, loc))
        recalc_targets.update(self.handle_castel(piece, loc))
        recalc_targets.update(self.fboard[loc])
        recalc_targets.update(self.fboard[piece.loc])

        if target is not None:
            self.capture(target)

        self.board[loc] = piece
        self.board[piece.loc] = None
        piece.move(loc)

        for p in recalc_targets:
            self.recalc_fboard(p)

        self.handle_checks()
        self.filter_pins()

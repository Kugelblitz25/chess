from typing import Iterator, Optional

from .board import AttackBoard, Board
from .piece import Color, Piece, Type
from .square import Square


class Engine:
    def __init__(self, fen: Optional[str] = None) -> None:
        self.board = Board(64)
        self.fboard = AttackBoard(64)
        self.fen = fen or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.ep_candidate: Optional[Piece] = None
        self.pinned_or_checked: dict[Piece, list[Piece]] = {}

        self.load_fen(self.fen)

        for piece in self.board.get_all_pieces(Color.WHITE):
            self.update_fboard(piece)

        for piece in self.board.get_all_pieces(Color.BLACK):
            self.update_fboard(piece)

    def reset(self) -> None:
        Engine.__init__(self, self.fen)

    def load_fen(self, fen: str) -> None:
        board_state = fen.split(" ")[0]
        rows = board_state.split("/")

        for r, row in enumerate(rows):
            file = 0
            for char in row:
                if char.isdigit():
                    file += int(char)
                else:
                    loc = Square((file << 3) | (7 - r))
                    piece = Piece.from_notation(char, loc)
                    self.board.put_piece(piece, loc)
                    file += 1

    def get_piece(self, loc: Square) -> Optional[Piece]:
        return self.board.get_piece(loc)

    def get_board(self) -> Board:
        return self.board

    def nmoves(self, color: Color) -> int:
        return sum(p.nmoves for p in self.board.get_all_pieces(color))

    def _is_ep_pseudopinned(self, p1: Piece, p2: Piece, king: Piece) -> bool:
        for attacker in self.fboard.get_attackers(king.color.other, p1.loc):
            if not attacker.is_sliding:
                continue

            dir1 = attacker.is_in_dir(king.loc)
            if dir1 is None:
                continue

            dir2 = attacker.is_in_dir(p1.loc)
            if dir2 is None:
                raise ValueError("Invalid State")

            if dir1 != dir2:
                continue

            ppin = True
            for i in self.iterate_between(p1, king):
                target = self.board.get_piece(i)
                if target is not None and target != p2:
                    ppin = False
                    break
            if ppin:
                return True
        return False

    def is_valid_move(self, piece: Piece, loc: Square) -> bool:
        if piece.type != Type.PAWN:
            return not self.is_own(piece, loc)

        if not self.board.is_adj_file(piece.loc, loc):
            return self.board.is_empty(loc)

        if not self.board.is_empty(loc):
            return True

        if self.ep_candidate is None or abs(piece.loc - self.ep_candidate.loc) != 8:
            return False

        if loc.file != self.ep_candidate.loc.file:
            return False

        # Check whether ep_candidate is can be taken without check
        king = self.board.get_king(piece.color)
        if self._is_ep_pseudopinned(self.ep_candidate, piece, king):
            return False
        if self._is_ep_pseudopinned(piece, self.ep_candidate, king):
            return False
        return True

    def does_blocks_check(self, piece: Piece, loc: Square) -> bool:
        king = self.board.get_king(piece.color)

        if king not in self.pinned_or_checked:
            return True

        if len(self.pinned_or_checked[king]) != 1:
            return piece.type == Type.KING and not self.is_threatened(piece, loc)

        if piece.type == Type.KING:
            return not self.is_threatened(piece, loc)

        attacker = self.pinned_or_checked[king][0]
        if loc == attacker.loc:
            return True

        if not attacker.is_sliding:
            # Only way to escape from a check with non sliding piece is to either move the king or capture the attacker
            return False

        if (attacker.ctrls & (1 << loc)) == 0:
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
            t = (loc.file - attacker.loc.file) / (king.loc.file - attacker.loc.file)
        else:
            t = (loc.rank - attacker.loc.rank) / (king.loc.rank - attacker.loc.rank)

        return 0 < t < 1

    def does_handle_pin(self, piece: Piece, loc: Square) -> bool:
        if piece.type == Type.KING:
            return True

        if piece not in self.pinned_or_checked:
            return True

        dir = self.pinned_or_checked[piece][0].is_in_dir(piece.loc)

        if dir is None:
            return True

        inv_dir = (dir[0] * -1, dir[1] * -1)

        move_dir = piece.is_in_dir(loc)

        if move_dir is None:
            return False

        return move_dir == dir or move_dir == inv_dir

    def is_own(self, piece: Piece, loc: Square) -> bool:
        target = self.board.get_piece(loc)
        return target is not None and target.color == piece.color

    def is_threatened(self, piece: Piece, loc: Square) -> bool:
        for attacker in self.fboard.get_attackers(piece.color.other, loc):
            if attacker.type == Type.PAWN:
                if self.board.is_adj_file(attacker.loc, loc):
                    return True
            else:
                return True
        return False

    def iterate_between(self, src: Piece, dst: Piece) -> Iterator[Square]:
        dir = src.is_in_dir(dst.loc)
        if dir is None:
            return

        df, dr = dir
        sq: Square = src.loc
        while (next_sq := sq.move_dir(df, dr)) is not None and next_sq != dst.loc:
            yield next_sq
            sq = next_sq

    def is_pinning(self, piece: Piece) -> Optional[Piece]:
        other_king = self.board.get_king(piece.color.other)
        pinned: Optional[Piece] = None
        for loc in self.iterate_between(piece, other_king):
            if self.is_own(other_king, loc):
                if pinned is None:
                    pinned = self.board.get_piece(loc)
                else:
                    return None
        return pinned

    def update_fboard(self, piece: Piece) -> None:
        self.fboard.remove_attacker(piece)
        piece.moves = 0
        piece.ctrls = 0

        if piece.captured:
            return

        generator = piece.gen_moves()

        for loc in generator:
            if not self.does_blocks_check(piece, loc):
                continue
            if not self.does_handle_pin(piece, loc):
                continue
            piece.ctrls ^= 1 << loc
            if self.is_valid_move(piece, loc):
                piece.moves ^= 1 << loc

            if piece.is_sliding and not self.board.is_empty(loc):
                try:
                    generator.send(True)
                except StopIteration:
                    pass

        self.fboard.add_attacker(piece)

        if piece.is_sliding:
            pinned = self.is_pinning(piece)
            if pinned is None:
                return None
            self.add_pin(piece, pinned)

    def list_moves(self, piece: Piece) -> list[Square]:
        return list(Piece.bb_to_loc(piece.moves))

    def is_in_check(self, color: Color) -> bool:
        cheked_by: list[Piece] = []
        king = self.board.get_king(color)
        for attacker in self.fboard.get_attackers(king.color.other, king.loc):
            if attacker.type == Type.PAWN:
                if self.board.is_adj_file(king.loc, attacker.loc):
                    cheked_by.append(attacker)
            else:
                cheked_by.append(attacker)
        if len(cheked_by) > 0:
            self.pinned_or_checked[king] = cheked_by
            return True
        else:
            self.pinned_or_checked.pop(king, None)
            return False

    def add_pin(self, piece: Piece, pinned: Piece) -> None:
        if pinned in self.pinned_or_checked:
            return
        self.pinned_or_checked[pinned] = [piece]
        self.update_fboard(pinned)
        self.update_fboard(self.board.get_king(piece.color))

    def remove_pin(self, piece: Piece, pinned: Piece) -> None:
        self.pinned_or_checked.pop(pinned, None)
        self.update_fboard(pinned)
        self.update_fboard(self.board.get_king(piece.color))

    def filter_pins(self) -> None:
        to_be_removed: list[tuple[Piece, Piece]] = []
        for piece, checked_by in self.pinned_or_checked.items():
            if piece.type == Type.KING:
                continue
            if checked_by[0].captured:
                to_be_removed.append((checked_by[0], piece))
                continue
            pinned = self.is_pinning(checked_by[0])
            if not pinned:
                to_be_removed.append((checked_by[0], piece))
        for p1, p2 in to_be_removed:
            self.remove_pin(p1, p2)

    def handle_pawn_move(self, piece: Piece, loc: Square) -> set[Piece]:
        self.ep_candidate = None
        if piece.type != Type.PAWN:
            return set()

        recalc_targets: set[Piece] = set()

        if self.board.is_adj_file(piece.loc, loc) and self.board.is_empty(loc):
            ep_sq = Square.from_coords(loc.file, piece.loc.rank)
            if ep_sq is not None:
                ep_candidate = self.board.get_piece(ep_sq)
                if ep_candidate:
                    self.board.capture(ep_candidate)
                    recalc_targets.add(ep_candidate)
                    recalc_targets.update(self.fboard.get_pattackers(ep_sq))

        if abs(piece.loc - loc) == 2:
            self.ep_candidate = piece
            for df in (-1, 1):
                adj = Square.from_coords(loc.file + df, loc.rank)
                if adj is not None:
                    target = self.board.get_piece(adj)
                    if target is not None and target.id == Type.PAWN | piece.color.other:
                        recalc_targets.add(target)

        return recalc_targets

    def handle_castle(self, piece: Piece, loc: Square) -> list[Piece]:
        if piece.type != Type.KING:
            return []

        return []

    def handle_checks(self) -> None:
        for color in Color:
            king = self.board.get_king(color)
            is_checked = king in self.pinned_or_checked
            if is_checked != self.is_in_check(color):
                for p in self.board.get_all_pieces(color):
                    self.update_fboard(p)

    def move_piece(self, piece: Piece, loc: Square) -> None:
        target = self.board.get_piece(loc)

        recalc_targets = {
            piece,
        }

        recalc_targets.update(self.handle_pawn_move(piece, loc))
        recalc_targets.update(self.handle_castle(piece, loc))
        recalc_targets.update(self.fboard.get_pattackers(loc))
        recalc_targets.update(self.fboard.get_pattackers(piece.loc))

        if target is not None:
            self.board.capture(target)
            recalc_targets.add(target)

        self.board.move_piece(piece, loc)

        for p in recalc_targets:
            self.update_fboard(p)

        self.handle_checks()
        self.filter_pins()

from typing import Optional


class Square(int):
    """Board square encoded as ``(file << 3) | rank``.

    file ∈ [0, 7]  →  a–h
    rank ∈ [0, 7]  →  1–8
    value ∈ [0, 63]
    """

    __slots__ = ()

    def __new__(cls, value: int) -> "Square":
        if not (0 <= value < 64):
            raise ValueError(f"Square value must be in [0, 63], got {value}")
        return super().__new__(cls, value)

    @property
    def file(self) -> int:
        return self >> 3

    @property
    def rank(self) -> int:
        return self & 7

    @classmethod
    def from_coords(cls, file: int, rank: int) -> Optional["Square"]:
        if not (0 <= file < 8 and 0 <= rank < 8):
            return None
        return cls((file << 3) | rank)

    @classmethod
    def from_notation(cls, notation: str) -> "Square":
        """Parse a square from algebraic notation, e.g. ``'e4'``."""
        if (
            len(notation) != 2
            or notation[0].lower() not in "abcdefgh"
            or notation[1] not in "12345678"
        ):
            raise ValueError(f"Invalid square notation: {notation!r}")
        file = ord(notation[0].lower()) - ord("a")
        rank = int(notation[1]) - 1
        sq = cls.from_coords(file, rank)
        assert sq is not None
        return sq

    def is_adj_file(self, other: "Square") -> bool:
        return abs(self.file - other.file) == 1
    
    def move_dir(self, df: int, dr: int) -> Optional["Square"]:
        return self.from_coords(self.file + df, self.rank + dr)

    def __str__(self) -> str:
        return f"{chr(self.file + ord('a'))}{self.rank + 1}"

    def __repr__(self) -> str:
        return f"Square('{self}')"

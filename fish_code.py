from __future__ import annotations
from collections import defaultdict

from typing import Tuple, Union
Coord = Tuple[Union[int, float], Union[int, float]]
Value = Union[str, float, int]



class FishCode:
    '''
    Codebox represented as a dict with (col: int, row: int) keys.
    '''


    def __init__(self, src: str = '', **flags) -> None:
        self.FLAGS = flags
        self.code = defaultdict(int)
        self.min_row = self.max_row = self.min_col = self.max_col = 0
        for r, line in enumerate(src.split('\n')):
            if r > self.max_row: self.max_row = r
            for c, char in enumerate(line):
                if c > self.max_col: self.max_col = c
                self.code[c,r] = ord(char)


    def wrap(self, v: int) -> int:
        return v % 65536


    def parse_value(self, val: Value) -> int:
        if isinstance(val, str):
            if len(val) != 1:
                raise Exception('Codebox values must be one char only.')
            return ord(val)
        elif isinstance(val, (float, int)):
            return round(val) if self.FLAGS['ROUND_VALUES'] else int(val)
        else:
            raise Exception('Codebox values must be a char or a real number.')


    def parse_coord(self, p: Coord) -> Tuple[int, int]:
        col, row = p
        return self.parse_value(col), self.parse_value(row)


    def bounding_box_contains(self, p: Coord) -> bool:
        col, row = self.parse_coord(p)
        return self.min_col <= col <= self.max_col and self.min_row <= row <= self.max_row


    def __repr__(self) -> str:
        text = '\n'
        for r in range(self.min_row, self.max_row + 1):
            for c in range(self.min_col, self.max_col + 1):
                char = self.get_char(c, r)
                text += char if char.isprintable() else ' '
            text += '\n'
        return text


    def get_char(self, index: Coord) -> str:
        return chr(self.wrap(self.code[self.parse_coord(index)]))


    def __getitem__(self, index: Coord) -> int:
        return self.code[self.parse_coord(index)]


    def __setitem__(self, index: Coord, val: Value) -> None:
        self.code[self.parse_coord(index)] = self.parse_value(val)


    def __contains__(self, item: Value) -> bool:
        return self.parse_value(item) in self.code.values()
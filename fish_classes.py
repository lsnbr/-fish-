from __future__ import annotations
from collections import defaultdict

from typing import Tuple, Union, Iterable, Optional, List
Coord = Tuple[Union[int, float], Union[int, float]]
Value = Union[str, float, int]
Input = Optional[Union[str, Iterable[Union[int, float]]]]




class FishError(Exception):
    def __init__(self, message):
        super().__init__('something smells fishy...' + '\n' + message)

class FishEndExecution(Exception):
    pass



class FishCode:
    '''Codebox represented as a dict with (col: int, row: int) keys.'''

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
                char = self.get_char((c, r))
                text += char if char.isprintable() else ' '
            text += '\n'
        return text


    def parse_char(self, n: Value) -> str:
        return chr(self.wrap(self.parse_value(n)))

    def get_char(self, index: Coord) -> str:
        return self.parse_char(self.code[self.parse_coord(index)])

    def __getitem__(self, index: Coord) -> int:
        return self.code[self.parse_coord(index)]

    def __setitem__(self, index: Coord, val: Value) -> None:
        col, row = self.parse_coord(index)
        self.code[col, row] = self.parse_value(val)
        if col < self.min_col: self.min_col = col
        elif col > self.max_col: self.max_col = col
        if row < self.min_row: self.min_row = row
        elif row > self.max_row: self.max_row = row

    def __contains__(self, item: Value) -> bool:
        val = self.parse_value(item)
        return val == 0 or val in self.code.values()




class FishStack:
    '''Represents a stack of stacks.'''

    def __init__(self, prefill: Union[str, Iterable[float]] = None) -> None:
        self.stack = []
        self.add_stack(prefill)


    @property
    def length(self) -> int:
        return len(self.stack[-1])

    @property
    def stack_count(self) -> int:
        return len(self.stack)


    def parse_input(self, inp: Input) -> List[Union[int, float]]:
        if inp is None:
            return []
        if isinstance(inp, str):
            return [ord(c) for c in inp]
        return list(inp)
        
    def add_stack(self, fill: Input = None) -> None:
        self.stack.append([])
        self.push(as_iter=self.parse_input(fill))

    def del_stack(self) -> Tuple[float, ...]:
        popped = self.pop()
        if self.stack_count > 1:
            self.stack.pop()
        return popped
        

    def push(self, *vals: float, as_iter: Iterable[float] = ()) -> None:
        items = [v if v%1 else int(v) for v in vals + tuple(as_iter)]
        self.stack[-1].extend(items)

    def pop(self, n: int = None) -> Tuple[float, ...]:
        n = self.length if n is None else max(0, n)
        if n > self.length:
            raise FishError(f'Not enough values to pop: {self.length} values on the stack, tried to pop {n}.')
        popped = tuple(self.stack[-1][-n:]) if n else ()
        self.stack[-1][-n:] = []
        return popped
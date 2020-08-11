from fish_classes import FishCode, FishStack, FishError, FishEndExecution

import operator as op
from random import randint
from string import hexdigits

from typing import Iterable, Tuple, Optional, Union
Input = Optional[Union[str, Iterable[Union[int, float]]]]



class Fish:
    '''
    Interprets a ><> (fish) program, initialized with its source code as a string.

    Can be called with initial stack and input, returning the output if terminating.
    Can also be initialized with stack and input first, and then advancing the program manually.
    '''

    VALID_CHARS  = '><^v/\\|_#x!?.+-*,%=)(\'":~$@}{rl[]oni&gp; \x00' + hexdigits[:16]
    R_FORWARD    = {'right': 'up',    'left': 'down',  'down': 'left',  'up': 'right'}
    R_BACKWARD   = {'right': 'down',  'left': 'up',    'down': 'right', 'up': 'left'}
    R_HORIZONTAL = {'right': 'right', 'left': 'left',  'down': 'up',    'up': 'down'}
    R_VERTICAL   = {'right': 'left',  'left': 'right', 'down': 'down',  'up': 'up'}
    R_CROSS      = {'right': 'left',  'left': 'right', 'down': 'up',    'up': 'down'}
    DIRECTIONS   = ('right',          'left',          'down',          'up')
    OPERATORS    = {'+': op.add, '-': op.sub, '*': op.mul, ',': op.truediv, '%': op.mod}


    def __init__(self, code: str = ';', **flags: bool) -> None:
        self.src_string = code
        self.FLAGS = flags
        if 'ARBITRARY_JUMP'  not in self.FLAGS: self.FLAGS['ARBITRARY_JUMP']  = False
        if 'EXACT_FRACTIONS' not in self.FLAGS: self.FLAGS['EXACT_FRACTIONS'] = False
        if 'ROUND_VALUES'    not in self.FLAGS: self.FLAGS['ROUND_VALUES']    = True
        self.COMMANDS = {
            '>': self.right,      '<': self.left,         '^': self.up,
            'v': self.down,       '/': self.m_forward,    '\\':self.m_backward,
            '|': self.m_vertical, '_': self.m_horizontal, '#': self.m_cross,
            'x': self.m_random,   '!': self.tramp,        '?': self.tramp_cond,
            '.': self.jump,       '=': self.equals,       ')': self.greater,
            '(': self.smaller,    "'": self.single_quote, '"': self.double_quote,
            ':': self.duplicate,  '~': self.remove,       '$': self.swap2,
            '@': self.swap3,      '}': self.shiftr,       '{': self.shiftl,
            'r': self.reverse,    'l': self.length,       '[': self.new_stack,
            ']': self.del_stack,  'o': self.out_char,     'n': self.out_num,
            'i': self.read_char,  '&': self.do_register,  'g': self.get_code,
            'p': self.set_code,   ';': self.end,
            **{c: lambda: None    for c in '\x00' + ' '},    # no-op commands
            **{c: self.literal    for c in hexdigits[:16]},  # commands 0-9 and a-f
            **{c: self.arithmetic for c in '+-*,%'},         # commands + - * , %
        }

    
    # commands
    def right(self) -> None:
        self.direction = 'right'
    def left(self) -> None:
        self.direction = 'left'
    def down(self) -> None:
        self.direction = 'down'
    def up(self) -> None:
        self.direction = 'up'
    def m_forward(self) -> None:
        self.direction = Fish.R_FORWARD[self.direction]
    def m_backward(self) -> None:
        self.direction = Fish.R_BACKWARD[self.direction]
    def m_horizontal(self) -> None:
        self.direction = Fish.R_HORIZONTAL[self.direction]
    def m_vertical(self) -> None:
        self.direction = Fish.R_VERTICAL[self.direction]
    def m_cross(self) -> None:
        self.direction = Fish.R_CROSS[self.direction]
    def m_random(self) -> None:
        self.direction = Fish.DIRECTIONS[randint(0, 3)]
    def tramp(self) -> None:
        self.skip = True
    def tramp_cond(self) -> None:
        self.skip = self.stack.pop(1)[0] == 0
    def jump(self) -> None:
        self.pos = self.code.parse_coord(self.stack.pop(2))
    def literal(self) -> None:
        self.stack.push(int(self.code.get_char(self.pos), base=16))
    def arithmetic(self) -> None:
        try:
            self.stack.push(Fish.OPERATORS[self.code.get_char(self.pos)](*self.stack.pop(2)))
        except ZeroDivisionError:
            raise FishError('Division by zero is not allowed.')
    def equals(self) -> None:
        self.stack.push(int(op.eq(*self.stack.pop(2))))
    def greater(self) -> None:
        self.stack.push(int(op.gt(*self.stack.pop(2))))
    def smaller(self) -> None:
        self.stack.push(int(op.lt(*self.stack.pop(2))))
    def single_quote(self) -> None:
        self.parse_mode = "'" if self.parse_mode is None else None
    def double_quote(self) -> None:
        self.parse_mode = '"' if self.parse_mode is None else None
    def duplicate(self) -> None:
        self.stack.push(as_iter=(2 * self.stack.pop(1)))
    def remove(self) -> None:
        self.stack.pop(1)
    def swap2(self) -> None:
        self.stack.push(as_iter=reversed(self.stack.pop(2)))
    def swap3(self) -> None:
        x, y, z = self.stack.pop(3)
        self.stack.push(z, x, y)
    def shiftr(self) -> None:
        if self.stack.length > 1:
            *x, y = self.stack.pop()
            self.stack.push(y, *x)
    def shiftl(self) -> None:
        if self.stack.length > 1:
            x, *y = self.stack.pop()
            self.stack.push(*y, x)
    def reverse(self) -> None:
        self.stack.push(as_iter=reversed(self.stack.pop()))
    def length(self) -> None:
        self.stack.push(self.stack.length)
    def new_stack(self) -> None:
        x = self.stack.pop(self.stack.pop(1)[0])
        self.stack.add_stack(x)
        self.register.append(None)
    def del_stack(self) -> None:
        if self.stack.stack_count > 1:
            x = self.stack.del_stack()
            self.stack.push(*x)
            self.register.pop()
        else:
            self.stack.del_stack()
            self.register = [None]
    def out_char(self) -> None:
        self.fish_out += self.code.parse_char(self.stack.pop(1)[0])
    def out_num(self) -> None:
        self.fish_out += str(self.stack.pop(1)[0])
    def read_char(self) -> None:
        self.stack.push(self.fish_in.pop() if self.fish_in else -1)
    def do_register(self) -> None:
        if self.register[-1] is None:
            self.register[-1] = self.stack.pop(1)[0]
        else:
            self.stack.push(self.register[-1]) 
            self.register[-1] = None
    def get_code(self) -> None:
        self.stack.push(self.code[self.stack.pop(2)])
    def set_code(self) -> None:
        v, *coord = self.stack.pop(3)
        self.code[coord] = v
    def end(self) -> None:
        self.is_running = False


    def initialize(self, inp: Input = None, stack: Input = None) -> None:
        self.code = FishCode(self.src_string, **self.FLAGS)
        self.stack = FishStack(stack)
        self.register = [None]
        self.fish_in = self.stack.parse_input(inp)
        self.fish_in = self.fish_in[::-1]
        self.fish_out = ''

        self.initialized = True
        self.pos = (0, 0)
        self.direction = 'right'
        self.parse_mode = None
        self.is_running = True
        self.skip = False

    def reset(self) -> None:
        self.initialized = False


    def next_cycle(self) -> None:
        if not self.initialized:
            raise Exception('Fish object must be initialized first.')

        cmd = self.code.get_char(self.pos)
        if self.parse_mode is not None and self.parse_mode != cmd:
            self.stack.push(ord(cmd))
        else:
            if cmd not in Fish.VALID_CHARS:
                raise FishError(f'Invalid command: {cmd}, ord={ord(cmd)}.')
            self.COMMANDS[cmd]()
        if not self.is_running: raise FishEndExecution()
        
        d = (1 + int(self.skip)) * (-1 if self.direction in ('left', 'up') else 1)
        col, row = self.pos
        self.skip = False
        self.pos = (
            (col + d) % (self.code.max_col + 1) if self.direction in {'right', 'left'} else col,
            (row + d) % (self.code.max_row + 1) if self.direction in {'up',    'down'} else row 
        )


    def __call__(self, inp: Input = None, stack: Input = None) -> str:
        self.initialize(inp, stack)
        while True:
            try:                     self.next_cycle()
            except FishEndExecution: return self.fish_out

    
    def __repr__(self) -> str:
        if hasattr(self, 'code'):
            return repr(self.code)
        return repr(FishCode(self.src_string, **self.FLAGS))

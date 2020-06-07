from fish_code import FishCode

from random import randint
import operator as op
from string import hexdigits


class FishError(Exception):
    def __init__(self, message):
        super().__init__('something smells fishy...')

class Fish:
    '''
    Interprets a ><> (fish) program

    ><> (fish) is a 2-D language where every char is an instruction
    The IP (instruction pointer) starts at (0,0) and moves to the right
    There are 1 or more stacks, each with a register to store a value
    Coordinates are always given as (column, row)

    Instructions:
    ---------------
    > < v ^     Change the IP direction to right/left/down/up respectively
    / \ | _ #   Mirrors: change the IP direction depending on its current direction
    x           Random direction
    !           Trampoline: skip the following instruction
    ?           Conditional trampoline: pop x of the stack. Skip the following instruction if x=0
    .           Jump: pop x, y of the stack. Jump to posintion (x,y) in the codebox
    0-9 a-f     Push the corresponding value onto the stack. a=10, ..., f=15
    + - * , %   Addition, subtraction, multiplication, float division and modulo:
                pop x, y of the stack and push x operator y to the stack
    =           Equals: pop x, y of the stack and push 1 if x=y and 0 otherwise
    ) (         Greater than, less than: pop x, y of the stack and push 1 if x operator y
                and 0 otherwise
    ' "         String parsing: pushes every character to the stack until it finds a closing quote
    :           Duplicate the top value on the stack
    ~           Remove the top value from the stack
    $           Swap the top two values on the stack
    @           Swap the top three values on the stack, shifting them rightwards,
                e.g.:  1,2,3,4  --- @ -->  1,4,2,3
    } {         Shift the entire stack to the right and left, respectively,
                e.g.:  1,2,3,4  --- } -->  4,1,2,3  and  1,2,3,4  --- { -->  2,3,4,1
    r           Reverse the stack
    l           Push the length of the stack onto the stack
    [           Pop x off the stack and create a new stack,
                moving x values from the old stack onto the new one
    ]           Remove the current stack, moving its values to the top of the underlying stack
                If the current stack is the last stack, the stack and registry just get emptied
    o n         Pop and output as a character and a number, respectively
    i           Read one character and push it to the stack. Push -1 if no input is available
    &           Pop the top value of the stack and put it in the register.
                Calling & again will take the value in the register and put it back on the stack
    g           Pop x, y of the stack and push the value at position (x,y) in the codebox.
                Empty cells (' ') are equal to 0
    p           Pop v, x, y of the stack, and change the value at position (x,y) to v,
                e.g.:  123p  puts 1 at (2,3) in the codebox
    ;           End execution
    '''

    VALID_CHARS = '> < ^ v / \\ | _ # x ! ? . + - * , % = ) ('.split() + \
                  '\' " : ~ $ @ } { r l [ ] o n i & g p ;'.split() + \
                  [' '] + list(hexdigits[:16])
    R_FORWARD    = {'right': 'up',    'left': 'down',  'down': 'left',  'up': 'right'}
    R_BACKWARD   = {'right': 'down',  'left': 'up',    'down': 'right', 'up': 'left'}
    R_HORIZONTAL = {'right': 'right', 'left': 'left',  'down': 'up',    'up': 'down'}
    R_VERTICAL   = {'right': 'left',  'left': 'right', 'down': 'down',  'up': 'up'}
    R_CROSS      = {'right': 'left',  'left': 'right', 'down': 'up',    'up': 'down'}
    DIRECTIONS   = ('right',          'left',          'down',          'up')
    OPERATORS    = {'+': op.add, '-': op.sub, '*': op.mul, ',': op.truediv, '%': op.mod}


    def __init__(self, code: str = ';'):
        self.code = FishCode(code)
        self.stack = [[]]
        self.pos = (0,0)
        self.direction = 'right'
        self.parse_mode = None
        self.skip = False
        self.is_running = False
        self.register = [None]
        self.stdout = ''
        self.stdin = []
        self.COMMANDS = {
            '>': self.right,      '<': self.left,         '^': self.up
           ,'v': self.down,       '/': self.m_forward,    '\\':self.m_backward
           ,'|': self.m_vertical, '_': self.m_horizontal, '#': self.m_cross
           ,'x': self.m_random,   '!': self.tramp,        '?': self.tramp_cond
           ,'.': self.jump,       '=': self.equals,       ')': self.greater
           ,'(': self.smaller,    "'": self.single_quote, '"': self.double_quote
           ,':': self.duplicate,  '~': self.remove,       '$': self.swap2
           ,'@': self.swap3,      '}': self.shiftr,       '{': self.shiftl
           ,'r': self.reverse,    'l': self.length,       '[': self.new_stack
           ,']': self.del_stack,  'o': self.out_char,     'n': self.out_num
           ,'i': self.read_char,  '&': self.do_register,  'g': self.get_code
           ,'p': self.set_code,   ';': self.end,          ' ': lambda: None
           ,**{c: self.literal for c in hexdigits[:16]}   # commands 0-9 and a-f
           ,**{o: self.arithmetic for o in '+-*,%'}       # commands + - * , %
           }

    @property
    def len_stack(self) -> int:
        return len(self.stack[-1])
    @property
    def stack_count(self) -> int:
        return len(self.stack)
    @property
    def current_cmd(self) -> str:
        return self.code[self.pos]

    def pop(self, n: float = None) -> (float):
        '''
        Pops round(n) values from the top of the stack as a tuple

        if the stack is [a,b,c,d,e], pop(2) returns (d,e)
        without argument all values get popped
        with n <= 0.5 an empty tuple is returned
        if n is more than the stack length, an error gets raised
        '''
        if n is None: n = self.len_stack
        n = max(0, round(n))
        if n > self.len_stack:
            raise FishError('not enough values to pop')
        popped = tuple(self.stack[-1][-n:]) if n > 0 else ()
        self.stack[-1][-n:] = []
        return popped

    def push(self, *vals: float, as_iter: [float] = ()) -> None:
        '''pushes vals + as_iter to the stack, e.g [a,b] -> push(x,y, as_iter=(8,8)) -> [a,b,x,y,8,8]'''
        items = vals + tuple(as_iter)
        for val in items:
            self.stack[-1].append(val)
    
    # commands
    def right(self):
        self.direction = 'right'
    def left(self):
        self.direction = 'left'
    def down(self):
        self.direction = 'down'
    def up(self):
        self.direction = 'up'
    def m_forward(self):
        self.direction = Fish.R_FORWARD[self.direction]
    def m_backward(self):
        self.direction = Fish.R_BACKWARD[self.direction]
    def m_horizontal(self):
        self.direction = Fish.R_HORIZONTAL[self.direction]
    def m_vertical(self):
        self.direction = Fish.R_VERTICAL[self.direction]
    def m_cross(self):
        self.direction = Fish.R_CROSS[self.direction]
    def m_random(self):
        self.direction = Fish.DIRECTIONS[randint(0, 3)]
    def tramp(self):
        self.skip = True
    def tramp_cond(self):
        self.skip = not bool(self.pop(1)[0])
    def jump(self):
        self.pos = self.pop(2)
    def literal(self):
        self.push(int(self.current_cmd, base=16))
    def arithmetic(self):
        try: self.push(Fish.OPERATORS[self.current_cmd](*self.pop(2)))
        except ZeroDivisionError: raise FishError('zero division is not allowed')
    def equals(self):
        self.push(int(op.eq(*self.pop(2))))
    def greater(self):
        self.push(int(op.gt(*self.pop(2))))
    def smaller(self):
        self.push(int(op.lt(*self.pop(2))))
    def single_quote(self):
        self.parse_mode = "'" if self.parse_mode is None else None
    def double_quote(self):
        self.parse_mode = '"' if self.parse_mode is None else None
    def duplicate(self):
        self.push(as_iter=(2 * self.pop(1)))
    def remove(self):
        self.pop(1)
    def swap2(self):
        self.push(as_iter=reversed(self.pop(2)))
    def swap3(self):
        x, y, z = self.pop(3)
        self.push(z, x, y)
    def shiftr(self):
        if self.len_stack > 1:
            *x, y = self.pop()
            self.push(y, *x)
    def shiftl(self):
        if self.len_stack > 1:
            x, *y = self.pop()
            self.push(*y, x)
    def reverse(self):
        self.push(as_iter=reversed(self.pop()))
    def length(self):
        self.push(self.len_stack)
    def new_stack(self):
        x = self.pop(self.pop(1)[0])
        self.stack.append(list(x))
        self.register.append(None)
    def del_stack(self):
        x = self.pop()
        if self.stack_count > 1:
            self.stack.pop()
            self.push(as_iter=x)
            self.register.pop()
        else: self.register[-1] = None
    def out_char(self):
        self.stdout += chr(round(self.pop(1)[0]))
    def out_num(self):
        self.stdout += str(self.pop(1)[0])
    def read_char(self):
        self.push(self.stdin.pop() if self.stdin else -1)
    def do_register(self):
        if self.register[-1] is None:
            self.register[-1] = self.pop(1)[0]
        else:
            self.push(self.register[-1]) 
            self.register[-1] = None
    def get_code(self):
        val = self.code[self.pop(2)]
        self.push(0 if val == ' ' else ord(val))
    def set_code(self):
        v, *coord = self.pop(3)
        self.code[coord] = chr(round(v))
    def end(self):
        self.is_running = False



    def run(self, new_input: str = '') -> str:
        self.stdin = list(map(ord, new_input))[::-1]
        self.is_running = True

        while True:
            cmd = self.current_cmd
            if self.parse_mode is not None and self.parse_mode != cmd:
                self.push(ord(cmd))
            else:
                if cmd not in self.VALID_CHARS:
                    raise FishError('invalid command')
                self.COMMANDS[cmd]()
            if not self.is_running: break

            d = (1 + int(self.skip)) * (-1 if self.direction in {'left', 'up'} else 1)
            col, row = self.pos
            self.skip = False
            self.pos = ((col + d) % self.code.cols if self.direction in {'right', 'left'} else col
                       ,(row + d) % self.code.rows if self.direction in {'up', 'down'} else row)

        return self.stdout


    def __call__(self, new_input: str = '') -> str:
        return self.run(new_input)

    def __str__(self):
        return str(self.code)







#### tests ####

from various_fishes import *

#print(Fish.__doc__)
#hello = Fish(bf)
#print(hello)
#print(hello.code.cols, hello.code.rows)
#res = hello('+' * 97 + '...')
#print(repr(res))
#print(*map(ord, res))
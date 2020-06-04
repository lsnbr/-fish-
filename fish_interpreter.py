from fish_code import FishCode

from random import randint
import operator as op
from string import hexdigits


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
    .           Jump: pop y and x of the stack. Jump to posintion (x,y) in the codebox
    0-9 a-f     Push the corresponding value onto the stack. a=10, ..., f=15
    + - * , %   Addition, subtraction, multiplication, float division and modulo:
                pop x, y of the stack and push x operator y to the stack
    =           Equals: pop x and y of the stack and push 1 if x=y and 0 otherwise
    ) (         Greater than, less than: pop x and y of the stack and push 1 if y operator x
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
    o n         Pop and output as a character and a number, respectively
    i           Read one character and push it to the stack. Push -1 if no input is available
    &           Pop the top value of the stack and put it in the register.
                Calling & again will take the value in the register and put it back on the stack
    g           Pop y and x of the stack and push the value at position (x,y) in the codebox.
                Empty cells are equal to 0
    p           Pop y,x and v of the stack, and change the value at position (x,y) to v,
                e.g.:  123p  puts 1 at (2,3) in the codebox
    ;           End execution
    '''
    VALID_CHARS = '> < ^ v / \\ | _ # x ! ? . + - * , % = ) ( \' " : ~ $ @ } { r l [ ] o n i & g p ;'.split() \
                + list(hexdigits[:16]) + [' ']
    R_FORWARD    = {'right': 'up',    'left': 'down',  'down': 'left',  'up': 'right'}
    R_BACKWARD   = {'right': 'down',  'left': 'up',    'down': 'right', 'up': 'left'}
    R_HORIZONTAL = {'right': 'right', 'left': 'left',  'down': 'up',    'up': 'down'}
    R_VERTICAL   = {'right': 'left',  'left': 'right', 'down': 'down',  'up': 'up'}
    R_CROSS      = {'right': 'left',  'left': 'right', 'down': 'up',    'up': 'down'}
    DIRECTIONS   = ('right',          'left',          'down',          'up')
    OPERATORS    = {'+': op.add, '-': op.sub, '*': op.mul, ',': op.truediv, '%': op.mod}


    def __init__(self, code: str):
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


    def fish_error(self):
        raise Exception('something smells fishy...')

    def pop(self, n: int = None) -> (int):
        '''
        Pops n values from the top of the stack

        if the stack is [a,b,c,d,e], pop(2) returns (d,e)
        without argument all values get popped
        if n is less than 1 or more than the stack length, an error gets raised
        '''
        if n is None: n = len(self.stack[-1])
        if not 0 < n <= len(self.stack[-1]):
            self.fish_error()
        result = tuple(self.stack[-1][-n:]) if n > 1 else self.stack[-1][-1]
        self.stack[-1][-n:] = []
        return result

    def push(self, *vals: float) -> None:
        '''pushes vals to the stack, e.g [a,b] -> push(x,y) -> [a,b,x,y]'''
        for val in vals:
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
        self.direction = self.R_FORWARD[self.direction]
    def m_backward(self):
        self.direction = self.R_BACKWARD[self.direction]
    def m_horizontal(self):
        self.direction = self.R_HORIZONTAL[self.direction]
    def m_vertical(self):
        self.direction = self.R_VERTICAL[self.direction]
    def m_cross(self):
        self.direction = self.R_CROSS[self.direction]
    def m_random(self):
        self.direction = self.DIRECTIONS[randint(0, 3)]
    def tramp(self):
        self.skip = True
    def tramp_cond(self):
        self.skip = not bool(self.pop(1))
    def jump(self):
        self.pos = self.pop(2)
    def literal(self):
        self.push(int(self.code[self.pos], base=16))
    def arithmetic(self):
        try: self.push(self.OPERATORS[self.code[self.pos]](*self.pop(2)))
        except ZeroDivisionError: self.fish_error()
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
        self.push(*(2 * [self.pop(1)]))
    def remove(self):
        self.pop(1)
    def swap2(self):
        self.push(*reversed(self.pop(2)))
    def swap3(self):
        x, y, z = self.pop(3)
        self.push(z, x, y)
    def shiftr(self):
        val = self.pop()
        if type(val) is tuple:
            *x, y = val
            self.push(y, *x)
    def shiftl(self):
        val = self.pop()
        if type(val) is tuple:
            x, *y = val
            self.push(*y, x)
    def reverse(self):
        if len(self.stack[-1]) != 1:
            self.push(*reversed(self.pop()))
    def length(self):
        self.push(len(self.stack[-1]))
    def new_stack(self):
        x = self.pop(self.pop(1))
        self.stack.append(list(x))
        self.register.append(None)
    def del_stack(self):
        x = self.pop()
        self.stack.pop()
        self.push(*x)
        self.register.pop()
    def out_char(self):
        self.stdout += chr(round(self.pop(1)))
    def out_num(self):
        self.stdout += str(self.pop(1))
    def read_char(self):
        val = self.stdin.pop() if self.stdin else -1
        self.push(val if isinstance(val, (int, float)) else ord(val))
    def do_register(self):
        if self.register[-1] is None:
            self.register[-1] = self.pop(1)
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
            cmd = self.code[self.pos]
            if cmd not in self.VALID_CHARS:
                self.fish_error
            if self.parse_mode is not None and self.parse_mode != cmd:
                self.push(ord(cmd))
            else:
                self.COMMANDS[cmd]()
            if not self.is_running: break
            d = (1 + int(self.skip)) * (-1 if self.direction in {'left', 'up'} else 1)
            col, row = self.pos
            if self.skip: self.skip = False
            self.pos = ((col + d) % self.code.cols if self.direction in {'right', 'left'} else col
                       ,(row + d) % self.code.rows if self.direction in {'up', 'down'} else row)

        return self.stdout


    def __str__(self):
        return str(self.code)







#### tests ####

from various_fishes import *

#print(Fish.__doc__)
hello = Fish(bf)
print(hello)
#print(hello.code.cols, hello.code.rows)
res = hello.run('+' * 97 + '.')
print(res)
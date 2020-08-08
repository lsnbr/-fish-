# The ><> language


A ><> (fish) program consists of a codebox, an IP (instruction pointer), a stack (of stacks), a register per stack, an input, and an output.  
A ><> program is executed like this:
```
load code
initialize IP

while True:
    try:    execute current command
    except: break
    move IP
```

<br><br>

### **The codebox**
- Coordinates are always written as (column, row).
- Holds a single number (character) per cell in the range (-∞, +∞).
- When parsed as command and when displayed, the cell value is wrapped into [0, 2**16).
- Spans from -∞ to +∞ in both directions.
- Starts with 0 in every cell.
- Initial source code is only in all positive coordinates.

### **The IP**
- Starts at (0,0) and moves to the right.
- Wraps to the other side of the codebox, if it reaches the border of the smallest bounding box of the code.
- Can never reach negative indexes. 

### **Errors**
- Division by zero.
- Reaching an invalid instruction.
- Trying to pop or modify the stack if it is empty or has too few values.
- ARBITRARY_JUMP = False: Jumping outside the smallest bounding box.



<br>

## ***Commands***
All commands are stored in the Codebox as their Unicode code points.

### **Movement**
- `> < ^ v ` Change the direction of the IP (right, left, up, down).
- `/ \ ` Change the direction of the IP by 90°.
- `| _ # ` Change the direction of the IP by 180°.
- `x ` Randomize the direction of the IP.
- `! ` Skip the following Instruction.
- `? ` Pop x of the stack. Skip the following instruction if x is zero.
- `. ` Pop y,x of the stack. Move the IP to (x,y) in the Codebox. Error if x or y is negative. If ARBITRARY_JUMP = False, moving outside the smallest bounding box causes an error.

### **Literals and Operators**
- `0-9 a-f ` Push the corresponding value onto the stack. a = 10, ... , f = 15.
- `' " ` Enable string parsing until matching closing quote is found. String parsing pushes every character as number to the stack, instead of executing them as commands.
- `+ - * , % ` Addition, substraction, multiplication, division and modulo. Pop y,x of the stack, and push x *operator* y to the stack. Division by zero causes an error. If EXACT_FRACTIONS, exact fractions are used, otherwise floating point numbers.
- `= ) ( ` Equality, greater than and less than. Pop y,x of the stack. Push 1 if x *operator* y and 0 otherwise.

### **Stack and Register Manipulation**
- `: ` Duplicate the top value on the stack.
- `~ ` Remove the top value from the stack.
- `$ ` Swap the two top values on the stack.
- `@ ` Swap the three top values on the stack, shifting them rightwards. e.g. 1,2,3,4 --@-> 1,4,2,3.
- `} { ` Shift the entire stack to the right/left. e.g. 1,2,3,4 --}-> 4,1,2,3 and 1,2,3,4 --{-> 2,3,4,1.
- `r ` Reverse the stack.
- `l ` Push the length of the stack onto the stack.
- `[ ` Pop x of the stack and create a new stack, moving max(x, 0) values from the old one onto the new one. Causes error if not enough values on the old stack are present. A new empty register for this stack is created.
- `] ` Remove the current stack, moving its values to the top of the underlying stack. Removes also the current register without moving its value. If the current stack already is the last stack, the stack and register get emptied.
- `& ` If the register is empty, pop the top value of the stack and put it in the register. Otherwise clear the register and put its value on the stack.

### **Input and Output**
- `o ` Pop x and output it as a character.
- `n ` Pop x and output it as a number.
- `i ` Read one character from input and push it as a number to the stack. When no more input is available, -1 is pushed.

### **Relection / Miscellaneous**
- `g ` Pop y,x of the stack and push the value at (x,y) in the codebox to the stack. x,y get rounded according to the ROUND_VALUES flag.
- `p ` Pop y,x,v of the stack and change the value at (x,y) in the codebox to v. x,y,v get rounded according to the ROUND_VALUES flag.
- `; ` End execution of the program.
- `space \x00 ` NOP. Does nothing.




<br><br>

### **Flags**
- `ARBITRARY_JUMP = False ` Let the jump instruction jump outside the smallest bounding box. Causes an error otherwise.
- `EXACT_FRACTIONS = False ` Uses fractions instead of floating point numbers.
- `ROUND_VALUES = False ` Rounds values from the stack to the nearest integer when used as coordinates or codebox character. Otherwise always round down to the nearest lower integer.

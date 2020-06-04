class FishCode:

    def __init__(self, src: str):
        '''
        Codebox represented as a rows x cols matrix

        supports subscription, length, contains and str
        all coordinates are given as (column, row)
        '''
        src = src.split('\n')
        while not src[0] or src[0].isspace(): src.pop(0)
        while not src[-1] or src[-1].isspace(): src.pop()
        self.rows, self.cols = len(src), max(map(len, src))
        self.code = [list(line.ljust(self.cols)) for line in src]


    def __str__(self) -> str:
        return '\n' + '\n'.join(map(''.join, self.code)) + '\n'


    def __len__(self) -> int:
        return self.rows * self.cols

    def __getitem__(self, index: (int, int)) -> str:
        col, row = index
        return self.code[row][col]

    def __setitem__(self, index: (int, int), val: str) -> None:
        if len(val) != 1: raise Exception('Only single chars!')
        col, row = index
        if col >= self.cols:
            self.code = [r + [' '] * (col - self.cols + 1) for r in self.code]
        if row >= self.rows:
            self.code += [[' '] * self.cols for _ in row - self.rows + 1]
        self.rows, self.cols = len(self.code), len(self.code[0])
        self.code[row][col] = val

    def __contains__(self, item: str) -> bool:
        if len(item) != 1: return False
        for line in self.code:
            if item in line: return True
        return False
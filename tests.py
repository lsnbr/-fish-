import unittest as ut
from fish_interpreter import *
from various_fishes import *


class TestFishGeneral(ut.TestCase):
    pass


class TestFishMovement(ut.TestCase):
    
    def test_move1(self):
        fish = Fish(move1)
        self.assertEqual(fish(), '1')


class TestFishCommands(ut.TestCase):

    def setUp(self):
        self.fish = Fish()
        self.fish.stack[0] = [1,2,3,4,5]

    def test_tramp_cond(self):
        self.fish.stack[0].append(0)
        self.fish.tramp_cond()
        self.assertEqual(self.fish.skip, True)
        self.fish.tramp_cond()
        self.assertEqual(self.fish.skip, False)

    def test_jump(self):
        self.fish.jump()
        self.assertEqual(self.fish.pos, (4,5))

    def test_swap2(self):
        self.fish.swap2()
        self.assertEqual(self.fish.stack, [[1,2,3,5,4]])

    def test_swap3(self):
        self.fish.swap3()
        self.assertEqual(self.fish.stack, [[1,2,5,3,4]])

    def test_shiftr(self):
        self.fish.shiftr()
        self.assertEqual(self.fish.stack, [[5,1,2,3,4]])

    def test_shiftl(self):
        self.fish.shiftl()
        self.assertEqual(self.fish.stack, [[2,3,4,5,1]])

    def test_reverse(self):
        self.fish.reverse()
        self.assertEqual(self.fish.stack, [[5,4,3,2,1]])

    def test_length(self):
        self.fish.length()
        self.assertEqual(self.fish.stack, [[1,2,3,4,5,5]])

    def test_new_stack(self):
        self.assertRaises(FishError, self.fish.new_stack)
        self.fish.stack = [[1,2,3,4,5,3]]
        self.fish.new_stack()
        self.assertEqual(self.fish.stack, [[1,2],[3,4,5]])

    def test_del_stack(self):
        self.fish.stack[-1].append(3)
        self.fish.new_stack()
        self.fish.del_stack()
        self.assertEqual(self.fish.stack, [[1,2,3,4,5]])

    def test_out_char(self):
        self.fish.stack[-1].append(97)
        self.fish.out_char()
        self.assertEqual(self.fish.stdout, 'a')

    def test_out_num(self):
        self.fish.out_num()
        self.assertEqual(self.fish.stdout, '5')
        self.fish.out_num()
        self.assertEqual(self.fish.stdout, '54')

    def test_read_char(self):
        self.fish.read_char()
        self.assertEqual(self.fish.stack, [[1,2,3,4,5,-1]])
        self.fish.stdin.append(ord('♞'))
        self.fish.read_char()
        self.assertEqual(self.fish.stack, [[1,2,3,4,5,-1,9822]])

    def test_do_register(self):
        self.fish.do_register()
        self.assertEqual(self.fish.register, [5])
        self.fish.do_register()
        self.assertEqual(self.fish.register, [None])

    def test_get_code(self):
        self.fish.get_code()
        self.assertEqual(self.fish.stack, [[1,2,3,0]])
        self.fish.stack[-1].append(0)
        self.fish.get_code()
        self.assertEqual(self.fish.stack, [[1,2,3,ord(';')]])

    def test_set_code(self):
        self.fish.set_code()
        self.assertEqual(self.fish.code[4,5], chr(3))


class TestFishPrograms(ut.TestCase):

    def test_quine1(self):
        fish = Fish(quine1)
        self.assertEqual(fish(fish()), fish())

    def test_quine2(self):
        fish = Fish(quine2)
        self.assertEqual(fish(fish()), fish())

    def test_hello_world(self):
        fish = Fish(hello_world)
        self.assertEqual(fish(), 'hello, world!')

    def test_fizzbuzz(self):
        fish = Fish(fizzbuzz)
        self.assertEqual(fish(), '\n'.join('FizzBuzz' if n%3+n%5==0 else 
                                           'Fizz' if n%3==0 else 
                                           'Buzz' if n%5==0 else str(n) for n in range(1,101)) + '\n')

    def test_factorial(self):
        fish = Fish(factorial)
        fish.push(10)
        self.assertEqual(fish(), '3628800')

    def test_sqrt(self):
        fish = Fish(sqrt)
        fish.push(2)
        self.assertAlmostEqual(float(fish()), 2 ** 0.5)

    def test_bf(self):
        fish = Fish(bf)
        self.assertEqual(fish('+' * 97 + '.'), 'a')


if __name__ == '__main__':
    ut.main()
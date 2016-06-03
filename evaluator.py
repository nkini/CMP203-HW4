import scanner
import screener
import parser
from pprint import pprint

from scanner import Token

#from collections import namedtuple

def step(C, E, K):

    print(type(C))
    print("C,E,K:")
    print('\t'.join(map(str,[C,E,K])))

    if type(C) == tuple:
        #CEK 1
        #if isinstance(C[0], Token) and C[0].type == 'APP'
        if C[0].type == 'APP':
            print('[cek1]')
            print()
            M = C[1][0]
            N = C[1][1]
            K.append(Token('ARG',(N,E)))
            return M, E

        #CEK 4
        #if isinstance(C[0], Token) and C[0].type == 'NUM' and K[-1].type == 'ARG':
        if C[0].type == 'NUM' and K[-1].type == 'ARG':
            print('[cek4]')
            print()
            V = C
            e = E
            k = K.pop()
            N = k.value[0]
            e_prime = k.value[1]
            K.append(Token('FUN',(V,e)))
            return N, e_prime

        #CEK 2b
        if C[0].type == 'OP2':
            print('[cek2b]')
            M = C[1]
            N = C[2]
            K.append(Token('ARG12', (C[0].value,N,E)))
            return (M),E

        #CEK 2a
        if C[0].type == 'OP1':
            print('[cek2a]')
            M = C[1].value
            o = C[0].value
            K.append(Token('ARG11', o))
            return (M),e

 
    if isinstance(C, Token):
        #CEK 5b
        if C.type == 'NUM' and K[-1].type == 'ARG22':
            print('[cek5b]')
            b = C.value
            k = K.pop()
            o = k.value[0]
            b1 = k.value[1]
            e_prime = k.value[2]
            V = compute(o, b1, b)
            return Token('NUM',V),[]

        #CEK 6b
        if C.type == 'NUM' and K[-1].type == 'ARG12':
            print('[cek6b]')
            k = K.pop()
            o = k.value[0]
            N = k.value[1]
            e_prime = k.value[2]
            K.append(Token('ARG22', (o,C.value,E)))
            return (N),e_prime

    return None, None


def compute(o,x,y):
    x,y = int(x),int(y)
    if o == '^' : return x**y
    if o == '+' : return x+y
    if o == '-' : return x-y
    if o == '*' : return x*y

import math
def evaluate(ast):
    control = ast
    environment = []
    stack = []
    while True:
        control, environment = step(control, environment, stack)
        print()

        if stack == [] and isinstance(control, Token) and control.type == 'NUM':
            return math.floor(control.value)

        if control is None and environment is None:
            return "stuck"

if __name__ == '__main__':

    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]
    
    for i,inp in enumerate([inputs[7]]):
        print("Input:   ",inp)
        outstring = ''
        scanout = scanner.generate_tokens(inp)
        screenout = screener.screen(scanout)
        ast = parser.parse(screenout)
        pprint(ast)
        #print("\nEvaluator returned:",evaluate(ast))
        #print('\n')

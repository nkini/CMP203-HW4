import scanner
import screener
import parser
from pprint import pprint

from scanner import Token

#from collections import namedtuple

def step(C, E, K):

    #print("C,E,K:")
    #print('\t'.join(map(str,[C,E,K])))

    #CEK 1
    if isinstance(C[0], Token) and C[0].type == 'APP':
        print('[cek1]')
        print()
        M = C[1][0]
        N = C[1][1]
        K.append(Token('ARG',(N,E)))
        return M, E

    #CEK 4
    if isinstance(C[0], Token) and C[0].type == 'NUM' and K[-1].type == 'ARG':
        print('[cek4]')
        print()
        V = C
        e = E
        k = K.pop()
        N = k.value[0]
        e_prime = k.value[1]
        K.append(Token('FUN',(V,e)))
        return N, e_prime

    return None, None

def evaluate(ast):
    control = ast
    environment = []
    stack = []
    while True:
        control, environment = step(control, environment, stack)
        if control is None and environment is None:
            return "stuck"

if __name__ == '__main__':

    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]
    
    for i,inp in enumerate([inputs[1]]):
        print("Input:   ",inp)
        outstring = ''
        scanout = scanner.generate_tokens(inp)
        screenout = screener.screen(scanout)
        ast = parser.parse(screenout)
        #print(ast)
        print("\nEvaluator returned:",evaluate(ast))
        #print('\n')

from pprint import pprint
import re
import collections

Token = collections.namedtuple('Token',['type','value'])

token_map = {

    'ID' : { 
            'lam'   : Token('LAM','lam'),
            'app'   : Token('APP','app'),
            'add1'  : Token('OP1','add1'),
            'sub1'  : Token('OP1','sub1'),
            'iszero': Token('OP1','iszero')
         },

    'OP' : {
            '+' : Token('OP2','+'),
            '-' : Token('OP2','-'),
            '*' : Token('OP2','*'),
            '^' : Token('OP2','^')
        }
}


def screen(inp, token_map=token_map):

    output = []

    for token in inp:        

        token_type = token.type
        token_value = token.value

        if token_type == 'WS': continue
        elif token_type == 'LPAREN' or 'RPAREN': output.append(token)
        elif token_type == 'NUM': output.append(token)

        elif token_type in token_map:
            if token_value in token_map[token_type]:
                output.append(token_map[token_type][token_value])
            else:
                output.append(Token('VAR',token_value))
        else: "Print something's not right"

    return output

import scanner
inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]
for inp in inputs:
    scanout = scanner.generate_tokens(inp)
    screenout = screen(scanout)
    print(screenout)

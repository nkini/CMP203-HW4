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

outputs = ["num(42)", "Lparen, app, num(43), num(44), Rparen", "Lparen, lam, var(hello), Lparen, app, var(hello), var(hello), Rparen, Rparen", "Lparen, lam, var(x), Lparen, app, var(y), Lparen, op1(add1), Lparen, op1(sub1), Lparen, op1(iszero), Lparen, op2(+), num(2), Lparen, op2(-), num(3), Lparen, op2(*), var(hello), Lparen, op2(^), num(33), num(44), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen", "Lparen, op2(^), Lparen, op2(-), num(0), num(2), Rparen, Lparen, op2(-), num(0), num(5), Rparen, Rparen", "var(blah)", "Lparen, app, Lparen, op2(+), num(2), num(3), Rparen, num(4), Rparen", "Lparen, op1(iszero), num(2), Rparen", "Lparen, op1(iszero), num(0), Rparen", "Lparen, app, Lparen, lam, var(x), var(x), Rparen, num(3), Rparen", "Lparen, app, Lparen, app, Lparen, app, Lparen, app, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Lparen, lam, var(f), Lparen, lam, var(n), Lparen, lam, var(a), Lparen, lam, var(b), Lparen, app, Lparen, app, var(n), Lparen, lam, var(m), Lparen, app, Lparen, app, Lparen, app, Lparen, app, var(f), var(f), Rparen, var(m), Rparen, var(a), Rparen, Lparen, app, var(a), var(b), Rparen, Rparen, Rparen, Rparen, var(b), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Lparen, lam, var(s), Lparen, lam, var(z), Lparen, app, var(s), Lparen, lam, var(s), Lparen, lam, var(z), var(z), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Lparen, lam, var(x), Lparen, op2(+), var(x), num(1), Rparen, Rparen, Rparen, num(5), Rparen", "Lparen, lam, var(z), Lparen, app, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Rparen, Rparen"]

for i,inp in enumerate(inputs):
    scanout = scanner.generate_tokens(inp)
    screenout = screen(scanout)
    print(screenout)
    assert(screenout.upper() == outputs[i].upper())
    print()

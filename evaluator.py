import scanner
import screener
import parser
from pprint import pprint

from scanner import Token

#from collections import namedtuple

outstring = ''

def step(C, E, K):

    global outstring

    #print("\n")
    #print("type(C)",type(C))
    #print("C is ",C)
    #print("C,E,K:")
    #print('\t'.join(map(str,[C,E,K])))
    #if K: print("K top is ",K[-1])

    #CEK 1
    #if isinstance(C[0], Token) and C[0].type == 'APP'
    if type(C) == tuple and C[0].type == 'APP':
        #print('[cek1]')
        outstring += '  [cek1]\n'
        M,N = C[1]
        K.append(Token('ARG',(N,E)))
        return (M), E

    #CEK 2b
    if type(C) == tuple and C[0].type == 'OP2':
        #print('[cek2b]')
        outstring += '  [cek2b]\n'
        M,N = C[1],C[2]
        K.append(Token('ARG12', (C[0].value,(N,E))))
        return (M),E

    #CEK 7  
    #if the control is a variable, we look it up in the environment
    if type(C) == Token and C.type == 'VAR':
        if E:
            #print('[cek7]')
            outstring += '  [cek7]\n'
            c = lookup(E,C)
            return c

        #if environment is empty, return an error
        # and if K is empty... not sure about this
        if not K:
            return None,None

    #CEK 4
    if K and isinstance(K[-1],Token) and K[-1].type == 'ARG':
        retval = cek4(C,E,K)
        if retval: return retval

    #CEK 3
    if K and K[-1].type == 'FUN':#C.type == 'NUM' 
        #print("got here")
        retval = cek3(C,E,K)
        if retval: return retval

    #CEK 6b
    if K and K[-1].type == 'ARG12':
        retval = cek6b(C,E,K)
        #if retval : return retval
        return retval

    if type(C) == tuple:
        
        #CEK 2a
        if C[0].type == 'OP1':
            #print('[cek2a]')
            outstring += '  [cek2a]\n'
            M = C[1].value
            o = C[0].value
            K.append(Token('ARG11', o))
            if type(M) == int:
                return Token('NUM',M),E
            else:
                return (M),E

        if C[0].type == 'LAM' and not K:
            return C,E
            
    if isinstance(C, Token):

        if not K:
            return C, E

        #CEK 5a
        if C.type == 'NUM' and K[-1].type == 'ARG11':
            #print('[cek5a]')
            outstring += '  [cek5a]\n'
            b = C.value
            k = K.pop()
            o = k.value
            V = compute(o, b, None)
            return Token('NUM',V),[]

        #CEK 5b
        if C.type == 'NUM' and K[-1].type == 'ARG22':
            #print('[cek5b]')
            outstring += '  [cek5b]\n'
            b = C.value
            k = K.pop()
            o = k.value[0]
            b1 = k.value[1][0]
            e_prime = k.value[1][1]
            #print(o, b1, b)
            V = compute(o, b1, b)
            return Token('NUM',V),[]


    return None, None


def cek6b(C,E,K):
    #print('[cek6b]')
    global outstring

    if type(C) == tuple:
        C = C[0]

    outstring += '  [cek6b]\n'
    k = K.pop()
    o = k.value[0]
    N = k.value[1][0]
    e_prime = k.value[1][1]
    K.append(Token('ARG22', (o,(C.value,E))))
    return (N),e_prime

def cek4(C,E,K):

    global outstring

    #print("This is K[-1]",K[-1])
    if K[-1].type == 'ARG':
        #print('[cek4]')
        outstring += '  [cek4]\n'
        #print(type(C))
        V = C
        e = E
        k = K.pop()
        N = k.value[0]
        e_prime = k.value[1]
        K.append(Token('FUN',(V,e)))
        return (N), e_prime

'''
Token(type='FUN', value=([(Token(type='VAR', value='x'), (Token(type='LAM', value='lam'), [...])), ([...], (Token(type='LAM', value='lam'), [...]))], [(Token(type='VAR', value='x'), (Token(type='LAM', value='lam'), [...])), ([...], (Token(type='LAM', value='lam'), [...]))]))
'''

def cek3(C,E,K):

    if C == tuple:
        C = C[0]

    global outstring
    if K and K[-1].type == 'FUN':#C.type == 'NUM' 
        #print("got here")
        #print(K[-1])
        if (type(K[-1].value[0]) == tuple and K[-1].value[0][0].type == 'LAM') or \
           (type(K[-1].value[0]) == Token and K[-1].value[0].type == 'LAM'):
            
            #print(['cek3'])
            #print("K[-1].value[0] is:",K[-1].value[0])
            outstring += '  [cek3]\n'
            k = K.pop()
            if type(k.value[0]) == tuple:
                X = k.value[0][1][0]
                M = k.value[0][1][1]
                e_prime = k.value[1]
            else:
                #print("in the else of cek3")
                #print("k is: ",k)
                #k is:  Token(type='FUN', value=(Token(type='LAM', value='lam'), [(Token(type='VAR', value='x'), (Token(type='LAM', value='lam'), [...]))]))
                X = k.value[1][0][0]
                M = k.value[1][0][1][0]
                e_prime = k.value[1][0][1][1]
            V = C#C.value
            #print("e_prime:",e_prime)
            #print("X:",X)
            #print("V:",V)
            #print("E:",E)
            #exit()
            e_prime.append((X,(V,E)))
            #print('\n',(M),e_prime,'\n')
            return (M),e_prime
    


def lookup(E, X):
    for e in E[-1::-1]:
        if X == e[0]:
            return e[1]


def compute(o,x,y):
    if y:
        x,y = int(x),int(y)
        if o == '^' : return x**y
        if o == '+' : return x+y
        if o == '-' : return x-y
        if o == '*' : return x*y
    else:
        x = int(x)
        if o == 'add1': return x+1
        if o == 'sub1': return x-1
        if o == 'iszero': return int(x == 0)

import math
def evaluate(ast):
    control = ast
    environment = []
    stack = []
    while True:
        control, environment = step(control, environment, stack)

        #print("control, environment:",control, environment)
        if control is None and environment is None:
            return "Stuck"

        if stack == []  and isinstance(control, Token) and control.type == 'LAM':
            return 'function'

        if stack == []  and isinstance(control, tuple) and isinstance(control[0],Token) and control[0].type == 'LAM':
            return 'function'

        if stack == [] and isinstance(control, Token) and control.type == 'NUM':
            return math.floor(control.value)



if __name__ == '__main__':

    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]
    

    outputs = [('',42),
('''  [cek1]
  [cek4]
''','Stuck'),
('','function'),
('','function'),
('''  [cek2b]
  [cek2b]
  [cek6b]
  [cek5b]
  [cek6b]
  [cek2b]
  [cek6b]
  [cek5b]
  [cek5b]
''',-1),
('','Stuck'),
('''  [cek1]
  [cek2b]
  [cek6b]
  [cek5b]
  [cek4]
''','Stuck'),
('''  [cek2a]
  [cek5a]
''',0),
('''  [cek2a]
  [cek5a]
''',1),
('''  [cek1]
  [cek4]
  [cek3]
  [cek7]
''',3),
('''  [cek1]
  [cek1]
  [cek1]
  [cek1]
  [cek4]
  [cek3]
  [cek1]
  [cek7]
  [cek4]
  [cek7]
  [cek3]
  [cek4]
  [cek3]
  [cek4]
  [cek3]
  [cek4]
  [cek3]
  [cek1]
  [cek1]
  [cek7]
  [cek4]
  [cek3]
  [cek4]
  [cek7]
  [cek3]
  [cek1]
  [cek7]
  [cek4]
  [cek3]
  [cek1]
  [cek1]
  [cek1]
  [cek1]
  [cek7]
  [cek4]
  [cek7]
  [cek3]
  [cek4]
  [cek7]
  [cek3]
  [cek4]
  [cek7]
  [cek3]
  [cek4]
  [cek1]
  [cek7]
  [cek4]
  [cek7]
  [cek3]
  [cek2b]
  [cek7]
  [cek6b]
  [cek5b]
  [cek3]
  [cek1]
  [cek1]
  [cek7]
  [cek4]
  [cek3]
  [cek4]
  [cek7]
  [cek3]
  [cek7]
''',6),
('','function')]

    for i,inp in enumerate(inputs):
        print("Input:   ",inp)
        outstring = ''
        scanout = scanner.generate_tokens(inp)
        screenout = screener.screen(scanout)
        ast = parser.parse(screenout)
        #pprint(ast)
        retval = evaluate(ast)
        print("Evaluator returned:",retval)
        print(outstring)
        assert(outputs[i] == (outstring,retval))

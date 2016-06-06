################################ SCANNER ################################

import re
import collections
from pprint import pprint

ID      = r'(?P<ID>[a-zA-Z][a-zA-Z0-9]*)'
NUM     = r'(?P<NUM>\d+)'
OP      = r'(?P<OP>[+\-*^])'
LPAREN  = r'(?P<Lparen>\()'
RPAREN  = r'(?P<Rparen>\))'
WS      = r'(?P<WS>\s+)'

master_pattern = re.compile('|'.join((ID, NUM, OP, LPAREN, RPAREN, WS)))

class Token(collections.namedtuple('Token',['type','value'])):
    __slots__ = ()
    '''
    def __repr__(self):
        if self.type in ['LPAREN','RPAREN','WS']: return self.type
        elif self.type in ['LAM','APP','OP1']: return (self.value).lower()
        else: return (self.type+'('+self.value+')').lower()
    '''

def generate_tokens(text, pattern=master_pattern):
    scanner = pattern.scanner(text)
    tokens = [Token(m.lastgroup, m.group()) for m in iter(scanner.match, None)]
    for i,tok in enumerate(tokens):
        if tok.type == 'NUM':
            tok = Token('NUM',int(tok.value))
            tokens[i] = tok
    return tokens

def stringify_tokens_scanner(tokens):
    buf = []
    for token in tokens:
        if token.type in ['Lparen','Rparen','WS'] : 
            buf.append(token.type)
        else: 
            buf.append(token.type+'('+str(token.value)+')')
    return buf

def pprint_scanner_output(tokens,per_line=False):
    buf = stringify_tokens_scanner(tokens)
    if per_line:
        print(',\n'.join(buf))
    else:
        print("Our output:     ",', '.join(buf))
        print("Expected output:",outputs[i].upper())

################################ SCREENER ################################

from pprint import pprint
import scanner
import re
import collections
from scanner import Token

#Token = collections.namedtuple('Token',['type','value'])

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

        if token.type == 'WS': continue
        elif token.type in ['LPAREN','RPAREN','NUM']: output.append(token)
        elif token.type in token_map:
            if token.value in token_map[token.type]:
                output.append(token_map[token.type][token.value])
            else:
                output.append(Token('VAR',token.value))
        else: "Print something's not right"

    return output


def stringify_tokens_screener(tokens):
    buf = []
    for token in tokens:
        if token.type in ['LPAREN','RPAREN','APP','LAM'] : 
            buf.append(token.type)
        else: 
            buf.append(token.type+'('+str(token.value)+')')
    return buf


def pprint_screener_output(tokens,per_line=False):
    buf = stringify_tokens_screener(tokens)
    if per_line:
        print(',\n'.join(buf))
    else:
        print("Our output:     ",', '.join(buf))
        print("Expected output:",outputs[i])



################################ PARSER ################################

import scanner
import screener
from pprint import pprint

outstring = ''

def E(tokens):

    global outstring

    if tokens[0].type == 'VAR':
        outstring += 'var('+tokens[0].value+')'
        return tokens[0], tokens[1:]

    elif tokens[0].type == 'NUM':
        outstring += 'num('+str(tokens[0].value)+')'
        return tokens[0], tokens[1:]

    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'LAM' and tokens[2].type == 'VAR':
        outstring += 'lam('+tokens[2].value+', '
        body,rem1 = E(tokens[3:])
        if rem1[0].type == 'RPAREN':
            outstring += ')'
            return (tokens[1], (tokens[2], body)), rem1[1:]
        else:
            return None,'Error'

    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'APP':
        outstring += 'app('
        fun, rem1 = E(tokens[2:])
        outstring += ', '
        arg, rem2 = E(rem1)
        if rem2[0].type == 'RPAREN':
            outstring += ')'
            return (tokens[1], (fun, arg)), rem2[1:]
        else:
            return None,'Error'

    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'OP1':
        outstring += 'op1('+tokens[1].value+', '
        body, rem = E(tokens[2:])
        if rem[0].type == 'RPAREN':
            outstring += ')'
            return (tokens[1], body), rem[1:]
        else:
            return None, 'Error'

    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'OP2':
        outstring += 'op2('+tokens[1].value+', '
        body1, rem1 = E(tokens[2:])
        outstring += ', '
        body2, rem2 = E(rem1)
        if rem2[0].type == 'RPAREN':
            outstring += ')'
            return (tokens[1], body1, body2), rem2[1:]
        else:
            return None,'Error'

    else:
        return None, 'Error'



def parse(tokens):
    ast,rem = E(tokens)
    if rem == []:
        return ast
    else:
        print("Error")


################################ EVALUATOR  ################################

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

################# EXECUTION AND OUTPUT ####################

if __name__ == '__main__':

    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]

    outputs_scanner = ["NUM(42)", "Lparen, ID(app), WS, NUM(43), WS, NUM(44), Rparen", "Lparen, ID(lam), WS, ID(hello), WS, Lparen, ID(app), WS, ID(hello), WS, ID(hello), Rparen, Rparen", "Lparen, ID(lam), WS, ID(x), WS, Lparen, ID(app), WS, ID(y), WS, Lparen, ID(add1), WS, Lparen, ID(sub1), WS, Lparen, ID(iszero), WS, Lparen, OP(+), WS, NUM(2), WS, Lparen, OP(-), WS, NUM(3), WS, Lparen, OP(*), WS, ID(hello), WS, Lparen, OP(^), WS, NUM(33), WS, NUM(44), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen", "Lparen, OP(^), WS, Lparen, OP(-), NUM(0), WS, NUM(2), Rparen, WS, Lparen, OP(-), NUM(0), WS, NUM(5), Rparen, Rparen", "ID(blah)", "Lparen, ID(app), WS, Lparen, OP(+), WS, NUM(2), WS, NUM(3), Rparen, WS, NUM(4), Rparen", "Lparen, ID(iszero), WS, NUM(2), Rparen", "Lparen, ID(iszero), WS, NUM(0), Rparen", "Lparen, ID(app), WS, Lparen, ID(lam), WS, ID(x), WS, ID(x), Rparen, WS, NUM(3), Rparen", "Lparen, ID(app), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, Lparen, ID(lam), WS, ID(x), WS, Lparen, ID(app), WS, ID(x), WS, ID(x), Rparen, Rparen, WS, Lparen, ID(lam), WS, ID(f), WS, Lparen, ID(lam), WS, ID(n), WS, Lparen, ID(lam), WS, ID(a), WS, Lparen, ID(lam), WS, ID(b), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, ID(n), WS, Lparen, ID(lam), WS, ID(m), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, Lparen, ID(app), WS, ID(f), WS, ID(f), Rparen, WS, ID(m), Rparen, WS, ID(a), Rparen, WS, Lparen, ID(app), WS, ID(a), WS, ID(b), Rparen, Rparen, Rparen, Rparen, WS, ID(b), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, WS, Lparen, ID(lam), WS, ID(s), WS, Lparen, ID(lam), WS, ID(z), WS, Lparen, ID(app), WS, ID(s), WS, Lparen, ID(lam), WS, ID(s), WS, Lparen, ID(lam), WS, ID(z), WS, ID(z), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, WS, Lparen, ID(lam), WS, ID(x), WS, Lparen, OP(+), WS, ID(x), WS, NUM(1), Rparen, Rparen, Rparen, WS, NUM(5), Rparen", "Lparen, ID(lam), WS, ID(z), WS, Lparen, ID(app), WS, Lparen, ID(lam), WS, ID(x), WS, Lparen, ID(app), WS, ID(x), WS, ID(x), Rparen, Rparen, WS, Lparen, ID(lam), WS, ID(x), WS, Lparen, ID(app), WS, ID(x), WS, ID(x), Rparen, Rparen, Rparen, Rparen"]

    outputs_screener = ["num(42)", "Lparen, app, num(43), num(44), Rparen", "Lparen, lam, var(hello), Lparen, app, var(hello), var(hello), Rparen, Rparen", "Lparen, lam, var(x), Lparen, app, var(y), Lparen, op1(add1), Lparen, op1(sub1), Lparen, op1(iszero), Lparen, op2(+), num(2), Lparen, op2(-), num(3), Lparen, op2(*), var(hello), Lparen, op2(^), num(33), num(44), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Rparen", "Lparen, op2(^), Lparen, op2(-), num(0), num(2), Rparen, Lparen, op2(-), num(0), num(5), Rparen, Rparen", "var(blah)", "Lparen, app, Lparen, op2(+), num(2), num(3), Rparen, num(4), Rparen", "Lparen, op1(iszero), num(2), Rparen", "Lparen, op1(iszero), num(0), Rparen", "Lparen, app, Lparen, lam, var(x), var(x), Rparen, num(3), Rparen", "Lparen, app, Lparen, app, Lparen, app, Lparen, app, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Lparen, lam, var(f), Lparen, lam, var(n), Lparen, lam, var(a), Lparen, lam, var(b), Lparen, app, Lparen, app, var(n), Lparen, lam, var(m), Lparen, app, Lparen, app, Lparen, app, Lparen, app, var(f), var(f), Rparen, var(m), Rparen, var(a), Rparen, Lparen, app, var(a), var(b), Rparen, Rparen, Rparen, Rparen, var(b), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Lparen, lam, var(s), Lparen, lam, var(z), Lparen, app, var(s), Lparen, lam, var(s), Lparen, lam, var(z), var(z), Rparen, Rparen, Rparen, Rparen, Rparen, Rparen, Lparen, lam, var(x), Lparen, op2(+), var(x), num(1), Rparen, Rparen, Rparen, num(5), Rparen", "Lparen, lam, var(z), Lparen, app, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Lparen, lam, var(x), Lparen, app, var(x), var(x), Rparen, Rparen, Rparen, Rparen"]

    outputs_parser = ["num(42)", "app(num(43), num(44))", "lam(hello, app(var(hello), var(hello)))", "lam(x, app(var(y), op1(add1, op1(sub1, op1(iszero, op2(+, num(2), op2(-, num(3), op2(*, var(hello), op2(^, num(33), num(44))))))))))", "op2(^, op2(-, num(0), num(2)), op2(-, num(0), num(5)))", "var(blah)", "app(op2(+, num(2), num(3)), num(4))", "op1(iszero, num(2))", "op1(iszero, num(0))", "app(lam(x, var(x)), num(3))", "app(app(app(app(lam(x, app(var(x), var(x))), lam(f, lam(n, lam(a, lam(b, app(app(var(n), lam(m, app(app(app(app(var(f), var(f)), var(m)), var(a)), app(var(a), var(b))))), var(b))))))), lam(s, lam(z, app(var(s), lam(s, lam(z, var(z))))))), lam(x, op2(+, var(x), num(1)))), num(5))", "lam(z, app(lam(x, app(var(x), var(x))), lam(x, app(var(x), var(x)))))"]

    outputs_evaluator = [('',42),
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


    #with open('reqdout.txt','w') as ft, open('recdout.txt','w') as fo:
    for i,inp in enumerate(inputs):
        print "Input string:\n  ",inp
        output_tokens = generate_tokens(inp)
        buf = stringify_tokens_scanner(output_tokens)
        print "Scanner tokens:\n  "+', '.join(buf)
        assert(outputs_scanner[i] == ', '.join(buf))
'''
    for i,inp in enumerate(inputs):
        print("Input:   ",inp)
        scanout = scanner.generate_tokens(inp)
        screenout = screen(scanout)
        buf = stringify_tokens(screenout)
        #pprint_screener_output(screenout)
        print(', '.join(buf))
        assert(', '.join(buf).upper() == outputs[i].upper())
        print('\n')

    
    for i,inp in enumerate(inputs):
        outstring = ''
        print("Input:   ",inp)
        scanout = scanner.generate_tokens(inp)
        screenout = screener.screen(scanout)
        ast = parse(screenout)
        #pprint(ast)
        #print("Our output:\n"+outstring)
        print(outstring)
        assert(outstring == outputs[i])
        print('\n')


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
'''

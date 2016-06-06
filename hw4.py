# TEAM:
# Sneha Das (sndas@ucsc.edu)
# Ankit Gupta (agupta29@ucsc.edu)
# Nikhil Kini (nkini@ucsc.edu)


################################ SCANNER ################################

import re
import collections
from pprint import pprint
import math

# We used regular expressions (sorry!) with the following functionality:
#(?P<label>...) Similar to regular parentheses, but the substring matched by the group is accessible via the symbolic group name label
# So the regular expression begins immediately after >
ID      = r'(?P<ID>[a-zA-Z][a-zA-Z0-9]*)'
NUM     = r'(?P<NUM>\d+)'
OP      = r'(?P<OP>[+\-*^])'
LPAREN  = r'(?P<Lparen>\()'
RPAREN  = r'(?P<Rparen>\))'
WS      = r'(?P<WS>\s+)'

# Match ID or NUM or OP or LPAREN ...
master_pattern = re.compile('|'.join((ID, NUM, OP, LPAREN, RPAREN, WS)))

'''
 Token is the datatype we have used for the Abstract Syntax Tree nodes

 namedtuple():  factory function for creating tuple subclasses with named fields

 collections.namedtuple(typename, field_names)

 Returns a new tuple subclass named typename. The new subclass is used to create tuple-like objects that have fields accessible by attribute lookup as well as being indexable and iterable. In our case, typename is Token and this is the subclass that we use for our AST, as well as for Scanner/Screener/Parser tokens.

 The field_names are a sequence of strings such as ['x', 'y']. In out case, field_names are type and value.

    Example:
    Creating and accessing a NUM token:
        >>> tok = Token('NUM',42)
        >>> tok.type
        'NUM'
        >>> tok.value
        42
'''

Token = collections.namedtuple('Token', ['type', 'value'])

def generate_tokens(text, pattern=master_pattern):
    # match the 'master' pattern - one regexp with all constituent token regexps ORed
    scanner = pattern.scanner(text)
    # iterate over the matched regexps
    # m.lastgroup is the label in (?P<label>...)
    tokens = [Token(m.lastgroup, m.group()) for m in iter(scanner.match, None)]
    for i,tok in enumerate(tokens):
        if tok.type == 'NUM':
            tok = Token('NUM',int(tok.value))
            tokens[i] = tok
    # Each element of the python list tokens is a scanner token
`   # tokens[0] is the first scanner token tokens[n] is the nth etc
    # tokens[0].type is the scanner class of the first scanner token
    # tokens[0].value is the instance (substring of the input string) of the first scanner token
    return tokens

def stringify_tokens_scanner(tokens):
    buf = []
    for token in tokens:
        if token.type in ['Lparen','Rparen','WS'] : 
            buf.append(token.type)
        else: 
            buf.append(token.type+'('+str(token.value)+')')
    return buf

################################ SCREENER ################################

'''
token_map is used to map from scanner tokens to parser tokens

The Token class is once again used for defining Parser tokens

Some parser tokens have values (op2,op1,var,num) while others don't (lam,app)
Wherever there are no values, the type itself is used as value
Parser tokens for Lparen and Rparen are simply Scanner tokens passed through as is e.g. Token('Lparen','(')

Parser tokens that have variable values (num,var) are not part of the map and are created at [**1**]

'''
token_map = {

    'ID' : { 
            'lam'   : Token('lam','lam'),
            'app'   : Token('app','app'),
            'add1'  : Token('op1','add1'),
            'sub1'  : Token('op1','sub1'),
            'iszero': Token('op1','iszero')
         },

    'OP' : {
            '+' : Token('op2','+'),
            '-' : Token('op2','-'),
            '*' : Token('op2','*'),
            '^' : Token('op2','^')
        }
}

def screen(inp, token_map=token_map):

    # Output 
    output = []

    for token in inp:        
        # Drop token
        if token.type == 'WS': continue
        # Pass through token
        elif token.type in ['Lparen','Rparen']: output.append(token)
        #[**1**]
        elif token.type == 'NUM': output.append(Token('num',token.value))
        # tokens in token_map (Identifiers and operators)
        elif token.type in token_map:
            # Reserved keywords and operators
            if token.value in token_map[token.type]:
                output.append(token_map[token.type][token.value])
            else:
                #[**1**]
                # variable names
                output.append(Token('var',token.value))
        else: "Print something's not right"
    # output is a python list of parser tokens
    # output[0] is the first parser token, output[n] is the nth etc
    # output[0].type is the parser class of the first parser token
    # output[0].value is only truly useful in the case where token.type is 'var','num','op1','op2' and 
    #                   represents the specific value of the variable/number/operator
    return output


def stringify_tokens_screener(tokens):
    buf = []
    for token in tokens:
        if token.type in ['Lparen','Rparen','app','lam'] : 
            buf.append(token.type)
        else: 
            buf.append(token.type+'('+str(token.value)+')')
    return buf

################################ AST ################################

outstring_ast = ''

def E(tokens):

    global outstring_ast

    if tokens[0].type == 'var':
        outstring_ast += 'var('+tokens[0].value+')'
        # a,b is Syntactic sugar for (a,b)
        # here we return a tuple tup  of 2 elements:
        #  tup[0] = tokens[0] -> first element in the list tokens
        #  tup[1] = tokens[1:] -> the list of the elements from 2 to the end of the list tokens
        return tokens[0], tokens[1:]

    elif tokens[0].type == 'num':
        outstring_ast += 'num('+str(tokens[0].value)+')'
        return tokens[0], tokens[1:]

    elif tokens[0].type == 'Lparen' and tokens[1].type == 'lam' and tokens[2].type == 'var':
        outstring_ast += 'lam('+tokens[2].value+', '
        body,rem1 = E(tokens[3:])
        if rem1[0].type == 'Rparen':
            outstring_ast += ')'
            # Once again, returns a tuple tup
            # tup[0] -> (tokens[1], (tokens[2], body)) -> is itself a tuple
            #   tup[0][0] -> tokens[1] -> Token('lam','lam') -> a token indicating that this is a tuple denoting a lambda expression
            #   tup[0][1] ->  (tokens[2], body) -> Also a tuple that contains:
            #       tup[0][1][0] -> tokens[2] -> the variable for the lambda expression
            #       tup[0][1][1] -> body -> the body of the lambda expression
            # tup[1] -> rem1[1:] -> is the remainder of the tokens left after parsing till the body and rparen corresponding to the current lambda expression
            return (tokens[1], (tokens[2], body)), rem1[1:]
        else:
            return None,'Error'

    elif tokens[0].type == 'Lparen' and tokens[1].type == 'app':
        outstring_ast += 'app('
        fun, rem1 = E(tokens[2:])
        outstring_ast += ', '
        arg, rem2 = E(rem1)
        if rem2[0].type == 'Rparen':
            outstring_ast += ')'
            # Once again, returns a tuple tup
            # tup[0] -> (tokens[1], (fun, arg)) -> is itself a tuple
            #   tup[0][0] -> tokens[1] -> Token('app','app') -> a token indicating that this is a tuple denoting a function application
            #   tup[0][1] ->  (fun, arg) -> Also a tuple that contains:
            #       tup[0][1][0] -> fun -> the definition for the function
            #       tup[0][1][1] -> arg -> the argument to the function
            # tup[1] -> rem2[1:] -> is the remainder of the tokens left after parsing till the body and rparen corresponding to the current lambda expression
            return (tokens[1], (fun, arg)), rem2[1:]
        else:
            return None,'Error'

    elif tokens[0].type == 'Lparen' and tokens[1].type == 'op1':
        outstring_ast += 'op1('+tokens[1].value+', '
        body, rem = E(tokens[2:])
        if rem[0].type == 'Rparen':
            outstring_ast += ')'
            # returns a tuple tup
            # tup[0][0] -> tokens[1] -> Token('op1','X') where X can be add1,sub1,iszero1
            # tup[0][1] -> body -> the expression to which op1 needs to be applied
            return (tokens[1], body), rem[1:]
        else:
            return None, 'Error'

    elif tokens[0].type == 'Lparen' and tokens[1].type == 'op2':
        outstring_ast += 'op2('+tokens[1].value+', '
        body1, rem1 = E(tokens[2:])
        outstring_ast += ', '
        body2, rem2 = E(rem1)
        if rem2[0].type == 'Rparen':
            outstring_ast += ')'
            # returns a tuple tup
            # tup[0][0] -> tokens[1] -> Token('op2','X') where X can be +,-,*,^
            # tup[0][1] -> body1 -> operand1
            # tup[0][2] -> body2 -> operand2
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


outstring_eval = ''

def step(C, E, K):

    global outstring_eval

    #print("\n")
    #print("type(C)",type(C))
    #print("C is ",C)
    #print("C,E,K:")
    #print('\t'.join(map(str,[C,E,K])))
    #if K: print("K top is ",K[-1])

    #CEK 1
    #if isinstance(C[0], Token) and C[0].type == 'APP'
    if type(C) == tuple and C[0].type == 'app':
        #print('[cek1]')
        outstring_eval += '  [cek1]\n'
        M,N = C[1]
        K.append(Token('ARG',(N,E)))
        return (M), E

    #CEK 2b
    if type(C) == tuple and C[0].type == 'op2':
        #print('[cek2b]')
        outstring_eval += '  [cek2b]\n'
        M,N = C[1],C[2]
        K.append(Token('ARG12', (C[0].value,(N,E))))
        return (M),E

    #CEK 7  
    #if the control is a variable, we look it up in the environment
    if type(C) == Token and C.type == 'var':
        if E:
            #print('[cek7]')
            outstring_eval += '  [cek7]\n'
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
        if C[0].type == 'op1':
            #print('[cek2a]')
            outstring_eval += '  [cek2a]\n'
            M = C[1].value
            o = C[0].value
            K.append(Token('ARG11', o))
            if type(M) == int:
                return Token('num',M),E
            else:
                return (M),E

        if C[0].type == 'lam' and not K:
            return C,E
            
    if isinstance(C, Token):

        if not K:
            return C, E

        #CEK 5a
        if C.type == 'num' and K[-1].type == 'ARG11':
            #print('[cek5a]')
            outstring_eval += '  [cek5a]\n'
            b = C.value
            k = K.pop()
            o = k.value
            V = compute(o, b, None)
            return Token('num',V),[]

        #CEK 5b
        if C.type == 'num' and K[-1].type == 'ARG22':
            #print('[cek5b]')
            outstring_eval += '  [cek5b]\n'
            b = C.value
            k = K.pop()
            o = k.value[0]
            b1 = k.value[1][0]
            e_prime = k.value[1][1]
            #print(o, b1, b)
            V = compute(o, b1, b)
            return Token('num',V),[]


    return None, None


def cek6b(C,E,K):
    #print('[cek6b]')
    global outstring_eval

    if type(C) == tuple:
        C = C[0]

    outstring_eval += '  [cek6b]\n'
    k = K.pop()
    o = k.value[0]
    N = k.value[1][0]
    e_prime = k.value[1][1]
    K.append(Token('ARG22', (o,(C.value,E))))
    return (N),e_prime

def cek4(C,E,K):

    global outstring_eval

    #print("This is K[-1]",K[-1])
    if K[-1].type == 'ARG':
        #print('[cek4]')
        outstring_eval += '  [cek4]\n'
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

    global outstring_eval
    if K and K[-1].type == 'FUN':#C.type == 'NUM' 
        #print("got here")
        #print(K[-1])
        if (type(K[-1].value[0]) == tuple and K[-1].value[0][0].type == 'lam') or \
           (type(K[-1].value[0]) == Token and K[-1].value[0].type == 'lam'):
            
            #print(['cek3'])
            #print("K[-1].value[0] is:",K[-1].value[0])
            outstring_eval += '  [cek3]\n'
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

def evaluate(ast):
    control = ast
    environment = []
    stack = []
    while True:
        control, environment = step(control, environment, stack)

        #print("control, environment:",control, environment)
        if control is None and environment is None:
            return "Stuck"

        if stack == []  and isinstance(control, Token) and control.type == 'lam':
            return 'function'

        if stack == []  and isinstance(control, tuple) and isinstance(control[0],Token) and control[0].type == 'lam':
            return 'function'

        if stack == [] and isinstance(control, Token) and control.type == 'num':
            return int(math.floor(control.value))

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
        print "Input string:\n  "+inp
        scanner_tokens = generate_tokens(inp)
        buf = stringify_tokens_scanner(scanner_tokens)
        print "Scanner tokens:\n  "+', '.join(buf)
        assert(outputs_scanner[i] == ', '.join(buf))

        screenout = screen(scanner_tokens)
        buf = stringify_tokens_screener(screenout)
        print "Parser tokens:\n  "+', '.join(buf)
        assert(', '.join(buf) == outputs_screener[i])

        outstring_ast = ''
        ast = parse(screenout)
        print "Syntax tree:\n  "+ outstring_ast
        assert(outstring_ast == outputs_parser[i])

        outstring_eval = ''
        retval = evaluate(ast)
        if outstring_eval:
            print "Sequence of rules:\n" + outstring_eval.strip('\n')
        else:
            print "Sequence of rules:"
        print "Answer:\n  "+str(retval)
        assert(outputs_evaluator[i] == (outstring_eval,retval))

        print

print "done"

#!/usr/bin/python

# TEAM:
# Sneha Das (sndas@ucsc.edu)
# Ankit Gupta (agupta29@ucsc.edu)
# Nikhil Kini (nkini@ucsc.edu)


################################ SCANNER ################################

import re
import collections
from pprint import pprint
import math
import sys
import fileinput

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
    # tokens[0] is the first scanner token tokens[n] is the nth etc
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

    #change to the token type for testing conditions consistently
    if type(C) == tuple:
        C_tok = C[0]
    else:
        C_tok = C

    # if C is a type of value
    if C_tok.type == 'num' or C_tok.type == 'lam':

        # check the top of stack
        if not K:
            return C_tok,'finished'

        #CEK 4
        #K[-1] is the stack top
        if K[-1].type == 'ARG':
            retval = cek4(C,E,K)
            if retval: return retval

        #CEK 3
        #e.g. k is:  (Token(type='FUN', value=(Token(type='LAM', value='lam'), [(Token(type='VAR', value='x'), (Token(type='LAM', value='lam'), [...]))])))
        # Details given below in the definition of function cek3
        if K[-1].type == 'FUN': 
            if (type(K[-1].value[0]) == tuple and K[-1].value[0][0].type == 'lam') or \
               (type(K[-1].value[0]) == Token and K[-1].value[0].type == 'lam'):
                #print("got here")
                retval = cek3(C,E,K)
                if retval: return retval

        #CEK 5a
        if K[-1].type == 'ARG11':
            #print('[cek5a]')
            b = C_tok.value
            k = K.pop()
            o = k.value
            # to be sure that delta exists
            if o in ['add1','sub1','iszero'] and b is not 'lam':
                V = compute(o, b, None)
                outstring_eval += '  [cek5a]\n'
                return Token('num',V),[]

        #CEK 6b
        if K[-1].type == 'ARG12':
            retval = cek6b(C,E,K)
            #if retval : return retval
            return retval

        #CEK 5b
        if K[-1].type == 'ARG22':
            #print('[cek5b]')
            b = C_tok.value
            k = K.pop()
            o = k.value[0]
            b1 = k.value[1][0]
            e_prime = k.value[1][1]
            # to be sure that delta exists
            if o in ['+','-','*','^'] and b1 is not 'lam' and b is not 'lam':     
                V = compute(o, b1, b)
                outstring_eval += '  [cek5b]\n'
                return Token('num',V),[]

        # This is equivalent to returning "stuck"
        return None, None

    else:   #Control dictates the rule to follow

        #CEK 1
        if C_tok.type == 'app':
            #print('[cek1]')
            outstring_eval += '  [cek1]\n'
            M,N = C[1]
            K.append(Token('ARG',(N,E)))
            return M, E

        #CEK 2b
        if C_tok.type == 'op2':
            #print('[cek2b]')
            outstring_eval += '  [cek2b]\n'
            M,N = C[1],C[2]
            K.append(Token('ARG12', (C[0].value,(N,E))))
            return M,E

        #CEK 7  
        #if the control is a variable, we look it up in the environment
        if C_tok.type == 'var':
            if E:
                #print('[cek7]')
                outstring_eval += '  [cek7]\n'
                c = lookup(E,C)
                return c

        #CEK 2a
        if C_tok.type == 'op1':
            #print('[cek2a]')
            outstring_eval += '  [cek2a]\n'
            M = C[1].value
            o = C[0].value
            K.append(Token('ARG11', o))
            if type(M) == int:
                return Token('num',M),E
            else:
                return M,E

        return None, None

    print "fell through"

def cek3(C,E,K):

    if C == tuple:
        C = C[0]

    global outstring_eval
        
    outstring_eval += '  [cek3]\n'
    k = K.pop()
    if type(k.value[0]) == tuple:
        #e.g. k is:  (Token(type='FUN', value=(Token(type='LAM', value='lam'), [(Token(type='VAR', value='x'), (Token(type='LAM', value='lam'), [...]))])))
        # k is: Token(type='FUN', value=((Token(type='lam', value='lam'), (Token(type='var', value='x'), Token(type='var', value='x'))), []))
        # k.value is: ((Token(type='lam', value='lam'), (Token(type='var', value='x'), Token(type='var', value='x'))), [])
        # k.value[1] is: []
        # k.value[0] is: (Token(type='lam', value='lam'), (Token(type='var', value='x'), Token(type='var', value='x')))
        # k.value[0][1] is: (Token(type='var', value='x'), Token(type='var', value='x'))
        # k.value[0][1][0] is: Token(type='var', value='x')
        # k.value[0][1][1] is: Token(type='var', value='x')
        X = k.value[0][1][0]
        M = k.value[0][1][1]
        e_prime = k.value[1]
    else:
        #print "k is:",k
        X = k.value[1][0][0]
        M = k.value[1][0][1][0]
        e_prime = k.value[1][0][1][1]
    V = C#C.value
    e_prime.append((X,(V,E)))
    return M,e_prime



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
    return N,e_prime

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
        return N, e_prime


def lookup(E, X):
    # E[-1::-1] enumerates in stack order (reverse of how a list is traversed
    # >>> E
    # [(Token(type='var', value='x'), (Token(type='num', value=3), [...]))]
    for e in E[-1::-1]:
        # >>> e
        # (Token(type='var', value='x'), (Token(type='num', value=3), [...]))
        if X == e[0]:
            # >>> e[0]
            # Token(type='var', value='x')
            return e[1]
            # >>> e[1]
            # (Token(type='num', value=3), [...]) A pair of Value and Env


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

        if control is None and environment is None:
            return 'Stuck'

        if stack == []  and isinstance(control, Token) and control.type == 'lam':
            return 'function'

        if stack == [] and isinstance(control, Token) and control.type == 'num':
            return int(math.floor(control.value))

################# EXECUTION AND OUTPUT ####################
for inp in fileinput.input():

    inp = inp.strip('\n').strip()

    print "Input string:\n  "+inp
    scanner_tokens = generate_tokens(inp)
    buf = stringify_tokens_scanner(scanner_tokens)
    print "Scanner tokens:\n  "+', '.join(buf)
    #assert(outputs_scanner[i] == ', '.join(buf))

    screenout = screen(scanner_tokens)
    buf = stringify_tokens_screener(screenout)
    print "Parser tokens:\n  "+', '.join(buf)
    #assert(', '.join(buf) == outputs_screener[i])

    outstring_ast = ''
    ast = parse(screenout)
    print "Syntax tree:\n  "+ outstring_ast
    #assert(outstring_ast == outputs_parser[i])

    outstring_eval = ''
    retval = evaluate(ast)
    if outstring_eval:
        print "Sequence of rules:\n" + outstring_eval.strip('\n')
    else:
        print "Sequence of rules:"
    print "Answer:\n  "+str(retval)
    #assert(outputs_evaluator[i] == (outstring_eval,retval))

    print

print "done"

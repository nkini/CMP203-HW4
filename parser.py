import scanner
import screener
from pprint import pprint

ast = []

def stringify_tokens(tokens):
    buf = []
    for token in tokens:
        if token.type in ['LPAREN','RPAREN','APP','LAM'] : 
            buf.append(token.type)
        else: 
            buf.append(token.type+'('+token.value+')')
    return buf


def E(tokens):
    if tokens[0].type == 'VAR':
        return (tokens[0], tokens[1:])
    elif tokens[0].type == 'NUM':
        return (tokens[0], tokens[1:])
    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'LAM' and tokens[2].type == 'VAR':
        body,rem1=E(tokens[3:])
        if rem1[0].type == 'RPAREN':
            return ((tokens[1], (tokens[2], body)), rem1[1:])
        else:
            return (None,'error')
    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'APP':
        fun, rem1 = E(tokens[2:])
        arg, rem2 = E(rem1)
        if rem2[0].type == 'RPAREN':
            return ((tokens[1], (fun, arg)), rem2[1:])
        else:
            return (None,'error')
    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'OP1':
        body, rem = E(tokens[2:])
        if rem[0].type == 'RPAREN':
            return ((tokens[1], body), rem[1:])
        else:
            return (None, 'error')
    elif tokens[0].type == 'LPAREN' and tokens[1].type == 'OP2':
        body1, rem1 = E(tokens[2:])
        body2, rem2 = E(rem1)
        if rem2[0].type == 'RPAREN':
            return ((tokens[1], body1, body2), rem2[1:])
        else:
            return (None,'error')
    else:
        return (None, 'error')


def parse(tokens):
    ast,rem = E(tokens)
    if rem == []:
        return ast
    else:
        print "Error"



def pprint_ast_output(ast):
    print("Implement this function")

if __name__ == '__main__':

    outputs = ["num(42)", "app(num(43), num(44))", "lam(hello, app(var(hello), var(hello)))", "lam(x, app(var(y), op1(add1, op1(sub1, op1(iszero, op2(+, num(2), op2(-, num(3), op2(*, var(hello), op2(^, num(33), num(44))))))))))", "op2(^, op2(-, num(0), num(2)), op2(-, num(0), num(5)))", "var(blah)", "app(op2(+, num(2), num(3)), num(4))", "op1(iszero, num(2))", "op1(iszero, num(0))", "app(lam(x, var(x)), num(3))", "app(app(app(app(lam(x, app(var(x), var(x))), lam(f, lam(n, lam(a, lam(b, app(app(var(n), lam(m, app(app(app(app(var(f), var(f)), var(m)), var(a)), app(var(a), var(b))))), var(b))))))), lam(s, lam(z, app(var(s), lam(s, lam(z, var(z))))))), lam(x, op2(+, var(x), num(1)))), num(5))", "lam(z, app(lam(x, app(var(x), var(x))), lam(x, app(var(x), var(x)))))"]
    
    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]

    
    for i,inp in enumerate(inputs):
        print("Input:   ",inp)
        scanout = scanner.generate_tokens(inp)
        screenout = screener.screen(scanout)
        ast = parse(screenout)
        pprint(ast)
        #buf = stringify_tokens(ast)
        #pprint_ast_output(ast)
        #assert(', '.join(buf).upper() == outputs[i].upper())
        print('\n')

import scanner
import screener

def stringify_tokens(ast):
    return []


def E(tokens):

    return tokens


def parse(tokens):
    ast,rem = E(tokens)
    if rem == []:
        return ast
    else:
        print "Error"    
        return


'''    
    i = 0

def term(token):
    global i
    i += 1
    return inp[i-1] == token.val

    # per non terminal, per production
    # E -> var
    def E_1():
        return

    # E -> ( lambda var E )
    def E_2():


    # E -> ( app E E )
    def E_3():
        

    # E -> ( op1 E )
    def E_4():
        

    # E -> ( op2 E E )
    def E_5():
        

    # E -> num
    def E_6():
        

    # for the entire non terminal E
    def E():
'''   
     

def pprint_ast_output(ast):
    print("Implement this function")

if __name__ == '__main__':

    outputs = ["num(42)", "app(num(43), num(44))", "lam(hello, app(var(hello), var(hello)))", "lam(x, app(var(y), op1(add1, op1(sub1, op1(iszero, op2(+, num(2), op2(-, num(3), op2(*, var(hello), op2(^, num(33), num(44))))))))))", "op2(^, op2(-, num(0), num(2)), op2(-, num(0), num(5)))", "var(blah)", "app(op2(+, num(2), num(3)), num(4))", "op1(iszero, num(2))", "op1(iszero, num(0))", "app(lam(x, var(x)), num(3))", "app(app(app(app(lam(x, app(var(x), var(x))), lam(f, lam(n, lam(a, lam(b, app(app(var(n), lam(m, app(app(app(app(var(f), var(f)), var(m)), var(a)), app(var(a), var(b))))), var(b))))))), lam(s, lam(z, app(var(s), lam(s, lam(z, var(z))))))), lam(x, op2(+, var(x), num(1)))), num(5))", "lam(z, app(lam(x, app(var(x), var(x))), lam(x, app(var(x), var(x)))))"]
    
    inputs = ["42", "(app   43 44)", "(lam hello (app hello hello))", "(lam x (app y (add1 (sub1 (iszero (+ 2 (- 3 (* hello (^ 33 44)))))))))", "(^ (-0 2) (-0 5))", "blah", "(app (+ 2 3) 4)", "(iszero 2)", "(iszero 0)", "(app (lam x x) 3)", "(app (app (app (app (lam x (app x x)) (lam f (lam n (lam a (lam b (app (app n (lam m (app (app (app (app f f) m) a) (app a b)))) b)))))) (lam s (lam z (app s (lam s (lam z z)))))) (lam x (+ x 1))) 5)", "(lam z (app (lam x (app x x)) (lam x (app x x))))"]

    
    for i,inp in enumerate(inputs):
        print("Input:   ",inp)
        scanout = scanner.generate_tokens(inp)
        screenout = screen(scanout)
        ast = parse(screenout)
        buf = stringify_tokens(ast)
        pprint_ast_output(ast)
        assert(', '.join(buf).upper() == outputs[i].upper())
        print()

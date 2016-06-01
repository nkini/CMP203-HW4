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

        token_type = token['type']
        token_value = token['value']

        if token_class == 'WS': continue
        elif token_class == 'LPAREN' or 'RPAREN': output.append(token)
        elif token_class == 'NUM': output.append(token)

        elif token_class in token_map:
            if token_value in token_map[token_class]:
                output.append(token_map[token_class][token_value])
            else:
                output.append(Token('VAR',token_value))
        else: "Print something's not right"

    return output
        

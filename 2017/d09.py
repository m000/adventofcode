#!/usr/bin/env python3
import sys
from pathlib import Path as _P
from ply.lex import TOKEN
import ply.lex as lex
import ply.yacc as yacc

INPUT_DEFAULT = _P(__file__).with_name('%s-input.txt' % _P(__file__).stem)
INPUT = sys.argv[1] if len(sys.argv) > 1 else INPUT_DEFAULT

### lex related stuff - start #####################################
# states
states = (
    ('garbagec', 'exclusive'),
    ('garbageb', 'exclusive'),
)

# tokens
tokens = (
    'LGROUP',
    'RGROUP',
    'LGARBAGE',
    'RGARBAGE',
    'EXCLAMATION',
    'COMMA',
    'STRING',
    'garbagec_STRING',
    'garbageb_STRING',
)

# token regexes
tre_LGROUP        = r'\{'
tre_RGROUP        = r'\}'
tre_LGARBAGE      = r'\<'
tre_RGARBAGE      = r'\>'
tre_EXCLAMATION   = r'\!'
tre_garbagec_STRING = r'.'
tre_garbageb_STRING = r'[^>!]+'

# token regexes for implicit rules
t_STRING        = r'[^{}<>!,]+'
t_COMMA         = r'\,'

@TOKEN(tre_LGROUP)
def t_LGROUP(t):
    t.lexer.level += 1
    return t

@TOKEN(tre_RGROUP)
def t_RGROUP(t):
    t.lexer.level -= 1
    return t

# Garbage char
@TOKEN(tre_EXCLAMATION)
def t_begin_garbagec(t):
    t.lexer.garbagec = t.lexer.lexdata[t.lexer.lexpos-1]
    t.lexer.push_state('garbagec')

@TOKEN(tre_garbagec_STRING)
def t_garbagec_end(t):
    t.lexer.garbagec += t.lexer.lexdata[t.lexer.lexpos-1]
    #print('%s: %s' % (t.lexer.lexstate, t.lexer.garbagec))
    t.lexer.pop_state()

# Garbage block
@TOKEN(tre_LGARBAGE)
def t_begin_garbageb(t):
    t.lexer.garbageb_start = t.lexer.lexpos-1
    t.lexer.push_state('garbageb')

@TOKEN(tre_RGARBAGE)
def t_garbageb_end(t):
    #print('%s: %s' % (t.lexer.lexstate, t.lexer.lexdata[t.lexer.garbageb_start:t.lexer.lexpos]))
    t.lexer.pop_state()

@TOKEN(tre_garbageb_STRING)
def t_garbageb_string(t):
    pass

@TOKEN(tre_EXCLAMATION)
def t_garbageb_begin_garbagec(t):
    t.lexer.garbagec = t.lexer.lexdata[t.lexer.lexpos-1]
    t.lexer.push_state('garbagec')

# errors and ignored
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
t_ignore        = ' \t\n'
### ply related stuff - end #######################################

### yacc related stuff - start ####################################
class Group:
    def __init__(self, contents=[]):
        self.parent = None
        self.score = 0
        self.level = 0
        self.contents = contents

    def update(self, parent=None):
        if parent is None:
            self.level = 1
        else:
            self.parent = parent
            self.level = parent.level + 1

        self.score = self.level
        if isinstance(self.contents, list):
            for c in self.contents:
                c.update(self)
                self.score += c.score

    def __str__(self):
        return '{%s:%02d:%03d}' % (self.contents, self.level, self.score)

    def __repr__(self):
        return self.__str__()

def p_group(p):
    '''group : LGROUP RGROUP
             | LGROUP garbage RGROUP
             | LGROUP STRING RGROUP
             | LGROUP group RGROUP
             | LGROUP group_list RGROUP
    '''
    if p[2] == '}':
        p[0] = Group()
    elif p[3] == '}' and isinstance(p[2], str):
        p[0] = Group(contents=p[2])
    elif p[3] == '}' and isinstance(p[2], Group):
        p[0] = Group(contents=[p[2],])
    elif p[3] == '}' and isinstance(p[2], list):
        p[0] = Group(contents=p[2])
    else:
        print([(it, type(it)) for it in p])
        assert False, '???'

def p_group_list(p):
    '''group_list : group COMMA group
                  | group COMMA group_list
    '''
    if isinstance(p[3], Group):
        p[0] = [p[1], p[3]]
    else:
        p[0] = [p[1],] + p[3]

def p_garbage(p):
    ''' garbage : garbagec_STRING
                | garbageb_STRING
    '''
    # drop garbage
    p[0] = None

def p_garbage_list(p):
    ''' garbage_list : garbage COMMA garbage
                | garbage COMMA garbage_list
    '''
    # drop garbage
    p[0] = None

### yacc related stuff - end ######################################

root = None
cur = None

LEXONLY = False

with open(INPUT) as f:
    lexer = lex.lex()
    lexer.level = 1
    parser = yacc.yacc()
    for l in f:
        l = l.strip()
        #print('LINE %02d: %s' % (lexer.lineno, l))

        if not LEXONLY:
            result = parser.parse(l)
            #result.update()
            print(result)
        else:
            lexer.input(l)
            while True:
                tok = lexer.token()
                if not tok:
                    break
                print(tok)

        lexer.lineno += 1

# vim:sts=4:sw=4:et:

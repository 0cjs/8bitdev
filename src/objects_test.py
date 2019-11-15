from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest
from    itertools import chain, count

####################################################################
#   Test fixtures and support

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/objects')
    return M

####################################################################
#   Tests

@pytest.mark.parametrize('char, num', [
    ('0', 0),  ('1', 1),    ('8', 8),  ('9', 9),
    ('A',10),  ('a',10),    ('F',15),  ('f',15),
    ('G',16),  ('g',16),    ('Z',35),  ('z',35),
])
def test_readascdigit_good(M, char, num):
    M.call(M.symtab.readascdigit, R(a=ord(char), C=1))
    assert R(a=num, C=0) == M.regs

@pytest.mark.parametrize('char', [
    '/',  ':', '@', '[', '`', '{',      # Chars either side of digits/letters
    '\x80', '\x81',
    '\xAF', '\xB0', '\xB9', '\xBa',     # MSb set: '/', '0', '9', ':'
    '\xDA', '\xFa', '\xFF',             # MSb set: 'Z', 'z'
    ])
def test_readascdigit_error(M, char):
    M.call(M.symtab.readascdigit, R(a=ord(char), C=0))
    assert R(C=1) == M.regs

def test_readascdigit_good_exhaustive(M):
    ''' Exhaustive test of all good values. Because we're nervous types.
        But the parametertized tests are easier for debugging errors.
    '''

    def ordrange(a, z):
        return range(ord(a), ord(z)+1)
    def readasc(a):
        M.call(M.symtab.readascdigit, R(a=a, C=1))
        return M.regs

    for num,char in zip(count(0), ordrange('0','9')):
        assert R(a=num, C=0) == readasc(char)
    for num,char in zip(count(10), ordrange('A', 'Z')):
        assert R(a=num, C=0) == readasc(char)
    for num,char in zip(count(10), ordrange('a', 'z')):
        assert R(a=num, C=0) == readasc(char)

def test_readascdigit_error_exhaustive(M):
    ''' Exhaustive test of all bad values. Because we're nervous types.
        But the parametertized tests are easier for debugging errors.
    '''
    badchars = chain(
        range(0,          ord('0')),
        range(ord('9')+1, ord('A')),
        range(ord('Z')+1, ord('a')),
        range(ord('z')+1,     255 ))
    for char in badchars:
        M.call(M.symtab.readascdigit, R(a=char, C=0))
        assert R(C=1) == M.regs

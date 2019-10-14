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
#   Tests: readascdigit

@pytest.mark.parametrize('char, num', [
    ('0', 0),  ('1', 1),    ('8', 8),  ('9', 9),
    ('A',10),  ('a',10),    ('F',15),  ('f',15),
    ('G',16),  ('g',16),    ('Z',35),  ('z',35),
    ('_', 40), ('\x7F', 40)
])
def test_readascdigit_good(M, char, num):
    M.call(M.symtab.readascdigit, R(a=ord(char), N=1))
    assert R(a=num, N=0) == M.regs

@pytest.mark.parametrize('char', [
    '/',  ':', '@',                     # Chars either side of digits/letters
    '\x80', '\x81',
    '\xAF', '\xB0', '\xB9', '\xBa',     # MSb set: '/', '0', '9', ':'
    '\xDA', '\xFa', '\xFF',             # MSb set: 'Z', 'z'
    ])
def test_readascdigit_error(M, char):
    M.call(M.symtab.readascdigit, R(a=ord(char), N=0))
    assert R(N=1) == M.regs

def test_readascdigit_good_exhaustive(M):
    ''' Exhaustive test of all good values. Because we're nervous types.
        But the parametertized tests are easier for debugging errors.
    '''

    def ordrange(a, z):
        return range(ord(a), ord(z)+1)
    def readasc(a):
        M.call(M.symtab.readascdigit, R(a=a, N=1))
        return M.regs

    for num,char in zip(count(0), ordrange('0','9')):
        assert R(a=num, N=0) == readasc(char)
    for num,char in zip(count(10), ordrange('A', '_')):
        assert R(a=num, N=0) == readasc(char), '{} ??? char {}'.format(num, char)
    for num,char in zip(count(10), ordrange('a', '\x7F')):
        assert R(a=num, N=0) == readasc(char), '{} ??? char {}'.format(num, char)

def test_readascdigit_error_exhaustive(M):
    ''' Exhaustive test of all bad values. Because we're nervous types.
        But the parametertized tests are easier for debugging errors.
    '''
    badchars = chain(
        range(0,          ord('0')),
        range(ord('9')+1, ord('A')),
        range(ord('_')+1, ord('a')),
        range(ord('\x7F')+1,  255 ),
        )
    for char in badchars:
        M.call(M.symtab.readascdigit, R(a=char, N=0))
        assert R(N=1) == M.regs, 'char {} should be bad'.format(char)

####################################################################
#   Tests: readhex

@pytest.mark.parametrize('input', [
    (b"/"),
    (b":"),
    (b"@"),
])
def test_bi_readhex_error(M, input):
    print('readhex_error:', input)
    S = M.symtab
    inbuf = 0x7000; outbuf = 0x7200

    M.deposit(inbuf, input)
    M.depword(S.inbuf, inbuf)
    M.depword(S.outbuf, outbuf)
    M.deposit(outbuf, [222]*5)      # sentinel

    with pytest.raises(M.Abort):
        M.call(S.bi_readhex, R(a=len(input)))
    #   Length is invalid, whatever it is.
    assert 222 == M.byte(outbuf+1)  # nothing further written

@pytest.mark.parametrize('input, bytes', [
    (b"0",               [0x00]),
    (b"5",               [0x05]),
    (b'67',              [0x067]),
    (b'89A',             [0x08, 0x9A]),
    (b'fedc',            [0xFE, 0xDC]),
    (b'fedcb',           [0x0F, 0xED, 0xCB]),
    (b"80000",           [0x08, 0x00, 0x00]),
    (b"0",               [0x00]),
    #(b"00000",           [0x00]),
])
def test_bi_readhex(M, input, bytes):
    print('bi_readhex:', input, type(input), bytes)
    S = M.symtab
    inbuf = 0x6FFE; outbuf = 0x71FE     # buffers cross page boundaries

    M.deposit(inbuf, input)
    M.depword(S.inbuf, inbuf)
    M.depword(S.outbuf, outbuf)
    size = len(bytes) + 2               # length byte + value + guard byte
    M.deposit(outbuf, [222] * size)     # 222 ensures any 0s really were written

    M.call(S.bi_readhex, R(a=len(input)))
    bvalue = M.bytes(outbuf+1, len(bytes))
    assert (len(bytes),     bytes,  222) \
        == (M.byte(outbuf), bvalue, M.byte(outbuf+size-1))

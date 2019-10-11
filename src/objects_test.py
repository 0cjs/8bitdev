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

def depint(M, addr, value):
    ''' Deposit a bigint in locations starting at `addr`.
        `addr` contains the length of the following bytes,
        which hold the value from LSB to MSB.
    '''

    next = addr + 1             # Skip length byte; filled in at end

    if value >= 0:              # Positive number; fill byte by byte
        while next == addr+1 or value > 0:
            value, byte = divmod(value, 0x100)
            M.deposit(next, [byte])
            next += 1
        if byte >= 0x80:        # MSbit = 1; sign in additional byte
            M.deposit(next, [0x00])
            next += 1

    else:                       # Negative: fill with two's complement values
        value = abs(value+1)    # two's complement = -(n+1)
        while next == addr+1 or value > 0:
            value, byte = divmod(value, 0x100)
            byte = 0xFF - byte  # two's complement
            M.deposit(next, [byte])
            next += 1
        if byte < 0x80:         # MSbit = 0; sign in additional byte
            M.deposit(next, [0xFF])
            next += 1

    #   Store the length
    M.deposit(addr, [next - (addr + 1)])

@pytest.mark.parametrize('value, bytes', [
    (0,             [0x00]),
    (1,             [0x01]),
    (127,           [0x7F]),
    (128,           [0x80, 0x00]),
    (255,           [0xFF, 0x00]),
    (256,           [0x00, 0x01]),
    (0x40123456,    [0x56, 0x34, 0x12, 0x40]),
    (0xC0123456,    [0x56, 0x34, 0x12, 0xC0, 0x00]),
    (-1,            [0xFF]),
    (-128,          [0x80]),
    (-129,          [0x7F, 0xFF]),
    (-255,          [0x01, 0xFF]),
    (-256,          [0x00, 0xFF]),
    (-257,          [0xFF, 0xFE]),
    (0-0x40123456,  [0xFF-0x56+1, 0xFF-0x34, 0xFF-0x12, 0xFF-0x40]),
    (0-0xC0123456,  [0xFF-0x56+1, 0xFF-0x34, 0xFF-0x12, 0xFF-0xC0, 0xFF]),
    ])
def test_depint(M, value, bytes):
    print('DEPOSIT', value, 'expecting', bytes)
    addr = 30000                    # arbitrary location for deposit
    size = len(bytes) + 2           # length byte + value + guard byte
    M.deposit(addr, [222] * size)   # 222 ensures any 0s really were written
    depint(M, addr, value)
    bvalue = M.bytes(addr+1, len(bytes))
    assert (len(bytes),   bytes,  222) \
        == (M.byte(addr), bvalue, M.byte(addr+size-1))

    #   Test against Python's conversion
    assert list(value.to_bytes(len(bytes), 'little', signed=True)) \
        == bvalue

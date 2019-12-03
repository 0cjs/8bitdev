from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest
from    itertools import chain, count

####################################################################
#   Test fixtures and support

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/bigint')
    return M

####################################################################
#   Tests: convascdigit

@pytest.mark.parametrize('char, num', [
    ('0', 0),  ('1', 1),    ('8', 8),  ('9', 9),
    ('A',10),  ('a',10),    ('F',15),  ('f',15),
    ('G',16),  ('g',16),    ('Z',35),  ('z',35),
    ('_', 40), ('\x7F', 40)
])
def test_convascdigit_good(M, char, num):
    M.call(M.symtab.convascdigit, R(a=ord(char), N=1))
    assert R(a=num, N=0) == M.regs

@pytest.mark.parametrize('char', [
    '/',  ':', '@',                     # Chars either side of digits/letters
    '\x80', '\x81',
    '\xAF', '\xB0', '\xB9', '\xBa',     # MSb set: '/', '0', '9', ':'
    '\xDA', '\xFa', '\xFF',             # MSb set: 'Z', 'z'
    ])
def test_convascdigit_error(M, char):
    M.call(M.symtab.convascdigit, R(a=ord(char), N=0))
    assert R(N=1) == M.regs

def test_convascdigit_good_exhaustive(M):
    ''' Exhaustive test of all good values. Because we're nervous types.
        But the parametertized tests are easier for debugging errors.
    '''

    def ordrange(a, z):
        return range(ord(a), ord(z)+1)
    def readasc(a):
        M.call(M.symtab.convascdigit, R(a=a, N=1))
        return M.regs

    for num,char in zip(count(0), ordrange('0','9')):
        assert R(a=num, N=0) == readasc(char)
    for num,char in zip(count(10), ordrange('A', '_')):
        assert R(a=num, N=0) == readasc(char), '{} ??? char {}'.format(num, char)
    for num,char in zip(count(10), ordrange('a', '\x7F')):
        assert R(a=num, N=0) == readasc(char), '{} ??? char {}'.format(num, char)

def test_convascdigit_error_exhaustive(M):
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
        M.call(M.symtab.convascdigit, R(a=char, N=0))
        assert R(N=1) == M.regs, 'char {} should be bad'.format(char)

####################################################################
#   Tests: readhex

#   Buffers used for testing deliberately cross page boundaries.
INBUF  = 0x6FFE
OUTBUF = 0x71FE

@pytest.mark.parametrize('input', [
    (b"/"),
    (b":"),
    (b"@"),
])
def test_bi_readhex_error(M, input):
    print('readhex_error:', input)
    S = M.symtab

    M.deposit(INBUF, input)
    M.depword(S.buf0ptr, INBUF)
    M.depword(S.buf1ptr, OUTBUF)
    M.deposit(OUTBUF, [222]*5)      # sentinel

    with pytest.raises(M.Abort):
        M.call(S.bi_readhex, R(a=len(input)))
    #   Length is invalid, whatever it is.
    assert 222 == M.byte(OUTBUF+1)  # nothing further written

@pytest.mark.parametrize('input, bytes', [
    (b"5",               [0x05]),
    (b'67',              [0x067]),
    (b'89A',             [0x08, 0x9A]),
    (b'fedc',            [0xFE, 0xDC]),
    (b'fedcb',           [0x0F, 0xED, 0xCB]),
    (b"80000",           [0x08, 0x00, 0x00]),
    (b"0",               [0x00]),
    (b"00000000",        [0x00]),
    (b"087",             [0x87]),
    (b"00000087",        [0x87]),
])
def test_bi_readhex(M, input, bytes):
    print('bi_readhex:', input, type(input), bytes)
    S = M.symtab

    M.deposit(INBUF, input)
    M.depword(S.buf0ptr, INBUF)
    M.depword(S.buf1ptr, OUTBUF)
    size = len(bytes) + 2               # length byte + value + guard byte
    M.deposit(OUTBUF, [222] * size)     # 222 ensures any 0s really were written

    M.call(S.bi_readhex, R(a=len(input)))
    bvalue = M.bytes(OUTBUF+1, len(bytes))
    assert (len(bytes),     bytes,  222,) \
        == (M.byte(OUTBUF), bvalue, M.byte(OUTBUF+size-1))

####################################################################
#   Tests: bi_read_dec

#   Memory locations of buffers used in tests.
#   These deliberately cross page boundaries for non-trivial buffer sizes.
TIN_ADDR  = 0x6FFE
TOUT_ADDR = 0x71FE
TSCR_ADDR = 0x73FE
TTMP_ADDR = 0x74FE

@pytest.mark.parametrize('signed, value', [
    ( 0, [0x03]), (-1, [0xFD]),
    (-1, [0xF4]),                         # min 1 byte input
    (-1, [0x0C]),                         # max 1 byte input
    ( 0, [0x19]),                         # max 1 byte input (unsigned)
    (-1, [0xFF, 0xF3]),
    (-1, [0xF3, 0x34]),                   # min 2 byte input
    (-1, [0x0C, 0xCC]),                   # max 2 byte input
    ( 0, [0x19, 0x99]),                   # max 2 byte input (unsigned)
    (-1, [0xFF, 0x87, 0x65, 0x43, 0x21]), # -20 million and a bit
    (-1, [0x02, 0xab, 0xcd, 0xef, 0x10]), # 11 billion or so
    (-1, [0xF4] + [0x00]*254),            # max length, approaching min value
    (-1, [0x0B] + [0xFF]*254),            # max length, approaching max value
    ( 0, [0x18] + [0xFF]*254),            # max length, (unsigned)
])
def test_bi_x10(M, signed, value):
    S = M.symtab

    decval   = int.from_bytes(value, byteorder='big', signed=signed)
    decval10 = decval * 10
    print('bi_x10: {} = {}'.format(list(map(hex, value)), decval))
    expected = decval10.to_bytes(len(value), byteorder='big', signed=signed)
    expected = list(expected)
    print('     -> {} = {}'.format(list(map(hex, expected)), decval10))
    buflen = len(value)

    #   Guard bytes around scratch buffer show we're not writing outside it.
    M.depword(TSCR_ADDR-1, 211)
    M.depword(TSCR_ADDR+buflen, 212)
    M.depword(S.bufSptr, TSCR_ADDR-1)

    M.deposit(TOUT_ADDR-1, [221] + value + [222])   # guard bytes
    M.depword(S.buf0ptr, TOUT_ADDR-1)

    M.deposit(S.buf0len, buflen)
    M.call(S.bi_x10, R(C=1))
    assert [211] == M.bytes(TSCR_ADDR-1, 1)
    assert [212] == M.bytes(TSCR_ADDR+buflen, 1)
    assert [221] + expected + [222] == M.bytes(TOUT_ADDR-1, len(value)+2)

    #   Turn this on to get a sense of how fast/slow this is.
    #assert not M.mpu.processorCycles

@pytest.mark.parametrize('sign, input, buf', [
    ( 0, b'0',      [0x00]),
    ( 0, b'255',    [0xFF]),
    (-1, b'1',      [0xFF]),
    (-1, b'128',    [0x80]),
    (-1, b'129',    [0x7F]),

    ( 0, b'0',      [0x00, 0x00]),
    ( 0, b'0',      [0x00, 0x00]),
    (-1, b'0',      [0x00, 0x00]),
    ( 0, b'0000',   [0x00, 0x00]),
    ( 0, b'9',      [0x00, 0x09]),
    (-1, b'3',      [0xFF, 0xFD]),
    ( 0, b'10',     [0x00, 0x0A]),

    #   Some smaller byte-boundry edge cases.
    #   These help test carry propagation.
    ( 0, b'32767',          [                  0x7F, 0xFF]),
    ( 0, b'32768',          [                  0x80, 0x00]),
    ( 0, b'2147483647',     [      0x7F, 0xFF, 0xFF, 0xFF]),
    ( 0, b'2147483648',     [      0x80, 0x00, 0x00, 0x00]),
    (-1, b'32768',          [                  0x80, 0x00]),
    (-1, b'32769',          [                  0x7F, 0xFF]),
    (-1, b'32769',          [            0xFF, 0x7F, 0xFF]),
    (-1, b'2147483648',     [      0x80, 0x00, 0x00, 0x00]),
    (-1, b'2147483648',     [0xFF, 0x80, 0x00, 0x00, 0x00]),
    (-1, b'2147483649',     [      0x7F, 0xFF, 0xFF, 0xFF]),
    (-1, b'2147483649',     [0xFF, 0x7F, 0xFF, 0xFF, 0xFF]),

    ( 0, b'65432',          [                              0xFF, 0x98]),
    ( 0, b'65432',          [                        0x00, 0xFF, 0x98]),
    ( 0, b'65432',          [                  0x00, 0x00, 0xFF, 0x98]),
    (-1, b'64321',          [                        0xFF, 0x04, 0xBF]),
    (-1, b'64321',          [            0xFF, 0xFF, 0xFF, 0x04, 0xBF]),
    ( 0, b'78912345678901', [      0x47, 0xC5, 0x36, 0x55, 0x24, 0x35]),
    (-1, b'78912345678901', [      0xB8, 0x3A, 0xC9, 0xAA, 0xDB, 0xCB]),
    (-1, b'78912345678901', [0xFF, 0xB8, 0x3A, 0xC9, 0xAA, 0xDB, 0xCB]),
])
def test_bi_read_decdigits(M, sign, input, buf):
    print('bi_read_decdigits:', input, buf)
    S = M.symtab

    if sign != 0: sign = 0xFF
    M.deposit(S.sign, [sign])

    osize = len(buf)
    M.deposit(S.buf0len, osize)
    M.deposit(TOUT_ADDR-1, [240] + [241]*osize + [242])
    M.depword(S.buf0ptr, TOUT_ADDR-1)

    M.deposit(TIN_ADDR-1, b'\xDD' + input + b'\xDF')    # guard bytes
    M.depword(S.buf1ptr, TIN_ADDR)
    M.deposit(S.buf1len, [len(input)])

    M.deposit(TSCR_ADDR-1, 250)                         # guard bytes
    M.deposit(TSCR_ADDR+osize, 251)
    M.depword(S.bufSptr, TSCR_ADDR-1)

    #   This value should be moderately different for many tests.
    xpreserved = (sum(map(int, input)) + sign) % 191 + 31

    #   XXX add `sign` param for positive/negative
    try:
        M.call(S.bi_read_decdigits, R(x=xpreserved))
    finally:
        print(M.regs)
        print('di={} buf0={}'.format(M.byte(S.curdigit),
            list(map(hex, M.bytes(TOUT_ADDR-1, osize+2)))))
    assert [240] + buf + [242] == M.bytes(TOUT_ADDR-1, osize+2)
    assert [250] == M.bytes(TSCR_ADDR-1, 1)
    assert [251] == M.bytes(TSCR_ADDR+osize, 1)
    assert R(x=xpreserved) == M.regs

@pytest.mark.skip(msg='These tests can take up to 10 seconds each to run')
@pytest.mark.parametrize('sign', [
    0x00,   # 3,531,433 cyles, about 3.5 seconds on 1 MHz 6502
    0xFF,   # 3,791,023 cyles, almost 4 seconds on 1 MHz 6502
])
def test_bi_read_decdigits_max(M, sign):
    S = M.symtab

    M.deposit(S.sign, [sign])

    input = b'9'*255
    input_i = int(input)
    if sign: input_i = -input_i
    expected = list(input_i.to_bytes(128, byteorder='big', signed=True))
    print(input_i, '\n', expected)

    M.deposit(TIN_ADDR-1, [122] + list(input) + [133])  # guard bytes
    M.depword(S.buf1ptr, TIN_ADDR)
    M.deposit(S.buf1len, [len(input)])

    osize = len(expected)
    M.deposit(S.buf0len, osize)
    M.deposit(TOUT_ADDR-1, [155] + [0]*osize + [166])
    M.depword(S.buf0ptr, TOUT_ADDR-1)
    M.depword(S.bufSptr, TSCR_ADDR-1)

    M.call(S.bi_read_decdigits)
    assert [155] + expected + [166] == list(M.bytes(TOUT_ADDR-1, osize+2))

    #   Uncommit to show number of cycles taken.
    #assert not M.mpu.processorCycles

@pytest.mark.parametrize('input, bytes', [
    #   Zero uses special-case code
    (b'0',              [0x00]),
    (b'+0',             [0x00]),
    (b'-0',             [0x00]),

    #   Single digits
    (b'1',              [0x01]),
    (b'-1',             [0xFF]),
    (b'9',              [0x09]),
    (b'-9',             [0xF7]),

    #   Stripping of leading zeros
    (b'0000',           [      0x00]),
    (b'+0001',          [      0x01]),
    (b'-0001',          [      0xFF]),
    (b'0000234',        [0x00, 0xEA]),
    (b'+000000234',     [0x00, 0xEA]),
    (b'-00000000234',   [0xFF, 0x16]),
    (b'-00000000345',   [0xFE, 0xA7]),

    #   Edge cases for sign extension
    (b'127',            [            0x7F]),
    (b'128',            [      0x00, 0x80]),
    (b'32767',          [      0x7F, 0xFF]),
    (b'32768',          [0x00, 0x80, 0x00]),
    (b'-128',           [            0x80]),
    (b'-129',           [      0xFF, 0x7F]),
    (b'-32768',         [      0x80, 0x00]),
    (b'-32769',         [0xFF, 0x7F, 0xFF]),

    #   Some biggish numbers
    (b'12345678',                   [0x00, 0xBC, 0x61, 0x4E]),
    (b'-1234567',                   [      0xED, 0x29, 0x79]),
    (b'-12345678',                  [0xFF, 0x43, 0x9E, 0xB2]),
    (b'999999999999',   [0x00, 0xE8, 0xD4, 0xA5, 0x0F, 0xFF]),
    (b'-999999999999',  [0XFF, 0X17, 0X2B, 0X5A, 0XF0, 0X01]),
])
def test_bi_read_dec(M, input, bytes):
    print('bi_read_dec:', input, bytes)
    S = M.symtab
    input = list(input)

    #   Allocate temp/scratch buffers. We do this here until we have an alloc
    #   system that will let bi_read_dec alloc its own temp/scratch buffers.
    #   We probably should be allocating a correctly sized buf rather than
    #   128 (big enough for all inputs) for better bounds checks.
    #   Note that the pointers point to 1 below the buffer itself.
    scratchlen = 128
    M.depword(S.bufSptr, TSCR_ADDR-1)
    M.deposit(TSCR_ADDR-1, [111] + [112]*scratchlen + [113])
    M.depword(S.buf0ptr, TTMP_ADDR-1)
    M.deposit(TTMP_ADDR-1, [121] + [122]*scratchlen + [123])

    M.depword(S.buf1ptr, TIN_ADDR)
    M.deposit(TIN_ADDR-1, [211] + input + [213])
    M.depword(S.buf2ptr, TOUT_ADDR)
    #   guard, output length, output value, guard
    M.deposit(TOUT_ADDR-1, [221, 222] + [223] * len(bytes) + [224])

    try:
        M.call(S.bi_read_dec, R(y=len(input)))
    except M.Abort as ex:
        print(ex)
        assert 0
    finally:
       #print('buf1ptr', hex(M.word(S.buf1ptr)), list(map(hex, M.bytes(M.word(S.buf1ptr), 8))))
        print('buf0ptr', hex(M.word(S.buf0ptr)), list(map(hex, M.bytes(M.word(S.buf0ptr), 8))))
        print('buf0len', hex(M.byte(S.buf0len)))
        print('   buf0       ', list(map(hex, M.bytes(M.word(S.buf0ptr), 8))))
       #print(' buf0 TTMP-1', list(map(hex, M.bytes(TTMP_ADDR-1, 12)))) #XXX
        print('buf2ptr', hex(M.word(S.buf2ptr)), list(map(hex, M.bytes(M.word(S.buf2ptr), 8))))
       #print(' buf2 TOUT-1', list(map(hex, M.bytes(TOUT_ADDR-1, 12)))) #XXX

    #   Assert scratch buffers were not written out of bounds
    assert 111 == M.byte(TSCR_ADDR-1)
    assert 113 == M.byte(TSCR_ADDR+scratchlen)
    assert 121 == M.byte(TTMP_ADDR-1)
    assert 123 == M.byte(TTMP_ADDR+scratchlen)

    #   Assert input buffer is unchanged
    assert [211] + input + [213] == M.bytes(TIN_ADDR-1, len(input)+2)

    #   Assert output buffer is correct and without out-of-bounds writes.
    assert [221, len(bytes)] + bytes + [224] \
        == M.bytes(TOUT_ADDR-1, len(bytes)+3)

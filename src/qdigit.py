from    itertools import chain, count
import  pytest

@pytest.mark.parametrize('char, num', [
    ('0', 0),  ('1', 1),    ('8', 8),  ('9', 9),
    ('A',10),  ('a',10),    ('F',15),  ('f',15),
    ('G',16),  ('g',16),    ('Z',35),  ('z',35),
    ('_', 40), ('\x7F', 40)
])
def test_qdigit_good(m, R, char, num):
    m.call(m.symtab.qdigit, R(a=ord(char), N=1))
    assert R(a=num, N=0) == m.regs

@pytest.mark.parametrize('char', [
    '/',  ':', '@',                     # Chars either side of digits/letters
    '\x80', '\x81',
    '\xAF', '\xB0', '\xB9', '\xBa',     # MSb set: '/', '0', '9', ':'
    '\xDA', '\xFa', '\xFF',             # MSb set: 'Z', 'z'
    ])
def test_qdigit_error(m, R, char):
    m.call(m.symtab.qdigit, R(a=ord(char), N=0))
    assert R(N=1) == m.regs

def test_qdigit_good_exhaustive(m, R):
    ''' Exhaustive test of all good values.

        Not just because we're nervous types, but also because these are
        useful for debugging new implementations where it's more convenient
        to see just the "next" error rather than lots of errors.

        As well, looping through the values in one test speeds things up by
        saving on setup/teardown for 256 tests.
    '''

    def ordrange(a, z):
        return range(ord(a), ord(z)+1)
    def readasc(a):
        print('{:02X}'.format(char), end=' ')
        m.call(m.symtab.qdigit, R(a=a, N=1))
        return m.regs

    for num,char in zip(count(0), ordrange('0','9')):
        assert R(a=num, N=0) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))
    for num,char in zip(count(10), ordrange('A', '_')):
        assert R(a=num, N=0) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))
    for num,char in zip(count(10), ordrange('a', '\x7F')):
        assert R(a=num, N=0) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))

def test_qdigit_error_exhaustive(m, R):
    ''' Exhaustive test of all bad values.
        See further comments on `test_qdigit_good_exhaustive`.
    '''
    badchars = chain(
        range(0,          ord('0')),
        range(ord('9')+1, ord('A')),
        range(ord('_')+1, ord('a')),
        range(ord('\x7F')+1,  255 ),
        )
    for char in badchars:
        m.call(m.symtab.qdigit, R(a=char, N=0))
        assert R(N=1) == m.regs, \
            'input ${:02X} {} should be bad'.format(char, repr(chr(char)))

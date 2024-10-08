''' Generic tests for ``qdigit`` routine.

    These functions are imported into the machine-specific test file after
    setting up the test rig to load the ``qdigit`` function and a pytest
    fixture `REG` that returns a function to create a `Registers` object.
    The function takes two parameters: the value for the input/return
    register (typically the accumulator) and True/False to indicate success
    or failure (which sets the machine-specific flag to the indicated
    value). Thus ``REG(13, True)`` should return an object such as
    ``Registers(a=13, N=0)``.
'''

from    itertools import chain, count
import  pytest

@pytest.mark.parametrize('char, num', [
    ('0', 0),  ('1', 1),    ('8', 8),  ('9', 9),
    ('A',10),  ('a',10),    ('F',15),  ('f',15),
    ('G',16),  ('g',16),    ('Z',35),  ('z',35),
    ('_', 40), ('\x7F', 40)
])
def test_qdigit_good(m, REG, char, num):
    m.call(m.symtab.qdigit, REG(ord(char), False))
    assert REG(num, True) == m.regs

@pytest.mark.parametrize('char', [
    '/',  ':', '@',                     # Chars either side of digits/letters
    '\x80', '\x81',
    '\xAF', '\xB0', '\xB9', '\xBa',     # MSb set: '/', '0', '9', ':'
    '\xDA', '\xFa', '\xFF',             # MSb set: 'Z', 'z'
    ])
def test_qdigit_error(m, REG, char):
    m.call(m.symtab.qdigit, REG(ord(char), True))
    assert REG(None, False) == m.regs

def test_qdigit_good_exhaustive(m, REG):
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
        m.call(m.symtab.qdigit, REG(a, False))
        return m.regs

    for num,char in zip(count(0), ordrange('0','9')):
        assert REG(num, True) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))
    for num,char in zip(count(10), ordrange('A', '_')):
        assert REG(num, True) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))
    for num,char in zip(count(10), ordrange('a', '\x7F')):
        assert REG(num, True) == readasc(char), \
            'failed on input ${:02X} {}'.format(char, repr(chr(char)))

def test_qdigit_error_exhaustive(m, REG):
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
        m.call(m.symtab.qdigit, REG(char, True))
        assert REG(None, False) == m.regs, \
            'input ${:02X} {} should be bad'.format(char, repr(chr(char)))

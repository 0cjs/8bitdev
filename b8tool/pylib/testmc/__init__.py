''' testmc -- test framework for microcomputer systems
'''

from    numbers  import Number

__all__ = ['LB', 'MB', 'tmc_tid', 'sym_tid']

def LB(n):
    ' Return the lowest byte (LSB) of a value. '
    return n & 0xFF

def MB(n):
    ''' Return the "middle" or 2nd-lowest byte of a value.
        This is the MSB of a 16-bit value.
    '''
    return (n >> 8) & 0xFF

def tmc_tid(x):
    ''' `testmc` pytest ID. This helps generate nicer test IDs for pytest
        parametrized tests, via ``parametrize(..., ids=testmc_tid)``, for
        the typical parameter data used in tests using `testmc`.

        - If `x` is a `Number` and ≥ 2, return a hex representation
          prefixed with ``$``.
        - If `x` is a `str`, return its `repr` to put quotes around it.
          (This helps avoid confusion between hex digits and letters.)
        - Otherwise return `x`.
    '''
    if isinstance(x, Number) and x >= 2:
        return '${:02X}'.format(x)
    elif isinstance(x, str):
        return repr(x)
    else:
        return x

def sym_tid(symtab, multi=True):
    ''' Return a function that returns symbol names from values, if a
        symbol in `symtab` has that value. This helps to generate more
        readable test IDs for pytest parametrized tests that use symbols.
        Values smaller than 5 and any value without a symbol will be
        passed to `tmc_tid()`. (Not translating small values avoids
        significant noise.)

        Typical usage, where `S` is the symtab::

            @pytest.mark.parametrize('f', [S.foo, S.bar], ids=sym_tid(S))

        Some values may have multiple symbols associated with them. If
        `multi` is `True`, all values will be returned (in ASCII order)
        separated by commas. If `multi` is `False`, only the value that
        sorts highest will be returned.
    '''
    def tid(value):
        if isinstance(value, Number) and value <= 5:
            return tmc_tid(value)
        names = tuple( s.name for s in sorted(symtab.valued(value)) )
        if not names:
            return tmc_tid(value)
        else:
            if multi:   return ','.join(names)
            else:       return names[0]

    return tid

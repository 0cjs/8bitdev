''' testmc -- test framework for microcomputer systems
'''

from    numbers  import Number

__all__ = ['LB', 'MB', 'tmc_tid']

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

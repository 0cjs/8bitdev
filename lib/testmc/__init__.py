''' testmc -- test framework for microcomputer systems
'''

from    numbers  import Number

__all__ = ['hexid', 'LSB', 'MSB']

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

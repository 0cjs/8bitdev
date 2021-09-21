''' testmc pytest support functions

    To avoid accidentally overriding pytest hooks from elsewhere, ``import
    *`` from this module will bring in only the support functions for
    building hooks.

    However, you may also import pre-built hooks explictly::

        from testmc.pytest import pytest_assertrepr_compare

'''
from    testmc.generic      import GenericRegisters as GR

#   Avoid non-explicit imports of actual pytest hook names.
__all__ = ['assertrepr_compare']

def assertrepr_compare(op, left, right):
    ''' Nicer assertion error displays for comparisons between testmc objects.

        This has the same parameters and return value (a sequence of `str`
        or `None`) as `pytest_assertrepr_compare`. You can include this in
        your own `pytest_assertrepr_compare` function, trying other formats
        if this returns `None`.
    '''
    if isinstance(left, GR) and isinstance(right, GR) and op == "==":
        return (
            'Unexpected {} values:'.format(right.__class__.__name__),
            repr(left), repr(right),
        )

def pytest_assertrepr_compare(op, left, right):
    ''' For `testmc` objects, override the standard pytest assertion
        comparison failure display. If you have other overrides as well,
        you probably want instead to import `assertrepr_compare()` and
        build your own version of this function.
    '''
    return assertrepr_compare(op, left, right)

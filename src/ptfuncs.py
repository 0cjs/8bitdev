' Convenience functions for use with pytest. '

#   Other things to consider adding as we want them:
#   • param(): = pytest.mark.parametrize
#   • ID(): pytest.param(*args, id=id)
#   • P(): = pytest.param, or maybe ID(id, …) instead

import  pytest

def XFAIL(*args, id=None, **kwargs):
    ''' Mark test parameters as (strictly) expected to fail.
        Just wrap XFAIL(…) around that parameter or list of parameters.
        Optional params include: ``id=…``, ``reason=…``.
    '''
    return pytest.param(*args, id=id,
        marks=pytest.mark.xfail(strict=True, **kwargs))

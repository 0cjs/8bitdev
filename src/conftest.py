import  pytest

#   Nicer assertion error display for various testmc objects.
from    testmc.pytest  import pytest_assertrepr_compare

@pytest.fixture
def m(request):
    ''' A simulated machine with the object file loaded.

        The caller must have two global variables defined in its
        module:
        - `Machine`: The class of the CPU/machine simulator to instantiate.
          Normally this is simply imported from `testmc`.
        - `object_file`: A `str` giving the path to the object file to load
          into the machine, relative to ``.build/obj/``.
    '''
    Machine = getattr(request.module, 'Machine')
    m = Machine()
    #   XXX This is probably not the best way to find this file; it makes
    #   this dependent on the CWD being the project root dir above .build/.
    m.load('.build/obj/' + getattr(request.module, 'object_file'))
    return m

#   These rely on pytest running the m() fixture only once per test, even
#   though both these fixtures and the test itself use it. I'm not sure if
#   this behaviour is documented, but it makes sense given that pytest
#   maintains careful control over the scope (test/module/etc.) in which a
#   fixture is used.

@pytest.fixture
def S(m):
    ''' The `Machine.symtab` attribute of the machine object produced by
        the `m` fixture.
    '''
    return m.symtab

@pytest.fixture
def R(m):
    ''' The `Machine.registers` attribute of the machine object produced by
        the `m` fixture.
    '''
    return m.Registers

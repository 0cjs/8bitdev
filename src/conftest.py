import  pytest

@pytest.fixture
def M(request):
    ''' A simulated machine with the object file loaded.

        The caller must have two global variables defined in its
        module:
        - `Machine`: The class of the CPU/machine simulator to instantiate.
          Normally this is simply imported from `testmc`.
        - `object_file`: A `str` giving the path to the object file to load
          into the machine, relative to ``.build/obj/``.
    '''
    Machine = getattr(request.module, 'Machine')
    M = Machine()
    #   XXX This is probably not the best way to find this file; it makes
    #   this dependent on the CWD being the project root dir above .build/.
    M.load('.build/obj/' + getattr(request.module, 'object_file'))
    return M

#   These rely on pytest running the M() fixture only once per test, even
#   though both these fixtures and the test itself use it. I'm not sure if
#   this behaviour is documented, but it makes sense given that pytest
#   maintains careful control over the scope (test/module/etc.) in which a
#   fixture is used.

@pytest.fixture
def S(M):
    ''' The `Machine.symtab` attribute of the machine object produced by
        the `M` fixture.
    '''
    return M.symtab

@pytest.fixture
def R(M):
    ''' The `Machine.registers` attribute of the machine object produced by
        the `M` fixture.
    '''
    return M.Registers

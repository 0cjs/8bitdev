from    testmc.m6502 import  Machine
import  pytest

@pytest.fixture
def M(request):
    ''' A simulated machine with the object file loaded. The calling
        module should define a global `object_file` bound to a string
        giving the path to the object file relative to ``.build/obj/``.
    '''
    M = Machine()
    #   XXX This is probably not the best way to find this file; it makes
    #   this dependent on the CWD being the project root dir above .build/.
    M.load('.build/obj/' + getattr(request.module, 'object_file'))
    return M

@pytest.fixture
def S(M):
    ''' The `Machine.symtab` of the machine object produced by the
        `M` fixture.
    '''
    #   This relies on pytest running the M() fixture only once per test,
    #   even though both this fixture and the test itself use it. I'm not
    #   sure if this behaviour is documented, but it makes sense.
    return M.symtab

from    testmc.m6502 import  Machine, Registers as R
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/objects.p')
    return M

####################################################################
#   Tests

def test_donothing(M):
    M.call(M.symtab.donothing)

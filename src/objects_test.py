from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest
from    itertools import chain, count

####################################################################
#   Test fixtures and support

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/objects')
    return M

####################################################################
#   Tests

def test_donothing(M):
    M.call(M.symtab.donothing)

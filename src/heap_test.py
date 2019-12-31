from    testmc.m6502 import  Machine, Registers as R
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/heap.p')
    return M

def test_heapinit(M):
    S = M.symtab
    heapstart = 0x0FFE                      # heap header crosses a page

    M.depword(S.heapstart, heapstart)
    M.call(S.heapinit, R(a=0x10, x=0x14))   #   16-byte heap

    assert [0x1014, 0x1002] == M.words(heapstart, 2)

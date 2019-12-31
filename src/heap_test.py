from    testmc.m6502 import  Machine, Registers as R
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/heap.p')
    return M

####################################################################
#   Heapdata types

def hdtype(n):
    return (n << 2) | 1

HDT_FREE        = hdtype(0)     # free block object
HDT_ENVHEADER   = hdtype(2)     # environment object header
HDT_ENVENTRY    = hdtype(3)     # environment object binding entry

def test_HDT_values(M):
    ''' Ensure this test code has defined with the same values all of
        the HDT_* constants defined in the assembly source.
    '''
    for name, value in M.symtab:
        if not name.startswith('HDT_'): continue
        assert globals()[name] == value, name

####################################################################
#   Tests

@pytest.mark.parametrize('size', (
    0x004, # minimum heap size
    0x008, 0x010,
    0x0F8, 0x0FC, 0x100, 0x104, 0x108,
    0x4F8, 0x4FC, 0x500, 0x504, 0x508,
    0xEF00, # massive heap, most of memory
))
def test_heapinit(M, size):
    S = M.symtab
    start = 0x0FFC              # Ensure heap crosses a page

    M.depword(S.heapstart, start)
    M.depword(S.heapend, start+size)
    M.call(S.heapinit)

    pos = 0; remain = size

    #   Max-size empty blocks on heap
    while remain >= 0x100:
        assert [HDT_FREE, 0xFE] == M.bytes(start+pos, 2), \
            'pos: {:04x}'.format(pos)
        pos    += 0x100
        remain -= 0x100

    #   Final remaining-size block on heap
    if remain > 0:
        assert [HDT_FREE, remain - 2] == M.bytes(start+pos, 2), \
            'pos: {:04x}'.format(pos)

    #   First free block object is at the start of the heap.
    assert start == M.word(S.heapff)

@pytest.mark.parametrize('start, end', (
    (0x0FFF, 0x2000),
    (0x1001, 0x2000), (0x1002, 0x2000), (0x1003, 0x2000), (0x1005, 0x2000),
    (0x1000, 0x10FB),
    (0x1000, 0x10FD), (0x1000, 0x10FE), (0x1000, 0x10FF), (0x1000, 0x2001)
))
def test_heapinit_misaligned(M, start, end):
    ' Ensure that we BRK if a misaligned start or end value is given. '
    S = M.symtab
    M.depword(S.heapstart, start)
    M.depword(S.heapend, end)
    with pytest.raises(M.Abort):
        M.call(S.heapinit)

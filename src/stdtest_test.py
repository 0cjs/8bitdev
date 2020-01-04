from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/stdtest.p')
    return M

def test_ds_db_dw(M):
    S = M.symtab
    start = S.defalloctest
    assert S.dstest0            == start
    assert S.dstest1            == start+3
    assert S.dbtest             == start+4
    assert b'\x00abc\xFF\xFF'   == bytes(M.bytes(S.dbtest, 6))
    assert S.dwtest             == start+10
    assert 0xABCD               == M.word(S.dwtest)
    assert (0xCD, 0xAB)         == (M.byte(S.dwtest), M.byte(S.dwtest+1))

def test_zds(M):
    S = M.symtab

    #   The initial value of __ZDS_loc at the zdstest0 label.
    #   This value $10 assumes that zdstest1 is the first ZDS in this assembly.
    zloc = 0x10

    assert 0xFF        < S.zdstest0
    assert 0xFF       >= S.zdstest1
    assert zloc       == S.zdstest1
    assert 0xFF       >= S.zdstest2
    assert zloc+3     == S.zdstest2
    assert 0xFF        < S.zdstest3
    assert S.zdstest3 == S.zdstest0 + 1     # Original location ctr. preserved

@pytest.mark.parametrize('input, expected', (
    (0x0000, 0x0001),
    (0x1234, 0x1235),
    (0x00FE, 0x00FF),
    (0x00FF, 0x0100),
    (0xFF00, 0xFF01),
    (0xFFFF, 0x0000),
))
def test_incw(M, input, expected):
    incw = M.symtab.incwtest
    data = M.symtab.incwdata
    r    = R(a=0x12, x=0x34, y=0x56)

    M.depword(data, input)
    M.call(incw, r)
    assert r == M.regs
    assert expected == M.word(data)

@pytest.mark.parametrize('inp, exp', (
    (0x1F9, 0x1FC), (0x1FA, 0x1FC), (0x1FB, 0x1FC), (0x1FC, 0x1FC),
    (0x1FD, 0x200), (0x1FE, 0x200), (0x1FF, 0x200), (0x200, 0x200),
    (0xFFFF, 0x0000), (0x0000, 0x0000),
))
def test_dwalign(M, inp, exp):
    dwaligntest, data = M.symtab.dwaligntest, M.symtab.dwaladdr
    preservedregs = R(x=87, y=65)
    M.depword(data, inp)
    M.call(dwaligntest, preservedregs)
    assert           exp == M.word(data)
    assert preservedregs == M.regs

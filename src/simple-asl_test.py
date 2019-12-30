from    testmc.m6502 import  Machine, Registers as R
import  pytest


@pytest.fixture
def M():
    M = Machine()

    #   XXX Not the best way to find this file: duplicates definition
    #   of $buildir in Test and dependent on CWD.
    M.load('.build/obj/src/simple-asl.p')

    #   Confirm correct file is loaded
    ident = M.symtab.ident
    assert 0x240 == ident
    ident_str = "simple-asl.a65"
    assert ident_str == M.str(ident, len(ident_str))

    return M

def test_addxy(M):
    S = M.symtab
    M.call(S.addxy, R(x=0x2A, y=0x33, C=1))
    expected = 0x2A + 0x33
    assert expected == M.byte(S.xybuf)
    assert R(a=expected, x=0x2A, y=0x33) == M.regs

@pytest.mark.parametrize('len', (1, 2, 16, 255))    # len must be at least 1
def test_fill(M, len):
    S = M.symtab
    base = 0x1234       # Fill does not include base address

    guard = [0xFF] * 2
    M.deposit(base-2, [0xFF]*260)

    #   There's also a temporary symbol in here but we currently have
    #   neither a reliable way to access it or any good use for it.
    M.depword(S.fillbase, base)
    M.call(S.fill, R(y=len))
    assert guard + [0xFF] + [0]*len + guard == M.bytes(base-2, len+5)

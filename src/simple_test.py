from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    M = Machine()

    #   XXX Not the best way to find this file: duplicates definition
    #   of $buildir in Test and dependent on CWD.
    M.load('.build/obj/simple')
    ident = M.symtab.ident

    #   Confirm correct file is loaded
    assert 0x400 == ident
    ident_str = "simple.a65"
    assert ident_str == M.str(ident, len(ident_str))

    return M

def test_addxy(M):
    S = M.symtab
    M.deposit(0x8000, [
        I.JSR, S.addxy & 0xff, (S.addxy & 0xff00) >> 8,
        I.NOP, I.NOP, I.NOP, I.NOP ])
    assert S.addxy == M.word(0x8001)     # Did we set it up right?
    M.setregs(pc=S.addxy, x=0x12, y=0x34)
    #   XXX Test entry with carry flag set.
    M.deposit(S.xybuf, [0xff])
    M.step(7+2)      # Execute a couple NOPs for safety
    assert R(a=0x12+0x34) == M.regs
    assert 0x12+0x34 == M.byte(S.xybuf)

def test_jmpptr(M):
    M.load('.build/obj/simple')
    S = M.symtab
    #   Step by step testing, to make _really_ sure the instructions
    #   are doing what I intend. Maybe overkill?
    M.setregs(pc=S.jmpabs, a=2)
    M.step()                 # asl
    assert R(a=4) == M.regs
    M.step()                 # tax
    M.step()                 # lda jmplist,X  ;LSB
    assert R(a=0xBC) == M.regs
    M.step()                 # sta jmpptr
    M.step()                 # inx
    M.step()                 # lda jmplist,X  ;MSB
    M.step()                 # sta jmpptr+1
    assert 0x9abc == M.word(S.jmpptr)
    M.step()                 # jmp [jmpptr]
    assert R(pc=0x9ABC) == M.regs
    #print(hex(M.mpu.pc), hex(M.mpu.a), hex(M.mpu.x))

def test_jmpabsrts(M):
    S = M.symtab
    M.setregs(pc=S.jmpabsrts, a=1)
    M.stepto(I.RTS)
    assert 0x5678-1 == M.spword()
    M.step()                 # rts
    assert R(pc=0x5678) == M.regs

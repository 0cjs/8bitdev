from tmpu import TMPU, Regs as R

JSR     = 0x20
NOP     = 0xEA

def test_addxy():
    tmpu = TMPU()

    #   XXX Not the best way to find this file: duplicates definition
    #   of $buildir in Test and dependent on CWD.
    tmpu.load('.build/obj/simple')
    S = tmpu.symtab

    #   Confirm we've loaded the correct file.
    assert S.ident == 0x400
    ident_str = 'simple.a65'
    assert ident_str == tmpu.strAt(S.ident, len(ident_str))

    tmpu.deposit(0x8000, [
        JSR, S.addxy & 0xff, (S.addxy & 0xff00) >> 8,
        NOP, NOP, NOP, NOP ])
    assert S.addxy == tmpu.wordAt(0x8001)     # Did we set it up right?
    tmpu.setregs(pc=S.addxy, x=0x12, y=0x34)
    #   XXX Test entry with carry flag set.
    tmpu.deposit(S.xybuf, [0xff])
    tmpu.step(7+2)      # Execute a couple NOPs for safety
    assert R(a=0x12+0x34) == tmpu.regs
    assert 0x12+0x34 == tmpu.byteAt(S.xybuf)

def test_jmpptr():
    tmpu = TMPU()
    tmpu.load('.build/obj/simple')
    S = tmpu.symtab

    ident_str = "simple.a65"
    assert ident_str == tmpu.strAt(S.ident, len(ident_str))

    #   Step by step testing, to make _really_ sure the instructions
    #   are doing what I intend. Maybe overkill?

    tmpu.setregs(pc=S.jmpabs, a=2)
    tmpu.step()                 # asl
    assert R(a=4) == tmpu.regs
    tmpu.step()                 # tax
    tmpu.step()                 # lda jmplist,X  ;LSB
    assert R(a=0xBC) == tmpu.regs
    tmpu.step()                 # sta jmpptr
    tmpu.step()                 # inx
    tmpu.step()                 # lda jmplist,X  ;MSB
    tmpu.step()                 # sta jmpptr+1
    assert 0x9abc == tmpu.wordAt(S.jmpptr)
    tmpu.step()                 # jmp [jmpptr]
    assert R(pc=0x9ABC) == tmpu.regs

    #print(hex(tmpu.mpu.pc), hex(tmpu.mpu.a), hex(tmpu.mpu.x))

def test_jmpabsrts():
    tmpu = TMPU()
    tmpu.load('.build/obj/simple')
    S = tmpu.symtab

    ident_str = "simple.a65"
    assert ident_str == tmpu.strAt(S.ident, len(ident_str))

    tmpu.setregs(pc=S.jmpabsrts, a=1)
    tmpu.step()                 # asl
    tmpu.step()                 # tax
    tmpu.step()                 # lda MSB
    tmpu.step()                 # pha
    tmpu.step()                 # lda ;LSB
    tmpu.step()                 # pha
    tmpu.step()                 # rts
    assert R(pc=0x5678) == tmpu.regs

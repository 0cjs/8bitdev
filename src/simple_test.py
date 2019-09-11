from tmpu import TMPU

JSR     = 0x20
NOP     = 0xEA

def test_addxy():
    tmpu = TMPU()

    #   XXX Not the best way to find this file: duplicates definition
    #   of $buildir in Test and dependent on CWD.
    with open('.build/obj/simple.bin', 'rb') as f:
        tmpu.load_bin(f.read())

    #   XXX We should be looking up these symbol locations from a
    #   debugger symbol table file.
    ident = 0x400
    addxy = 0x40a
    xybuf = 0x416

    #   Confirm we've loaded the correct file.
    ident_str = "simple.a65"
    assert ident_str == tmpu.strAt(ident, len(ident_str))

    tmpu.deposit(0x8000, [
        JSR, addxy & 0xff, (addxy & 0xff00) >> 8,
        NOP, NOP, NOP, NOP ])
    assert addxy == tmpu.wordAt(0x8001)     # Did we set it up right?
    tmpu.setregs(pc=addxy, x=0x12, y=0x34)
    #   XXX Test entry with carry flag set.
    tmpu.deposit(xybuf, [0xff])
    tmpu.step(7+2)      # Execute a couple NOPs for safety
    tmpu.assertregs(a=0x12+0x34)
    assert 0x12+0x34 == tmpu.byteAt(xybuf)

def test_jmpptr():
    tmpu = TMPU()
    with open('.build/obj/simple.bin', 'rb') as f:
        tmpu.load_bin(f.read())

    ident       = 0x0400
    jmpptr      = 0x0010
    jmpabs      = 0x0417
    jmplist     = 0x0427

    ident_str = "simple.a65"
    assert ident_str == tmpu.strAt(ident, len(ident_str))

    #   Step by step testing, to make _really_ sure the instructions
    #   are doing what I intend. Maybe overkill?

    tmpu.setregs(pc=jmpabs, a=2)
    tmpu.step()                 # asl
    tmpu.assertregs(a=4)
    tmpu.step()                 # tax
    tmpu.step()                 # lda jmplist,X  ;LSB
    tmpu.assertregs(a=0xbc)
    tmpu.step()                 # sta jmpptr
    tmpu.step()                 # inx
    tmpu.step()                 # lda jmplist,X  ;MSB
    tmpu.step()                 # sta jmpptr+1
    assert 0x9abc == tmpu.wordAt(jmpptr)
    tmpu.step()                 # jmp [jmpptr]
    tmpu.assertregs(pc=0x9abc)

    #print(hex(tmpu.mpu.pc), hex(tmpu.mpu.a), hex(tmpu.mpu.x))

def test_jmpabsrts():
    tmpu = TMPU()
    with open('.build/obj/simple.bin', 'rb') as f:
        tmpu.load_bin(f.read())

    ident       = 0x0400
    jmplist     = 0x0427
    jmpabsrts   = 0x0437

    ident_str = "simple.a65"
    assert ident_str == tmpu.strAt(ident, len(ident_str))

    tmpu.setregs(pc=jmpabsrts, a=1)
    tmpu.step()                 # asl
    tmpu.step()                 # tax
    tmpu.step()                 # lda MSB
    tmpu.step()                 # pha
    tmpu.step()                 # lda ;LSB
    tmpu.step()                 # pha
    tmpu.step()                 # rts
    tmpu.assertregs(pc=0x5678)

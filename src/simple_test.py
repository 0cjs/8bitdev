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

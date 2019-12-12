from    testmc.m6502 import  Machine, Registers as R
import  pytest

def test_addxy_call():
    #   Manually set locations until SymTab support is added.
    M = Machine()
    M.load('.build/obj/src/simple-asl.p')
    addxy = 0x260
    xybuf = 0x26C

    M.call(addxy, R(x=0x2A, y=0x33, C=1))
    expected = 0x2A + 0x33
    assert expected == M.byte(xybuf)
    assert R(a=expected, x=0x2A, y=0x33) == M.regs

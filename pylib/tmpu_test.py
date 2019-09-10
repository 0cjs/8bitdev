from tmpu import TMPU

def test_testmpu():
    tmpu = TMPU()
    assert [0]*0x10000 == tmpu.mpu.memory

def test_deposit_list():
    tmpu = TMPU()
    tmpu.deposit(6, [9, 2, 3, 8])
    assert [0]*6 + [9, 2, 3, 8] + [0]*(0x10000 - 6 - 4) == tmpu.mpu.memory

def test_regs():
    tmpu = TMPU()
    tmpu.assertregs(0, 0, 0, 0, 0xff)

    tmpu.setregs(y=4, a=2)
    tmpu.assertregs(y=4, a=2)
    tmpu.assertregs(0000, 2, 0, 4, 0xff)

    tmpu.setregs(1, 3, 5, 7, 0x80)
    tmpu.assertregs(1, 3, 5, 7, 0x80)

    #   We should never compare P status register bits 5 and 4.
    #   Some of these values for P are probably invalid in this
    #   emulator, but we never run in these states.
    tmpu.assertregs(p=0b00110000); tmpu.assertregs(p=0)
    tmpu.mpu.p = 0
    tmpu.assertregs(p=0b00110000); tmpu.assertregs(p=0)
    tmpu.mpu.p = 0xff
    tmpu.assertregs(p=0b11001111); tmpu.assertregs(p=0xff)

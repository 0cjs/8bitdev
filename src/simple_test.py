from tmpu import TMPU

LDAi    = 0xA9      # immediate
LDXz    = 0xA6      # zero page
NOP     = 0xEA

def test_mpu_step():
    ''' Test a little program we've hand assembled here to show
        that we're using the MPU API correctly.
    '''
    #   See py65/monitor.py for examples of how to set up and use the MPU.
    tmpu = TMPU()

    tmpu.deposit(7, [0x7E])
    tmpu.deposit(0x400, [
        LDAi, 0xEE,
        LDXz, 0x07,
        NOP,
    ])
    assert   0x07 == tmpu.mpu.ByteAt(0x403)
    assert 0xEEA9 == tmpu.mpu.WordAt(0x400)  # LSB, MSB

    tmpu.assertregs(0, 0, 0, 0)
    tmpu.setregs(pc=0x400)

    tmpu.step(); tmpu.assertregs(0x402, a=0xEE)
    tmpu.step(); tmpu.assertregs(0x404, x=0x7E)
    tmpu.step(); tmpu.assertregs(0x405, 0xEE, 0x7E, 0x00)

from py65.devices.mpu6502 import MPU

LDAi    = 0xA9      # immediate
LDXz    = 0xA6      # zero page
NOP     = 0xEA

####################################################################
#   Test framework

class TMPU():

    def __init__(self):
        self.mpu = MPU()

    def setregs(self, pc=None, a=None, x=None, y=None, sp=None):
        m = self.mpu
        if pc is not None:  m.pc = pc
        if  a is not None:   m.a =  a
        if  x is not None:   m.x =  x
        if  y is not None:   m.y =  y
        if sp is not None:  m.sp = sp
        #   We don't do processor status register here as flags should
        #   be set/reset individually, particularly because we should
        #   avoid ever changing unused bits 5 and 6.

    def assertregs(self, pc=None, a=None, x=None, y=None, sp=None, p=None):
        ''' Assert any registers specified have given values.

            This needs to be tweaked to produce better output on failure.
            - Hex comparisions would be nice.
            - Can we end the stack trace one level above this?
        '''
        m = self.mpu
        if pc is not None:  assert pc == m.pc
        if  a is not None:  assert  a == m.a
        if  x is not None:  assert  x == m.x
        if  y is not None:  assert  y == m.y
        if sp is not None:  assert sp == m.sp
        if  p is not None:
            #   Ignore unused bits 5 and 4 in the processor status register.
            assert  p & 0b11001111 == m.p & 0b11001111

    def deposit(self, addr, values):
        self.mpu.memory[addr:addr+len(values)] = values

    def step(self):
        self.mpu.step()


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


####################################################################
#   Tests

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

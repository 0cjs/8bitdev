from py65.devices.mpu6502 import MPU

LDAi    = 0xA9      # immediate
LDXz    = 0xA6      # zero page
NOP     = 0xEA

####################################################################
#   Utility routines

#   These functions should probably be replaced by a class
#   encapsulating the MPU with these functions on it.

def assertregs(mpu, pc=None, a=None, x=None, y=None, sp=None, p=None):
    ''' Assert any registers specified have given values.

        This needs to be tweaked to produce better output on failure.
        - Hex comparisions would be nice.
        - Can we end the stack trace one level above this?
    '''
    if pc is not None:  assert pc == mpu.pc
    if  a is not None:  assert  a == mpu.a
    if  x is not None:  assert  x == mpu.x
    if  y is not None:  assert  y == mpu.y
    if sp is not None:  assert sp == mpu.sp
    if  p is not None:  assert  p == mpu.p

def deposit(mem, addr, values):
    mem[addr:addr+len(values)] = values

def test_deposit():
    mem =  [0,0,0,0,0,0,0,0,0,0]
    deposit(mem, 2, [9, 2, 3, 8])
    assert [0,0,9,2,3,8,0,0,0,0] == mem

####################################################################
#   Tests

def test_mpu_step():
    ''' Test a little program we've hand assembled here to show
        that we're using the MPU API correctly.
    '''
    #   See py65/monitor.py for examples of how to set up and use the MPU.
    mpu = MPU()

    mpu.memory[7] = 0x7E
    deposit(mpu.memory, 0x400, [
        LDAi, 0xEE,
        LDXz, 0x07,
        NOP,
    ])
    assert   0x07 == mpu.ByteAt(0x403)
    assert 0xEEA9 == mpu.WordAt(0x400)  # LSB, MSB

    assertregs(mpu, 0, 0, 0, 0)
    mpu.pc = 0x400

    mpu.step(); assertregs(mpu, 0x402, a=0xEE)
    mpu.step(); assertregs(mpu, 0x404, x=0x7E)
    mpu.step(); assertregs(mpu, 0x405, 0xEE, 0x7E, 0x00)

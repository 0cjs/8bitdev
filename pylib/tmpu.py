''' Test framework for code on py65 MPU.
'''

from py65.devices.mpu6502 import MPU

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

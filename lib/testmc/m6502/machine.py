''' The test "machine" itself.
    Wraps py65 in an API suitable for use in unit tests.
'''

from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    sys import stderr

from    testmc.generic  import *
from    testmc.m6502.instructions  import Instructions as I

from    testmc.tool import asl, asxxxx

class Machine(GenericMachine):

    is_little_endian = True
    def get_memory_seq(self):
        return self.mpu.memory

    class Registers(GenericRegisters):
        machname = '6502'
        registers = (Reg('pc', 16), Reg('a'), Reg('x'), Reg('y'), Reg('sp'))
        #   No "B flag" here; it's not actually a flag in the PSR, it's
        #   merely set in the value pushed on to the stack on IRQ or `BRK`.
        srbits = (  Flag('N'), Flag('V'),   Bit(1),     Bit(1),
                    Flag('D'), Flag('I'), Flag('Z'), Flag('C'), )
        srname = 'p'

    ####################################################################

    def __init__(self):
        super().__init__()
        self.mpu = MPU()
        self.regsobj = self.mpu

    def _stackaddr(self, depth, size):
        addr = 0x100 + self.mpu.sp + 1 + depth
        if addr >= 0x201 - size:
            raise IndexError("stack underflow: addr={:04X} size={}" \
                .format(addr, size))
        return addr

    def spbyte(self, depth=0):
        return self.byte(self._stackaddr(depth, 1))

    def spword(self, depth=0):
        return self.word(self._stackaddr(depth, 2))

    ####################################################################
    #   Execution

    _JSR_opcodes        = set([I.JSR])
    _RTS_opcodes        = set([I.RTS])
    _ABORT_opcodes      = set([I.BRK])

    def _getpc(self):   return self.mpu.pc
    def _step(self):    self.mpu.step()



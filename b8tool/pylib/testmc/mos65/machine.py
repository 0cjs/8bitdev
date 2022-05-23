''' The test "machine" itself.
    Wraps py65 in an API suitable for use in unit tests.
'''

from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    testmc.generic.iomem  import IOMem
from    sys import stderr

from    testmc.generic  import *
from    testmc.mos65.instructions  import Instructions

from    testmc.tool import asl, asxxxx

#   We don't use ObservableMemory, but if we did, we'd need this.
#
#class ObservableMemorySeq(ObservableMemory):
#    ''' Our GenericMachine (`testmc.generic.memory.MemoryAccess`, actually)
#        needs a standard sequence function that ObservableMemory does not
#        provide.
#    '''
#    def __len__(self):
#        return len(self._subject)

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

        #   To implement functions simulating memory-mapped I/O we could
        #   use py65.memory.ObservableMemory, but it's almost 3× slower
        #   than the list of int that MPU() uses by default. Instead we use
        #   our own IOMem which is only about 15% slower than the list of
        #   int (perhaps because it's a bytearray and/or because it
        #   subclasses instead of accessing a separate object.)
        #
        #   py65 may rely on the memory returning an int instead of some
        #   sort of byte when individual elements are accessed, but if it
        #   does it doesn't matter because bytearray's [] returns an int
        #   when a single element is read. But this hasn't been tested with
        #   py65's unit tests (though it has with many of 8bitdev's tests).
        #
        self.mpu = MPU(memory=IOMem())      # defaults to 64K
        self.get_memory_seq().copyapi(self)

        self.regsobj = self.mpu

    def _stackaddr(self, depth, size):
        ''' Return the address of `size` bytes of data on the stack
            at `depth` bytes above the current head of the stack.
        '''
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

    _RTS_opcodes        = set([Instructions.RTS])
    _ABORT_opcodes      = set([Instructions.BRK])

    def _getpc(self):   return self.mpu.pc
    def _getsp(self):   return self.mpu.sp
    def _step(self):    self.mpu.step()

    def pushretaddr(self, addr):
        ''' Like JSR, this pushes `addr` - 1; RTS compensates for this.
            See MC6800 Family Programming Manual §8.1 p.108.
        '''
        self.mpu.sp -= 2
        self.depword(self._stackaddr(0, 2), addr - 1)

    def getretaddr(self):
        ''' Like RTS, we compensate for the return address pointing to the
            last byte of the JSR operand instead of the first byte of the
            next instruction. See MC6800 Family Programming Manual §8.2 p.108.
        '''
        return self.word(self._stackaddr(0, 2)) + 1

from    testmc.generic  import *
from    testmc.mc6800.opcodes  import OPCODES, Instructions

from    itertools  import repeat


class NotImplementedError(Exception):
    ''' Get rid of this once we're more complete. ''' # XXX
def raiseNI(msg):
    raise NotImplementedError(msg)

class Machine(GenericMachine):

    def __init__(self):
        ''' Initialize the machine.

            To make life easier for unit test clients, we initialize the
            stack pointer to $BFFF. (This assumes that the usual
            configuration may involve using any of the lower 32K as RAM and
            upper 16K as ROM and I/O.)

            All other registers, and all of memory, are initialized to
            zero. On a real machine certainly the memory, and probaby the
            registers and flags as well would all be left in a random state
            on power-up, but that doesn't seem worth emulating here.
        '''
        self.mem = bytearray(65536)
        self.pc = self.a = self.b = self.x = 0
        self.sp = 0xBFFF
        self.H = self.I = self.N = self.Z = self.V = self.C = False

    def is_little_endian(self):
        return False

    def get_memory_seq(self):
        return self.mem

    class Registers(GenericRegisters):
        machname  = '6800'
        registers = (
            Reg('pc', 16), Reg('a'), Reg('b'), Reg('x', 16), Reg('sp', 16) )
        srbits    = ( Bit(1), Bit(1),
            Flag('H'), Flag('I'), Flag('N'), Flag('Z'), Flag('V'), Flag('C') )

    ####################################################################
    #   Instruction Execution

    def step(self, count=1):
        ''' Execute `count` instructions (default 1).
        '''
        for _ in repeat(None, count):       # no tail call optimization; sigh
            opcode = self.mem[self.pc]
            _, f = OPCODES.get(opcode,
                ('NotImplemented', lambda m: raiseNI(opcode)))
            f(self)

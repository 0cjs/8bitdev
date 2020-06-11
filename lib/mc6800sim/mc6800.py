from    mc6800sim.memory  import Memory
from    mc6800sim.opcodes  import OPCODES, Instructions

from    itertools  import repeat


class NotImplementedError(Exception):
    ''' Get rid of this once we're more complete. ''' # XXX
def raiseNI(msg):
    raise NotImplementedError(msg)

class MC6800(Memory):

    def __init__(self):
        Memory.__init__(self)
        self._a = self._b = self._x = self._sp = self._pc = 0
        self._H = self._I = self._N = self._Z = self._V = self._C = False

    def get(propname):
        return lambda self: getattr(self, propname);

    def setmax(maxval, propname):
        def set(self, value):
            if value < 0 or value > maxval:
                raise ValueError(
                    "Register/flag '{}' value 0x{:X} exceeds range 0-0x{:X}"
                    .format(propname[1:], value, maxval))
            setattr(self, propname, value)
        return set

    a  = property(get('_a'),  setmax(0xFF,   '_a'),  None, 'Accumulator A')
    b  = property(get('_b'),  setmax(0xFF,   '_b'),  None, 'Accumulator B')
    x  = property(get('_x'),  setmax(0xFFFF, '_x'),  None, 'Index register X')
    sp = property(get('_sp'), setmax(0xFFFF, '_sp'), None, 'Stack pointer')
    pc = property(get('_pc'), setmax(0xFFFF, '_pc'), None, 'Program counter')

    H  = property(get('_H'),  setmax(1, '_H'),       None, 'Half-carry')
    I  = property(get('_I'),  setmax(1, '_I'),       None, 'Interrupt mask')
    N  = property(get('_N'),  setmax(1, '_N'),       None, 'Negative')
    Z  = property(get('_Z'),  setmax(1, '_Z'),       None, 'Zero')
    V  = property(get('_V'),  setmax(1, '_V'),       None, 'Overflow')
    C  = property(get('_C'),  setmax(1, '_C'),       None, 'Carry')

    ####################################################################
    #   Instruction Execution

    def step(self, count=1):
        ''' Execute `count` instructions (default 1).
        '''
        for _ in repeat(None, count):       # no tail call optimization; sigh
            opcode = self.mem[self.pc]
            _, f = OPCODES.get(opcode, lambda m: raiseNI(opcode))
            f(self)

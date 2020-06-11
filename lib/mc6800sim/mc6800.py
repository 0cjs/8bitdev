from    mc6800sim.opcodes  import OPCODES, Instructions

from    collections.abc  import Sequence
from    itertools  import repeat
from    numbers  import Integral


class NotImplementedError(Exception):
    ''' Get rid of this once we're more complete. ''' # XXX
def raiseNI(msg):
    raise NotImplementedError(msg)

class MC6800:

    def __init__(self):
        self._a = self._b = self._x = self._sp = self._pc = 0
        self._H = self._I = self._N = self._Z = self._V = self._C = False
        self.mem = bytearray(65536)

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
    #   More convenient methods to access memory.

    def byte(self, addr):
        ' Return the byte at `addr`. '
        return self.mem[addr]

    def bytes(self, addr, n):
        ' Return `n` `bytes` starting at `addr`. '
        bs = self.mem[addr:addr+n]
        if len(bs) < n:
            raise IndexError(
                'Last address 0x{:X} out of range'.format(addr+n-1))
        return bytes(bs)

    def word(self, addr):
        ' Return the word (decoding native endianness) at `addr`. '
        return self.mem[addr] * 0x100 + self.mem[addr+1]

    def words(self, addr, n):
        ''' Return a sequence of `n` words (decoding native endianness)
            starting `addr`. '
        '''
        return tuple( self.word(i) for i in range(addr, addr+n*2, 2) )

    def deposit(self, addr, *values):
        ''' Deposit bytes to memory at `addr`. Remaining parameters
            are values to deposit at contiguous addresses, each of which
            is a `numbers.Integral` in range 0x00-0xFF or a `Sequence`
            of such numbers (e.g., `list`, `tuple`, `bytes`).

            Returns a `bytes` of the deposited data.
        '''
        def assertvalue(x):
            if not isinstance(x, Integral):
                err('non-integral value {}', repr(x))
            if x < 0x00 or x > 0xFF:
                err('invalid byte value ${:02X}', x)

        vlist = []
        for value in values:
            if isinstance(value, Integral):
                assertvalue(value)
                vlist.append(value)
            elif isinstance(value, Sequence):
                list(map(assertvalue, value))
                vlist += list(value)
            else:
                err('invalid argument {}', repr(value))

        lastaddr = addr + len(vlist) -1
        if lastaddr > 0xFFFF:
            raise IndexError(
                'Last address 0x{:X} out of range'.format(lastaddr))
        self.mem[addr:lastaddr+1] = vlist
        return bytes(vlist)

    def _deperr(self, addr, message, *errvalues):
        s = 'deposit @${:04X}: ' + message
        raise ValueError(s.format(addr, *errvalues))

    def depword(self, addr, *values):
        ''' Deposit 16-bit words to memory at `addr` in native endian
            format. Remaining parameters are values to deposit at
            contiguous addresses, each of which is a
            `numbers.Integral` in range 0x0000-0xFFFF or a `Sequence`
            of such numbers (e.g., `list`, `tuple`, `bytes`).

            Returns a `bytes` of the deposited data.
        '''
        def assertvalue(x):
            if not isinstance(x, Integral):
                self._deperr(addr, 'non-integral value {}', repr(x))
            if x < 0x00 or x > 0xFFFF:
                self._deperr(addr, 'invalid word value ${:02X}', x)

        words = []
        for value in values:
            if isinstance(value, Integral):
                assertvalue(value)
                words.append(value)
            elif isinstance(value, Sequence):
                list(map(assertvalue, value))
                words += list(value)
            else:
                self._deperr(addr, 'invalid argument {}', repr(value))

        data = []
        for word in words:
            data.append((word & 0xFF00) >> 8)   # MSB first for 6800
            data.append(word & 0xFF)            # LSB
        self.deposit(addr, data)

        return self.bytes(addr, len(words)*2)

    ####################################################################
    #   Instruction Execution

    def step(self, count=1):
        ''' Execute `count` instructions (default 1).
        '''
        for _ in repeat(None, count):       # no tail call optimization; sigh
            opcode = self.mem[self.pc]
            _, f = OPCODES.get(opcode, lambda m: raiseNI(opcode))
            f(self)

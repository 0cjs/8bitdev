''' Test framework for code on py65 MPU.
'''

from    collections  import namedtuple
from    itertools  import repeat
from    struct  import unpack_from
from    py65.devices.mpu6502  import MPU

RegsTuple = namedtuple('RegsTuple', 'pc a x y sp N V D I Z C')
class Regs(RegsTuple):
    ''' The register set, including flags, of the 6502.

        Any values set to `None` will be ignored in comparisons
        between two register sets.

        Register names are lower-case; flags are upper-case. The
        registers in the constructor are given in order of
        approximately how likely you are to want to check them for
        comparisons. The flags given in the program status register
        order (MSB first); you will almost invariably want to set
        those by name, or by instead passing in a program status
        register value `psr`.

        repr() returns the processor name, register values in
        hexadecimal and a flags list with the flag letter upper-case
        if set, lower-case if clear. Any values that are `None`
        (ignored in comparisons) will be printed with hyphens. repr()
        is overridden instead of just str() because pytest prints
        repr() output, and that's where we want easily to see what's
        wrong.

        This inherits from `tuple` for immutability.
    '''

    def __new__(cls,
            pc=None, a=None, x=None, y=None, sp=None,
            N=None, V=None, D=None, I=None, Z=None, C=None,
            psr=None):

        def checkvalue(n):
            try:
                if n is None or n >= 0: return
            except TypeError:
                pass
            raise ValueError('bad value: {}'.format(n))
        [ checkvalue(n) for n in [pc, a, x, y, sp, N, V, D, I, Z, C, psr] ]

        if psr is not None:
            if psr < 0 or psr > 0xff:
                raise AttributeError('invalid psr: ' + hex(psr))
            if [f for f in [Z, C, N, V, I, D] if f is not None]:
                raise AttributeError("must not give both psr and flag values")
            C = 1 if psr & 0x01 else 0
            Z = 1 if psr & 0x02 else 0
            I = 1 if psr & 0x04 else 0
            D = 1 if psr & 0x08 else 0
            V = 1 if psr & 0x40 else 0
            N = 1 if psr & 0x80 else 0

        self = super(Regs, cls).__new__(cls, pc, a, x, y, sp, N, V, D, I, Z, C)
        return self

    def __repr__(self):
        pc = '----' if self.pc is None else '{:04X}'.format(self.pc)
        a  =   '--' if self.a  is None else '{:02X}'.format(self.a )
        x  =   '--' if self.x  is None else '{:02X}'.format(self.x )
        y  =   '--' if self.y  is None else '{:02X}'.format(self.y )
        sp =   '--' if self.sp is None else '{:02X}'.format(self.sp)
        def f(char, val):   # flag letter and value
            if val is None: return '-'
            if val is 0:    return char.lower()
            if val is 1:    return char.upper()
            return '?'
        return '6502 pc={} a={} x={} y={} sp={} {}{}--{}{}{}{}' \
            .format(pc, a, x, y, sp,
                f('N', self.N), f('V', self.V),
                f('D', self.D), f('I', self.I), f('Z', self.Z), f('C', self.C))

    def __ne__(a, b):
        #   Not sure if I'm seeing problems w/the default version
        #   delegating to __eq__, but this should definitely fix it.
        return not a.__eq__(b)

    def __eq__(a, b):
        if type(a) != type(b): return False

        #print('a:', a, '\nb:', b)
        def comp(a, b): # Should we compare a and b?
            #print('comp({}, {}) → {})'.format(a, b, a is not None and b is not None))
            return a is not None and b is not None

        if comp(a.pc, b.pc) and a.pc != b.pc: return False
        if comp(a.a , b.a ) and a.a  != b.a : return False
        if comp(a.x , b.x ) and a.x  != b.x : return False
        if comp(a.y , b.y ) and a.y  != b.y : return False
        if comp(a.sp, b.sp) and a.sp != b.sp: return False
        if comp(a.V , b.V ) and a.V  != b.V : return False
        if comp(a.D , b.D ) and a.D  != b.D : return False
        if comp(a.I , b.I ) and a.I  != b.I : return False
        if comp(a.Z , b.Z ) and a.Z  != b.Z : return False
        if comp(a.C , b.C ) and a.C  != b.C : return False

        return True

class TMPU():

    def __init__(self):
        self.mpu = MPU()

    @property
    def regs(self):
        m = self.mpu
        return Regs(m.pc, m.a, m.x, m.y, m.sp, psr=m.p)

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

    #   XXX This "examine" interface isn't so nice. Perhaps we can condense
    #   in down to a single examine() function that takes a length and type?

    def byteAt(self, addr):
        ' Examine a byte from memory. '
        return self.mpu.ByteAt(addr)

    def wordAt(self, addr):
        ' Examine a word from memory. '
        return self.mpu.WordAt(addr)

    def strAt(self, addr, len):
        ' Examine a string from memory. '
        #   This currently throws an exception if any of the bytes
        #   in the memory range are >0x7f. It's not clear how we
        #   should be decoding those. Possibly we want an option to
        #   clear the high bit on all chars before decoding.
        return bytes(self.mpu.memory[addr:addr+len]).decode('ASCII')

    def deposit(self, addr, values):
        self.mpu.memory[addr:addr+len(values)] = values

    def load_bin(self, buf):
        recs = ParseBin(buf)
        for addr, data in recs:
            self.deposit(addr, data)
        self.mpu.pc = recs.entrypoint

    def step(self, count=1):
        for _ in repeat(None, count):
            self.mpu.step()

class ParseBin(list):
    ''' Parse records in "Tandy CoCo Disk BASIC binary" (.bin) format
        as generated by the ASxxxx assembler's `aslink` program.

        This has poor error-handling; it is intended to be used only
        on files generated by assemblers and linkers that always
        produce valid output.
    '''
    def __init__(self, buf):
        #   There's not really any reason to keep the buf here, actually,
        #   so it would be more efficient to change this to use a binary
        #   input stream.
        self.buf = buf
        pos = 0
        while True:
            type, len, addr = unpack_from('>BHH', buf, pos)
            if type == 0:
                pos += 5
                data = unpack_from('B'*len, buf, pos)
                pos += len
                self.append((addr, list(data)))
            elif type == 0xFF:
                self.entrypoint = addr
                break
            else:
                raise ValueError('Bad .bin record type {} at {}: {}' \
                    .format(type, pos, buf[pos:pos+5]))

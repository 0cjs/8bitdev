import  pytest

class HeapBuilder:
    ''' Deposit objects into a downward-growing heap at the given address.

        XXX This does not yet handle car/cdr; it's on the caller always
        to deposit an appropriate cdr after the car.
    '''

    def __init__(self, m, addr=None):
        if addr is None: addr = 0x9000
        self.m = m
        self.topaddr = addr
        self.addr = addr

    @property
    def size(self):
        return self.topaddr - self.addr

    ####################################################################

    @staticmethod
    def checkrange(n, name):
        if (n < 0x0000 or n > 0xFFFF):
            raise ValueError(f'{name} out of range: {n}')

    NIL     = 0x00
    TRUE    = 0x04

    def cons(self, car, cdr=NIL):
        self.checkrange(car, 'car'); self.checkrange(cdr, 'cdr')
        self.addr -= 2; self.m.depword(self.addr, cdr);
        self.addr -= 2; self.m.depword(self.addr, car)

    ####################################################################
    #   Pointers

    def ptr(self, p):
        if (p >> 8) == 0:
            #   Not clear if we really need or even want this check.
            raise ValueError(f'iconst is not pointer: ${p:04X}')
        self.cons(p & 0xFFFC)

    ####################################################################
    #   Intrinsic constants

    def nil(self):
        self.const(self.NIL)

    def const(self, n):
        ' Intrinsic constants have MSB=$00 and LSB=%xxxxxx00. '
        self.cons(n & 0x00FC)

    ####################################################################
    #   Short symbols

    @staticmethod
    def checksym(sym, goodlen):
        if not isinstance(sym, (bytes, bytearray)):
            raise ValueError(f'Bad sym type {type(sym)}: {sym}')
        if len(sym) not in goodlen:
            raise ValueError(f'Bad sym{goodlen} length {len(sym)}: {sym}')

    def sym12(self, sym):
        self.checksym(sym, [1,2])
        if   len(sym) == 1:     self.sym1(sym)
        elif len(sym) == 2:     self.sym2(sym)

    def sym1(self, sym):
        self.checksym(sym, [1])
        self.cons((sym[0] << 8) | 0b00000010)

    def sym2(self, sym):
        ''' NOTE: with a sym2, the MSB contains the second char, not the first.
        '''
        if sym[0] > 0x7F or sym[1] > 0x7F:
            raise ValueError(f'sym2 chars must be ≤ $7F: {sym}')
        self.checksym(sym, [2])
        msb = sym[1]
        if sym[0] & 0x40: msb |= 0x80    # copy sym0 bit 6 to MSB bit 7
        lsb = (sym[0] << 2) & 0xFC | 0b10
        self.cons((msb << 8) | lsb)

    ####################################################################
    #   Smallints

    def smallint(self, i):
        if i > 8191 or i < -8192:
            raise ValueError(f'smallint out of range: {i}')
        if i < 0: i += 0x4000       # negative numbers → 2s complement
        self.cons((i << 2) | 0b01)

####################################################################

@pytest.fixture
def hb(m, addr=None):
    return HeapBuilder(m, addr)

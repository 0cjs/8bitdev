' Object Reference generator for Clic. '

class ORef:
    ''' Object reference generator.

        This generates 16-bit words as `int`s intended to be deposited with
        `Machine.depword()`, which will handle converting the word to the
        correct endianness as it deposits.
    '''

    NIL     = 0x0000;       ' Intrinsic constant NIL.'
    TRUE    = 0x0004;       ' Intrinsic constant TRUE.'

    ####################################################################
    #   Intrinsic constants

    @classmethod
    def const(cls, n):
        ''' Return intrinsic constant `n`.

            This takes the value _including_ the %00 tag in the LSbits.
            If the tag is not %00 or the constant is not in range, a
            `ValueError` is raised.
        '''
        if (n < 0) or (n > 0xFF):  raise ValueError(
            f'Instrinsic const out of range: ${n:02X}')
        tag = n & 0x03
        if tag != 0:  raise ValueError(
            f'bad tag bits %{tag:02b} for intrinsic const: ${n:02X}')
        return n

    ####################################################################
    #   Pointers

    @classmethod
    def ptr(cls, addr):
        ''' Return pointer to `addr`. This may not be used to create
            "intrinsic constant" pointers.

            If the tag (LSbits) is not %00 or the pointer is not in the
            range $0100 through $FFFC, a `ValueError` is raised.

            XXX This assumes a 16-bit address space. It's also not clear
            if not allowing creation of intrinsic constant pointers with
            this is good or inconvenient.
        '''
        if (addr < 0x0100) or (addr > 0xFFFF):  raise ValueError(
            f'pointer out of range: ${addr:04X}')
        tag = addr & 0x03
        if tag != 0:  raise ValueError(
            f'bad tag bits %{tag:02b} for pointer: ${addr:04X}')
        return addr

    ####################################################################
    #   Short symbols

    @staticmethod
    def _checksym(sym, goodlen):
        if not isinstance(sym, (bytes, bytearray)):
            raise ValueError( f'Bad sym type {type(sym)}: {sym}')
        if len(sym) not in goodlen:
            sgoodlen = ''.join(map(str, goodlen))
            raise ValueError(f'Bad sym{sgoodlen} length {len(sym)}: {sym}')

    @classmethod
    def sym1(self, sym):
        self._checksym(sym, [1])
        return ((sym[0] << 8) | 0b00000010)

    @classmethod
    def sym2(self, sym):
        ''' NOTE: with a sym2, the MSB contains the second char, not the first.
        '''
        self._checksym(sym, [2])
        if sym[0] == 0x00:
            raise ValueError(f'sym2 1st char cannot be $00: {sym}')
        if sym[0] > 0x7F or sym[1] > 0x7F:
            raise ValueError(f'sym2 chars must be ≤ $7F: {sym}')
        msb = sym[1]
        if sym[0] & 0x40: msb |= 0x80    # copy sym0 bit 6 to MSB bit 7
        lsb = (sym[0] << 2) & 0xFC | 0b10
        return ((msb << 8) | lsb)

    @classmethod
    def sym12(self, sym):
        self._checksym(sym, [1,2])
        if   len(sym) == 1:     return self.sym1(sym)
        elif len(sym) == 2:     return self.sym2(sym)

    ####################################################################
    #   Smallints

    @classmethod
    def smallint(self, i):
        if i > 8191 or i < -8192:
            raise ValueError(f'smallint out of range: {i}')
        if i < 0: i += 0x4000       # negative numbers → 2s complement
        return ((i << 2) | 0b01)



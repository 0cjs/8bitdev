from    collections.abc  import Sequence
from    numbers  import Integral

class Memory:
    ''' A random-access memory and its access methods.

        This handles reading and depositing of bytes and words (in
        big-endian format) with error checking.
    '''

    def __init__(self, memsize=65536):
        self.mem = bytearray(memsize)

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

        lastaddr = addr + len(vlist) - 1
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


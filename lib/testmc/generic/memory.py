from    abc  import ABC, abstractmethod, abstractproperty
from    collections.abc  import Sequence
from    numbers  import Integral


class MemoryAccess(ABC):
    ''' Access methods for a random-access memory stored as a mutable
        sequence of values.

        This handles reading and depositing of bytes and words (in
        big-endian format) with error checking of both addresses and values
        on deposits, but only addresses on examines (i.e., if the memory
        contains non-byte values deposited through another method, this
        will return them).

        Subclasses must define attributes `is_little_endian` and
        `get_memory_seq()`; see their docstrings below for details.
    '''

    @abstractmethod
    def get_memory_seq(self):
        ''' Return the mutable sequence storing the memory that we access.

            The store must (as with all sequences) support two-parameter
            slice indexing, but need not support three-parameter (i.e., a
            "step" parameter). It must support all values that can be held
            in a byte, integers 0..255

            If you are creating the store yourself, a `bytearray` is a good
            choice:

                def __init__(self):
                    self.memory = bytearray(65536)
                def get_memory_seq(self):
                    return self.memory

            You may also use stores created by other systems, such as a
            `py65.memory.ObservableMemory` instance.
        '''

    @abstractproperty
    def is_little_endian(self):
        ''' Set to `True` if this is used with a little-endian architecture,
            otherwise `False` if it's used with a big-endian architecture.

            This is used by the word-access methods.
        '''

    def byte(self, addr):
        ' Return the byte value at `addr` as an `int`. '
        mem = self.get_memory_seq()
        if addr >= len(mem):
            _memerr(addr, "bad location", ex=IndexError)
        return int(self.get_memory_seq()[addr])

    def bytes(self, addr, n):
        ' Return `n` byte values starting at `addr` as a `bytes`. '
        bs = self.get_memory_seq()[addr:addr+n]
        if len(bs) < n:
            _memerr(addr+n-1, "bad location", ex=IndexError)
        return bytes(bs)

    def word(self, addr):
        ' Return the word (decoding native endianness) at `addr`. '
        mem = self.get_memory_seq()
        b0 = mem[addr]; b1 = mem[addr+1]
        if self.is_little_endian:
            return b0 + 0x100 * b1
        else:
            return b0 * 0x100 + b1

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
                _memerr(addr, 'non-integral value {}', repr(x))
            if x < 0x00 or x > 0xFF:
                _memerr(addr, 'invalid byte value ${:02X}', x)

        if addr < 0:
            _memerr(addr, "bad location", ex=IndexError)

        vlist = []
        for value in values:
            if isinstance(value, Integral):
                assertvalue(value)
                vlist.append(value)
            elif isinstance(value, Sequence):
                list(map(assertvalue, value))
                vlist += list(value)
            else:
                _memerr(addr, 'invalid argument {}', repr(value))

        mem = self.get_memory_seq()

        lastaddr = addr + len(vlist) - 1
        if lastaddr >= len(mem):
            _memerr(lastaddr, "bad location", ex=IndexError)
        mem[addr:lastaddr+1] = vlist
        return bytes(vlist)

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
                _memerr(addr, 'non-integral value {}', repr(x))
            if x < 0x00 or x > 0xFFFF:
                _memerr(addr, 'invalid word value ${:02X}', x)

        words = []
        for value in values:
            if isinstance(value, Integral):
                assertvalue(value)
                words.append(value)
            elif isinstance(value, Sequence):
                list(map(assertvalue, value))
                words += list(value)
            else:
                _memerr(addr, 'invalid argument {}', repr(value))

        data = []
        for word in words:
            if self.is_little_endian:
                data.append(word & 0xFF)            # LSB first
                data.append((word & 0xFF00) >> 8)   # MSB
            else:
                data.append((word & 0xFF00) >> 8)   # MSB first
                data.append(word & 0xFF)            # LSB
        self.deposit(addr, data)

        return self.bytes(addr, len(words)*2)

    def hexdump(self, addr, length):
        ''' Return a human-readable hexadecimal dump of of `length` bytes
            of this memory starting at `addr`.

            This is useful for printing debugging information in unit tests.
        '''
        s = '{:04X}:'.format(addr)
        for b in self.bytes(addr, length):
            s += ' {:02X}'.format(b)
        return s


####################################################################
#   "Static" methods; external to class for easier calling

def _memerr(addr, message, *errvalues, ex=ValueError):
    #   The argument list couldwbe shortened a bit more, and this possibly
    #   generalized slightly, by using dynamic scoping--reaching up the
    #   stack to find the name of the caller and the value of `addr`.
    s = 'memory @${:04X}: ' + message
    raise ex(s.format(addr, *errvalues))


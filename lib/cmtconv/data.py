''' cmtconv.data: byte data stored in tape blocks and files

    This is above the level of both the bitstream representation of the
    bytes (mark/space sequences) and the audio data representing the
    bitstream.

    XXX This is currently all specific to the JR-200 format. When we add a
    second format we'll probably want to make these classes define the API
    and hold common operations (if any), and use subclasses for particular
    implementations.
'''

####################################################################
#   Tape Blocks

class Block(object):
    ''' JR-200 Tape Block

        0-1: magic number $02 $2A (2,42)
          2: block number: 0-254; 255 indicates end block
          3: length of the data portion of the block; 0=256 bytes
             (255 for tail block)
        4-5: load address ($0000 if not used)
        6…n: data (datalen bytes)
        n+1: checksum: sum of bytes 0…n modulo 256
    '''

    @classmethod
    def make(cls, blockno, addr, data=b'', checksum=None):
        ''' Create a `Block`. If `checksum` is not `None`, the checksum
            will be verified and a `ChecksumError` will be thrown if
            the checksum is incorrect.
        '''
        if not isinstance(data, bytes):
            raise ValueError('`data` must be a `bytes`')
        block = cls(blockno, addr, data)
        block._check_checksum(checksum)
        return block

    @classmethod
    def make_tail(cls, addr):
        ''' Create a tail block.

            Tail blocks have an address (usually the previous block's
            addr+datalen+1) but no data, and the blockno is always 0xFF.
        '''
        return TailBlock(addr)

    @classmethod
    def from_header(cls, headerbytes):
        ''' Create a `Block` from header bytes, returning a pair of the
            block and the datalen specified by the header. The caller will
            normally read that many more bytes plus the checksum byte from
            the source and call `setdata()` with those.
        '''
        if len(headerbytes) != 6:
            raise ValueError('Bad length: expected=6 actual={}'
                .format(len(headerbytes)))
        if headerbytes[0:2] != cls.MAGIC:
            raise ValueError(
                'Bad magic: expected={:02X}{:02X} actual={:02X}{:02X}'.format(
                    cls.MAGIC[0], cls.MAGIC[1], headerbytes[0], headerbytes[1]))

        blockno = headerbytes[2]
        datalen = headerbytes[3]
        addr = headerbytes[4] * 0x100 + headerbytes[5]

        if blockno == 0xFF and datalen == 0xFF:
            return (cls.make_tail(addr), 0)
        else:
            if datalen == 0:  datalen = 0x100
            return (cls.make(blockno, addr), datalen)

    MAGIC = b'\x02\x2A'

    class ChecksumError(ValueError): pass

    def __init__(self, blockno, addr, data):
        if blockno is not None:         # XXX hack for subclass
            self.blockno    = blockno
        self.addr       = addr
        self._data      = data

    def is_tail(self):
        return False

    @property
    def datalen(self):
        return len(self.data)

    @property
    def data(self):
        return self._data

    def setdata(self, data, checksum=None):
        self._data = data
        self._check_checksum(checksum)

    def _check_checksum(self, checksum):
        if checksum is not None and checksum != self.checksum():
            raise self.ChecksumError('expected={:02X} actual={:02X}'
                .format(self.checksum(), checksum))

    def checksum(self):
        return sum(self._bytes()) & 0xFF

    def _bytes(self):
        ' Return the data as bytes for tape, but without a checksum appended. '
        b = bytearray(self.MAGIC)
        b.append(self.blockno)
        b.append(0 if self.datalen == 256 else self.datalen)
        b.append(self.addr >> 8)
        b.append(self.addr & 0xFF)
        b.extend(self.data)
        return bytes(b)

    def to_bytes(self):
        return self._bytes() + bytes([self.checksum()])

    def __repr__(self):
        return '{}.{}(blockno={}, addr={}, data={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            hex(self.blockno), hex(self.addr),
            self.data)

class TailBlock(Block):
    ''' Tail blocks are special:
        - The block number is always $FF.
        - The data are always an empty `bytes`.
        - The datalen byte on tape is $FF, but there are no data bytes.
        - The checksum is $00 instead of the calculated value.
    '''

    def __init__(self, addr):
        #   `data` as b'' instead of None allows concatenating all the
        #   data from a series of blocks without having to check if
        #   there's a TailBlock at the end.
        super().__init__(None, addr, b'')

    def is_tail(self):  return True

    @property
    def blockno(self):  return 0xFF

    def setdata(self, data, checksum=None):
        if data != b'':  raise ValueError('Tail block data must be empty.')
        self._check_checksum(checksum)

    def checksum(self): return 0

    def to_bytes(self):
        #   XXX this can probably re-use more from the superclass
        b = bytearray(self.MAGIC)
        b.extend(b'\xFF\xFF')       # blockno and datalen identify tail block
        b.append(self.addr >> 8)
        b.append(self.addr & 0xFF)
        b.append(self.checksum())
        return bytes(b)

    def __repr__(self):
        return '{}.{}(addr={})'.format(
            self.__class__.__module__, self.__class__.__name__, hex(self.addr))

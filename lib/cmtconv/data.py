''' cmtconv.data: byte data stored in tape blocks and files

    This is above the level of both the bitstream representation of the
    bytes (mark/space sequences) and the audio data representing the
    bitstream.

    XXX This is currently all specific to the JR-200 format. When we add a
    second format we'll probably want to make these classes define the API
    and hold common operations (if any), and use subclasses for particular
    implementations.

    Sources:
    - omff_ Old Machinery Blog, "Panasonic JR200U tape file format"
    - omwg_ Old Machinery Blog, "Panasonic JR200u tape wave generation"
    - mr_ Markku Reunanen, "Discovering the Panasonic JR-200U,"
      section "File Transfer and Creation"

    .. _omff: https://oldmachinery.blogspot.com/2012/01/panasonic-jr200u-tape-file-format.html
    .. _omwg: https://oldmachinery.blogspot.com/2012/02/panasonic-jr200u-tape-wave-generation.html
    .. _mr: http://www.kameli.net/marq/?page_id=1270

'''

from enum import IntEnum

####################################################################
#   Tape Blocks

class Block(object):
    ' A JR-200 Tape Block '
    # Block format on tape:
    #   0-1: magic number $02 $2A (2,42)
    #     2: block number: 0-254; 255 indicates end block
    #     3: length of the data portion of the block; 0=256 bytes
    #        (255 for tail block)
    #   4-5: load address ($0000 if not used)
    #   6…n: data (datalen bytes)
    #   n+1: checksum: sum of bytes 0…n modulo 256

    @classmethod
    def make(cls, blockno, addr, data=b'', checksum=None):
        ''' Create a `Block`. If `checksum` is not `None`, the checksum
            will be verified and a `ChecksumError` will be thrown if
            the checksum is incorrect.
        '''
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

    headerlen = 6

    @classmethod
    def from_header(cls, headerbytes):
        ''' Create a `Block` from exactly `headerlen` header bytes, returning
            a pair ``(block, datalen)`` of the new block and the data
            length given in the header. The caller will normally read
            ``datalen`` more bytes plus the checksum byte from the source
            and call `setdata()` with those.
        '''
        if len(headerbytes) != cls.headerlen:
            raise ValueError('Bad length: expected={} actual={}'
                .format(cls.headerlen, len(headerbytes)))
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

    ####################################################################

    MAGIC = b'\x02\x2A'

    class ChecksumError(ValueError): pass

    def __init__(self, blockno, addr, data):
        if blockno is not None:         # XXX hack for subclass
            self.blockno    = blockno
        self.addr       = addr
        self._data      = bytes(data)

    def is_tail(self):
        return False

    @property
    def datalen(self):
        return len(self.data)

    @property
    def data(self):
        return self._data

    def setdata(self, data, checksum=None):
        self._data = bytes(data)
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

class FileHeader(Block):
    ''' The header block for a JR-200 tape file. This is a standard block
        with blockno 0, address $FFFF and datalen 26, and the file metadata
        in the data section. It is always a 600 baud block.

        This is an immutable object because it has so few attributes
        that it's easy to create a new one if something need be changed.
    '''
    # Data section contents:
    #    0-15: file name
    #      16: BASIC(0)/Binary(1)
    #      17: Baud rate of following blocks: 0=2400, 1=600
    #   18-25: pad: $FF

    @classmethod
    def make(cls, filename, filetype, baudrate):
        if len(filename) > 16:
            raise ValueError(
                'len(filename) must be < 16 (len={})'.format(len(filename)))
        if filetype not in cls.FileType:
            raise ValueError('filetype must be BASIC or BINARY, not {}'
                .format(repr(filetype)))
        if baudrate not in cls.BaudRate:
            raise ValueError('baudrate must be B_2400 or B_600, not {}'
                .format(repr(baudrate)))

        fnfill = bytearray(16)
        fnfill[0:len(filename)] = filename
        return cls.from_bytes(
            bytes([
                0x02, 0x2A,             # magic number
                   0, 0x1A,             # block 0, datalen
                0xFF, 0xFF,             # address: $FFFF
            ])
            + fnfill                    # filename
            + bytes([filetype, baudrate])
            + bytes([0xFF]*8)           # padding
            , checksum=False)

    #   The length of the entire block, including checksum.
    blocklen = Block.headerlen + 26 + 1

    @classmethod
    def from_bytes(cls, blockbytes, checksum=True):
        ''' Create a `FileHeader` from exactly `blocklen` bytes, which must
            be the entire contents of a block read from tape. A
            `ValueError` or `ChecksumError` will be raised if the block is
            not a valid FileHeader block.

            If `checksum` is `False`, `blockbytes` must not have a trailing
            checksum byte (i.e., length `blocklen` - 1).
        '''
        if not checksum:
            blockbytes += b'\xEE'   # dummy checksum that will be ignored
        if len(blockbytes) != cls.blocklen:
            raise ValueError('bad length: expected={} actual={}'
                .format(cls.blocklen, len(blockbytes)))
        block = FileHeader(blockbytes[Block.headerlen:-1])

        if block.blockno != 0:
            raise ValueError('bad blockno: expected=${:02X} actual=${:02X}'
                .format(0, block.blockno))
        if block.addr != 0xFFFF:
            raise ValueError('bad addr: expected=${:04X} actual=${:04X}'
                .format(0xFFFF, block.addr))
        if checksum and block.checksum() != blockbytes[-1]:
            raise cls.ChecksumError('expected=${:02X} actual=${:02X}'
                .format(block.checksum(), blockbytes[-1]))

        return block

    def __init__(self, data):
        ' `data` must be already validated. '
        super().__init__(0, 0xFFFF, data)

    @property
    def filename(self):
        ''' The filename is a 0-15 character `bytes` using JR-200 charset.

            This may include Japanese characters, and so should probably be
            a (Unicode) Python `str`, but we don't do character set
            conversion right now.
        '''
        return self.data[0:16].rstrip(b'\x00')

    class FileType(IntEnum): BASIC = 0; BINARY = 1
    BASIC  = FileType.BASIC
    BINARY = FileType.BINARY

    @property
    def filetype(self):
        ' Returns either `BASIC` or `BINARY`. '
        return self.FileType(self.data[16])

    class BaudRate(IntEnum): B_2400 = 0; B_600 = 1
    B_2400 = BaudRate.B_2400
    B_600  = BaudRate.B_600

    @property
    def baudrate(self):
        ''' Returns the baud rate used by the remaining blocks in the file,
            `B_2400` or `B_600`. The FileHeader block (this block) is
            always stored at 600 baud.
        '''
        return self.BaudRate(self.data[17])

    def __repr__(self):
        return '{}.{}(filename={}, filetype={} baudrate={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.filename, self.filetype.name, self.baudrate.name)

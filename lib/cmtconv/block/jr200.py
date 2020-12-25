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
    #     2: block number: 0-254; 255 indicates EOF block
    #     3: length of the data portion of the block; 0=256 bytes
    #        (255 for EOF block)
    #   4-5: load address ($0000 if not used)
    #   6…n: data (datalen bytes)
    #   n+1: checksum: sum of bytes 0…n modulo 256

    #   The 'short' platform name is just the module name: `jr200`.
    platform = 'National/Panasonic JR-200'

    @classmethod
    def make_block(cls, blockno, addr, data=b'', checksum=None):
        ''' Create a data `Block`. If `checksum` is not `None`, the
            checksum will be verified and a `ChecksumError` will be thrown
            if the checksum is incorrect.
        '''
        block = cls(blockno, addr, data)
        block._check_checksum(checksum)
        return block

    @classmethod
    def make_eof_block(cls, addr):
        ''' Create an end-of-file block.

            EOF blocks have an address (usually the previous block's
            addr+datalen+1) but no data, and the blockno is always 0xFF.
        '''
        return EOFBlock(addr)

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
        cls._check_magic(headerbytes)

        blockno = headerbytes[2]
        datalen = headerbytes[3]
        addr = headerbytes[4] * 0x100 + headerbytes[5]

        if blockno == 0xFF and datalen == 0xFF:
            return (cls.make_eof_block(addr), 0)
        else:
            if datalen == 0:  datalen = 0x100
            return (cls.make_block(blockno, addr), datalen)

    @classmethod
    def _check_magic(cls, headerbytes):
        ''' Raise an exception i the first two values in `headerbytes` are
            not the correct magic value.
        '''
        if bytes(headerbytes[0:2]) != cls.MAGIC:
            raise ValueError(
                'Bad magic: expected={:02X}{:02X} actual={:02X}{:02X}'.format(
                    cls.MAGIC[0], cls.MAGIC[1], headerbytes[0], headerbytes[1]))

    ####################################################################

    MAGIC = b'\x02\x2A'

    class ChecksumError(ValueError): pass

    def __init__(self, blockno, addr, _data):
        ' For internal use only. '
        if blockno is not None:         # XXX hack for subclass
            self.blockno    = blockno
        self.addr       = addr
        self._data      = bytes(_data)

    @property
    def is_eof(self):
        ''' Return True if this is an "EOF" block, indicating the last
            block of a file on tape.
        '''
        return False

    @property
    def filedata(self):
        ''' Returns the file data contained in this block, if any. This is
            not necessarily the contents of the data section of the block on
            tape, which may contain metadata as well as or instead of file
            data.
        '''
        return self._data

    def setdata(self, data, checksum=None):
        ''' Set the contents of the block's data. The exact meaning of the
            data depends on the block type, and it is not necessarily what
            `filedata()` will return. (E.g., if it's metadata about the
            file stored on tape, `filedata()` may return a zero-length
            `bytes` regardless of what this is set to.

            If `checksum` is not `None`, it will be compared to the
            calculated checksum for the updated block and a `ChecksumError`
            will be thrown if it is different.

            In most cases no validation is done on the data; setting bad
            data may produce invalid blocks.
        '''
        self._data = bytes(data)
        self._check_checksum(checksum)

    def _check_checksum(self, checksum):
        if checksum is not None and checksum != self.checksum:
            raise self.ChecksumError('expected={:02X} actual={:02X}'
                .format(self.checksum, checksum))

    @property
    def checksum(self):
        return sum(self._tapebytes()) & 0xFF

    def _tapebytes(self):
        ' Return the data as bytes for tape, but without a checksum appended. '
        b = bytearray(self.MAGIC)
        b.append(self.blockno)
        b.append(0 if len(self._data) == 0x100 else len(self._data))
        b.append(self.addr >> 8)
        b.append(self.addr & 0xFF)
        b.extend(self._data)
        return bytes(b)

    def to_bytes(self):
        return self._tapebytes() + bytes([self.checksum])

    def __repr__(self):
        return '{}.{}(blockno={}, addr={}, _data={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            hex(self.blockno), hex(self.addr),
            self._data)

class EOFBlock(Block):
    ''' EOF blocks are special:
        - The block number is always $FF.
        - The data are always an empty `bytes`.
        - The datalen byte on tape is $FF, but there are no data bytes.
        - The checksum is $00 instead of the calculated value.
    '''

    def __init__(self, addr):
        #   `data` as b'' instead of None allows concatenating all the
        #   data from a series of blocks without having to check if
        #   there's a EOFBlock at the end.
        super().__init__(None, addr, b'')

    @property
    def is_eof(self):   return True

    @property
    def blockno(self):  return 0xFF

    def setdata(self, data, checksum=None):
        if data != b'':  raise ValueError('EOF block data must be empty.')
        self._check_checksum(checksum)

    @property
    def checksum(self): return 0

    def to_bytes(self):
        #   XXX this can probably re-use more from the superclass
        b = bytearray(self.MAGIC)
        b.extend(b'\xFF\xFF')       # blockno and datalen identify EOF block
        b.append(self.addr >> 8)
        b.append(self.addr & 0xFF)
        b.append(self.checksum)
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
    def make_block(cls, filename=None, filetype=None, baudrate=None):
        ''' Create a FileHeader block.

            If `filetype` is `None`, `BINARY` will be used. If `baudrate`
            is `None`, `B_2400` will be used.
        '''
        if filename is None:    filename = b''
        if filetype is None:    filetype = cls.BINARY
        if baudrate is None:    baudrate = cls.B_2400

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
        cls._check_magic(blockbytes)
        block = FileHeader(blockbytes[Block.headerlen:-1])

        if block.blockno != 0:
            raise ValueError('bad blockno: expected=${:02X} actual=${:02X}'
                .format(0, block.blockno))
        if block.addr != 0xFFFF:
            raise ValueError('bad addr: expected=${:04X} actual=${:04X}'
                .format(0xFFFF, block.addr))
        if checksum and block.checksum != blockbytes[-1]:
            raise cls.ChecksumError('expected=${:02X} actual=${:02X}'
                .format(block.checksum, blockbytes[-1]))

        return block

    def __init__(self, data):
        ' `data` must be already validated. '
        super().__init__(0, 0xFFFF, data)

    @property
    def filedata(self):
        ''' Always returns an empty `bytes` because this block contains no
            file data. Read the `filename`, `filetype` and `baudrate`
            attributes for the file metadata.
        '''
        return b''

    @property
    def filename(self):
        ''' The filename is a 0-15 character `bytes` using JR-200 charset.

            This may include Japanese characters, and so should probably be
            a (Unicode) Python `str`, but we don't do character set
            conversion right now.
        '''
        return self._data[0:16].rstrip(b'\x00')

    class FileType(IntEnum): BASIC = 0; BINARY = 1
    BASIC  = FileType.BASIC
    BINARY = FileType.BINARY

    @property
    def filetype(self):
        ' Returns either `BASIC` or `BINARY`. '
        return self.FileType(self._data[16])

    class BaudRate(IntEnum): B_2400 = 0; B_600 = 1
    B_2400 = BaudRate.B_2400
    B_600  = BaudRate.B_600

    @property
    def baudrate(self):
        ''' Returns the baud rate used by the remaining blocks in the file,
            `B_2400` or `B_600`. The FileHeader block (this block) is
            always stored at 600 baud.
        '''
        return self.BaudRate(self._data[17])

    def __repr__(self):
        return '{}.{}(filename={}, filetype={} baudrate={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.filename, self.filetype.name, self.baudrate.name)

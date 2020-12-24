''' cmtconv.data: byte data stored in tape blocks and files

    This is above the level of both the bitstream representation of the
    bytes (mark/space sequences) and the audio data representing the
    bitstream.

    XXX This is currently all specific to the JR-200 format. When we add a
    second format we'll probably want to make these classes define the API
    and hold common operations (if any), and use subclasses for particular
    implementations.
'''

from    enum  import Enum
from    logging  import debug

####################################################################
#   Tape Blocks

class BlockHeader(object):
    ''' JR-200 Tape Block

        0-1: magic number $02 $2A (2,42)
          2: block number: 0-254; 255 indicates end block
          3: length of the data portion of the block; 0=256 bytes
        4-5: load address ($0000 if not used)
        6…n: data (datalen bytes)
        n+1: checksum: sum of bytes 0…n modulo 256

    '''

    def __init__(self, blockno, datalen, addr):
        '''Caller is responsible for ensuring bytes match interpretation'''
        self.blockno = blockno
        self._datalen = datalen  # XXX should be removed in favour of len(data)
        self.addr    = addr

    MAGIC = b'\x02\x2A'

    @classmethod
    def from_bytes(self, b):
        ' Construct the block header from raw bytes '
        if b[0:2] != self.MAGIC:
            raise ValueError(
                'Bad magic number: ${:02X} ${:02X}'.format(b[0], b[1]))

        datalen = b[3]
        if datalen == 0:
            datalen = 256
        addr = b[4] * 256 + b[5]
        return BlockHeader(b[2], datalen, addr)

    @classmethod
    def make(self, blockno, datalen, addr):
        '''Build a block header from details'''
        if blockno < 0 or blockno > 255:
            raise ValueError(
                'Block number must be in range 0-255: {:02X}'.format(blockno))
        if datalen < 0 or datalen > 256:
            raise ValueError('datalen must be in range 0-256: {}' % datalen)
        if addr < 0 or addr > 0xffff:
            raise ValueError('Address must be in range 0x0000-0xffff: {}' %
                addr)
        return BlockHeader(blockno, datalen, addr)

    @property
    def datalen(self):
        return self._datalen    # XXX should be len(data)

    def __repr__(self):
        return '{}.{}(blockno={}, datalen={}, addr={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            hex(self.blockno), hex(self.datalen), hex(self.addr))

    def is_tail(self):
        #FIXME: what happens when we try to save the whole 64k?
        #Is the block number alone enough?
        return self.blockno == 255 and self.datalen == 255

    def to_bytes(self):
        b = bytearray(self.MAGIC)
        b.append(self.blockno)
        b.append(0 if self.datalen == 256 else self.datalen)
        b.append(self.addr >> 8)
        b.append(self.addr & 0xFF)
        return b

class Block(object):
    '''Represents a block of data'''

    @classmethod
    def make_tail(cls, addr):
        ''' Create a tail block.

            Tail blocks have an address (usually the previous block's
            addr+datalen+1) but no data, and the blockno is always 0xFF.
        '''
        return cls(BlockHeader.make(255, 255, addr), None)

    def __init__(self, header, data):
        self.header     = header
        self.data       = data

    def __repr__(self):
        return '{}.{}(header={}, data={})'.format(
            self.__class__.__module__, self.__class__.__name__,
            self.header, self.data)

    def checksum(self):
        if self.header.is_tail():
            return 0
        else:
            return sum(list(self.header.to_bytes() + self.data)) & 0xFF

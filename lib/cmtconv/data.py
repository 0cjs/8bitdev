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
          3: length in bytes; 0=256 bytes
        4-5: load address ($0000 if not used)
        6…n: data
        n+1: checksum: sum of bytes 0…n modulo 256

    '''

    def __init__(self, header, block_number, length, addr, raw_bytes):
        '''Caller is responsible for ensuring bytes match interpretation'''
        self.header         = header
        self.block_number   = block_number
        self.length         = length
        self.addr           = addr
        self.raw_bytes      = raw_bytes

    MAGIC = b'\x02\x2A'

    @classmethod
    def from_bytes(self, raw_bytes):
        ' Construct the block header from raw bytes '
        b = raw_bytes
        if b[0:2] != self.MAGIC:
            raise ValueError(
                'Bad magic number: ${:02X} ${:02X}'.format(b[0], b[1]))
        header = (b[0], b[1])

        length = b[3]
        if length == 0:
            length = 256
        addr = b[4] * 256 + b[5]

        return BlockHeader(header, b[2], length, addr, raw_bytes)

    @staticmethod
    def make(block_number, length, addr):
        '''Build a block header from details'''
        if block_number < 0 or block_number > 255:
            raise ValueError('Block number must be in range 0-255: {}' %
                block_number)
        if length < 0 or length > 256:
            raise ValueError('Length must be in range 0-256: {}' % length)
        if addr < 0 or addr > 0xffff:
            raise ValueError('Address must be in range 0x0000-0xffff: {}' %
                addr)
        header = (2, 42)
        b = bytearray()
        b.extend(header)
        b.append(block_number)
        b.append(0 if length == 256 else length)
        b.append(addr // 256)
        b.append(addr % 256)
        return BlockHeader(header, block_number, length, addr, b)

    @staticmethod
    def make_tail():
        '''Make a tail block'''
        return BlockHeader.make(255, 255, 0)

    def __str__(self):
        s = ''
        s += 'JR-200 Data block header\n'
        s += 'Header: {}\n'.format(tuple(hex(x) for x in self.header))
        s += 'Block: {}\n'.format(self.block_number)
        s += 'Length: {}\n'.format(self.length)
        s += 'Address: {}\n'.format(self.addr)
        return s

    def is_tail(self):
        #FIXME: what happens when we try to save the whole 64k?
        #Is the block number alone enough?
        return self.block_number == 255 and self.length == 255

    def calc_checksum(self):
        if self.is_tail():
            return 0
        else:
            return sum(self.raw_bytes) % 256

class Block(object):
    '''Represents a block of data'''

    def __init__(self, header, data, checksum):
        self.header     = header
        self.data       = data
        self.checksum   = checksum

    def __str__(self):
        s = ''
        s += str(self.header)
        for (i, x) in enumerate(self.data):
            if i % 20 == 0:
                s+= '\n'
            s += '  {0:02x}'.format(x)
        s += '\n\nChecksum: %x' % self.checksum
        return s

    def calc_checksum(self):
        if self.header.is_tail():
            return 0
        else:
            header_chksum = self.header.calc_checksum()
            data_chksum = sum(self.data) % 256
            chksum = (header_chksum + data_chksum) % 256
            debug('header_chksum: %d, data_chksum: %d, chksum: %d' %
                  (header_chksum,data_chksum, chksum))
            return chksum

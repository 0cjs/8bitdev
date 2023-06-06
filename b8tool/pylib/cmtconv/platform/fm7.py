''' cmtconv.platform.fm7
'''
from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PulseDecoder, PULSE_MARK, PULSE_SPACE, \
        Encoder, silence, sound
import  cmtconv.audio

####################################################################

class Block(object):
    'FM-7 tape block'
    #
    # The FM-7 block format is as follows:
    #
    # Gap/Leader of FF bytes
    #
    # Block types:
    #   00 - Header block
    #   01 - Data block
    #   FF - end block
    #
    # Block header
    # 01 3C     Magic
    # xx        Block type
    # xx        Block length
    # data...
    # xx        Checksum
    #
    # Header block
    # 0-7       filename, padded with spaces
    # 8         file format - (00 - BASIC, 01 - DATA, 02 - MACHINE LANGUAGE)
    # 9         ASCII/Binary - (00 - binary, FF - ASCII)
    # 10-15     reserved
    #

    platform = "Fujitsu FM-7"

    MAGIC     = b'\x01\x3c'

    BLOCK_HEADER_LEN = 4

    class BlockType(IntEnum):
        HEADER  = 0x00
        DATA    = 0x01
        END     = 0xff

    class FileType(IntEnum):
        BASIC               = 0x00
        DATA                = 0x01
        MACHINE_LANGUAGE    = 0x02

    class Binary(IntEnum):
        BINARY  = 0x00
        ASCII   = 0xFF

    class ChecksumError(ValueError) : pass

    @classmethod
    def _calc_checksum(cls, data):
        return sum(data) & 0xff

    @classmethod
    def _check_magic(cls, headerbytes):
        ''' Raise an exception if the first two values in `headerbytes` are
            not the correct magic value.
        '''
        if bytes(headerbytes[0:2]) != cls.MAGIC:
            raise ValueError('Bad magic,'
                ' expected=${:02X}{:02X} actual=${:02X}{:02X}'.format(
                    cls.MAGIC[0], cls.MAGIC[1],
                    headerbytes[0], headerbytes[1]))

    @property
    def is_eof(self):
        return False

    def __repr__(self):
        return '{}.{}( data={})'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                self._data)

class HeaderBlock(Block):
    HEADERLEN = 20

    @classmethod
    def make_block(cls, file_name, file_type, binary ):
        # FIXME: check stuff, pad file_name
        return cls(file_name, file_type, binary)

    def __init__(self, file_name=None, file_type=None, binary=None):
        'For internal use only.'
        self._file_name = file_name
        self._file_type = file_type
        self._binary = binary

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        if headerbytes[2] != Block.BlockType.HEADER:
            raise ValueError('Bad type for header block ${:02X}'.format(
                headerbytes[2]))
        if headerbytes[3] != cls.HEADERLEN:
            raise ValueError('Bad length for header block: ${:02X}'.format(
                headerbytes[3]))
        return (cls(), cls.HEADERLEN)

    def setdata(self, data, checksum=None):
        # Header checksum seems to include the length byte,
        # which is always 20 (0x14)
        expected_checksum = self._calc_checksum(
            bytearray((self.HEADERLEN,)) + data)
        if checksum is not None and expected_checksum != checksum:
            raise self.ChecksumError('expected=${:02X}, actual=${:02X}'.format(
                expected_checksum, checksum))
        self._file_name = data[0:8].decode()
        self._file_type = data[8]
        if self._file_type not in list(self.FileType):
            raise self.ChecksumError(
                'Unrecognised file type: {:02X}'.format(self._file_type))
        self._binary = data[9]
        if self._binary not in list(self.Binary):
            raise self.ChecksumError(
                'Unrecognised binary flag: {:02X}'.format(self._file_type))

    @property
    def filename(self):
        return self._file_name

    @property
    def checksum(self):
        data = bytearray((self.HEADERLEN,))
        data.extend(self._data())
        return self._calc_checksum(data)

    @property
    def filedata(self):
        return bytearray()

    def _data(self):
        b = bytearray(self._file_name, encoding='ascii') # FIXME: pad
        b.append(self._file_type)
        b.append(self._binary)
        b.append(self._binary) # Note: seems to be replicated
        b.extend((0,0,0,0,0,0,0,0,0))
        return b

    def to_bytes(self):
        b = bytearray(self.MAGIC)
        b.append(self.BlockType.HEADER)
        b.append(self.HEADERLEN)
        b.extend(self._data())
        b.append(self.checksum)
        return b    

class DataBlock(Block):

    @classmethod
    def make_block(cls):
        return cls()

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        if headerbytes[2] != Block.BlockType.DATA:
            raise ValueError('Bad type for data block ${:02X}'.format(
                headerbytes[2]))
        return (cls(), headerbytes[3])

    def setdata(self, data, checksum=None):
        expected_checksum = (self._calc_checksum(data) + len(data) + 1) % 0x100
        v3('Checksum = {:02X}, Expected = {:02X}', checksum, expected_checksum)
        if checksum is not None and expected_checksum != checksum:
            raise self.ChecksumError('expected={:02X}, actual={:02X}'.format(
                expected_checksum, checksum))
        self.data = data

    @property
    def checksum(self):
        return (self._calc_checksum(self.data) + len(self.data) + 1) % 0x100

    @property
    def filedata(self):
        return self.data

    def to_bytes(self):
        b = bytearray(self.MAGIC)
        b.append(self.BlockType.DATA)
        b.append(len(self.data))
        b.extend(self.data)
        b.append(self.checksum)
        return b

class EndBlock(Block):

    @classmethod
    def make_block(cls):
        return cls()

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        if headerbytes[2] != Block.BlockType.END:
            raise ValueError('Bad type for data block ${:02X}'.format(
                headerbytes[2]))
        return (cls(), 0)

    @property
    def is_eof(self):
        return True

    @property
    def filedata(self):
        return bytearray()

    def to_bytes(self):
        b = bytearray(self.MAGIC)
        b.append(self.BlockType.END)
        b.append(0)
        return b


class FileReader(object):
    'Read FM-7 data from audio'

    def __init__(self):
        self.pd = PulseDecoder(1100, 2, 2200, 2, False, True, (0,), (1,1,),
            (0.2, 0.2), (0.25, 0.5))


    def read_leader(self, pulses, i_next):
        '''Detect the next leader, read, confirm then return next pulse'''

        # Note: recordings often seem to have a rising amplitude
        # envelope that covers at least some of the first byte,
        # often several bytes. This reduces accuracy of mark/space detection.
        #
        # So, we skip over a few first potential matches.
        # Note that the leader bytes are FF, so the
        # pattern is s [mmmm mmmmm] mm

        # Find some possible 1 bits

        # FIXME: want to be able to detect multiple marks, as per multiple
        # spaces
        # as this will be very common, push down to audio module as a helper
        # function "probe_leader_start"
        leader_start = i_next
        (leader_start,_) = self.pd.next_mark(pulses, leader_start)
        v3('Leader mark detected at %d - %fs' %
            (leader_start, pulses[leader_start][0]))
        # (leader_start,_) = self.pd.next_mark(pulses, leader_start+1)
        # v3('Leader mark detected at %d - %fs' %
        #     (leader_start, pulses[leader_start][0]))
        # Find possible start bit of next byte
        leader_start = self.pd.next_space(pulses, leader_start, 2)
        v3('Leader space detected at %d - %fs' %
            (leader_start, pulses[leader_start][0]))

        (leader_start,_) = self.pd.next_mark(pulses, leader_start+1)
        v3('Leader mark detected at %d - %fs' %
            (leader_start, pulses[leader_start][0]))

        # Rewind back to start bit
        leader_start = leader_start-2

        # Try to read a byte
        (i_next, b) = self.pd.read_byte(pulses, leader_start)
        n_bs = 1

        # Read until 0x01
        while b != 0x01:
            (i, b) = self.pd.read_byte(pulses, i_next)
            if b != 0x01:
                if b != 0xff:
                    v3('Ignoring non 0xff byte in leader: {}', b)
                i_next = i
                n_bs += 1

        v3('Number of leader bytes read before $01: {}', n_bs)

        return i_next

    def read_leader2(self, pulses, i_next):
        # Try to read a byte
        (i_next, b) = self.pd.read_byte(pulses, i_next)

        # Read until something other than 0xff
        while b == 0xff:
            (i, b) = self.pd.read_byte(pulses, i_next)
            if b == 0xff:
                i_next = i

        return i_next


    # returns ( int, ( block, ) )
    def read_block(self, pulses, i_next):
        # leader
        i_next = self.read_leader(pulses, i_next)
        # header
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, Block.BLOCK_HEADER_LEN)
        v3('headerbytes={}'.format(bs))
        if (bs[2] == Block.BlockType.HEADER):
            (block, datalen) = HeaderBlock.from_header(bs)
        elif (bs[2] == Block.BlockType.DATA):
            (block, datalen) = DataBlock.from_header(bs)
        elif (bs[2] == Block.BlockType.END):
            (block, datalen) = EndBlock.from_header(bs)
        else:
            raise ValueError('Unrecognised block type: {:02X}'.format(bs[2]))
        v3('Block length: %d' % datalen)
        # consume data
        if datalen > 0:
            (i_next, bs) = self.pd.read_bytes(pulses, i_next, datalen)
            (i_next, checksum) = self.pd.read_byte(pulses, i_next)
            v3('data={}, checksum={:02X}', bs, checksum)
            block.setdata(bs, checksum)
        return (i_next, block)

    # returns ( int, ( block, ) )
    def read_blocks(self, pulses, i_next):
        #i_next = self.read_leader(pulses, i_next)
        blocks = []
        block = None
        while block is None or not block.is_eof:
            (i_next, block) = self.read_block(pulses, i_next)
            blocks.append(block)
            # search for gap
            while i_next < len(pulses) and pulses[i_next][2] < (1.3/2200.0):
                i_next += 1
            if i_next < len(pulses) - 1:
                i_next += 1
                v3('post-footer gap at {} - {}s',
                    i_next, pulses[i_next][0])
        return (i_next, blocks)

    # read a file
    # returns ( int, ( block, ) )
    def read_file(self, pulses, i_next):
        return self.read_blocks(pulses, i_next)


def read_block_bytestream(stream):
    ''' Read bytes from `stream`, parse them as FM-7 blocks
        and return a sequence of the block objects.
    '''
    blocks = []
    blk = None
    while blk is None or not blk.is_eof:
        bh = stream.read(Block.BLOCK_HEADER_LEN)
        if bh[2] == Block.BlockType.HEADER:
            v3('Header block')
            (blk, datalen) = HeaderBlock.from_header(bh)
            bs = stream.read(datalen)
            chksum = stream.read(1)
            blk.setdata(bs, chksum[0])
        elif bh[2] == Block.BlockType.DATA:
            v3('Data block')
            (blk, datalen) = DataBlock.from_header(bh)
            bs = stream.read(datalen)
            chksum = stream.read(1)
            blk.setdata(bs, chksum[0])
        elif bh[2] == Block.BlockType.END:
            v3('End block')
            (blk, datalen) = EndBlock.from_header(bh)
        else:
            raise ValueError('Unrecognised block type: {:02X}'.format(bh[2]))
        blocks.append(blk)
    return tuple(blocks)

def blocks_from_bin(stream, loadaddr=0x0000, filename=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as data to be loaded
        as it would be saved on an FM-7. `loadaddr` is the load
        address for the file.

        If `filename` is `None`, a default (perhaps empty) filename
        will be generated. Otherwise `filename` will be processed with
        `native_filename()`.
    '''
    # FIXME: Need a flag to indicate file type - binary/basic
    blocks = []
    basic_blk = 0
    blk_num = 1
    addr = loadaddr
    while True:
        filedata = stream.read(0x100)
        if len(filedata) > 0:
            blocks.append(Block.make_block(Block.BINARY, basic_blk, filename,
                blk_num, addr, filedata))
            if len(filedata) == 0x100:
                blk_num += 1
                addr += len(filedata)
            else:
                break
        else:
            break

    blocks.append(Block.make_block(Block.AUX, basic_blk, filename,
        blk_num, loadaddr, bytearray( (0x7e,) )))
    return blocks

####################################################################

class FileEncoder(object):
    def __init__(self):
        self.encoder = Encoder(1100, 2, 2200, 2, False, True, (0,), (1,1))

        # long lead in for header and first data block
        self.long_lead_in = self.encoder.encode_bytes( (0xff,) * 255 )

        # Lead-in
        self.lead_in = self.encoder.encode_bytes( (0xff,) * 10 )

        # Lead-out
        self.lead_out = self.encoder.encode_bytes( (0xff,) * 4 )

    def encode_block(self, blk, long_leader = False):
        res = []
        if long_leader:
            res.extend(self.long_lead_in)
        else:
            res.extend(self.lead_in)
        res.extend(self.encoder.encode_bytes(blk.to_bytes()))
        res.extend(self.lead_out)
        return (sound(res), silence(.01))

    def encode_blocks(self, blocks):
        res = (silence(2.0),)

        for (n, b) in enumerate(blocks):
            res += self.encode_block(b, n < 2)

        return res

    def encode_file(self, blocks):
        return self.encode_blocks(blocks)


def write_file_bytestream(blocks, stream):
    bs = bytes(chain(*( b.filedata for b in blocks)))
    stream.write(bs)

def parameters():
    return dict()

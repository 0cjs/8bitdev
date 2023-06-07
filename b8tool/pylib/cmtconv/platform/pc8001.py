''' cmtconv.platform.pc8001
'''
from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PulseDecoder, PULSE_MARK, PULSE_SPACE, \
        Encoder, silence, sound
import  cmtconv.audio

####################################################################

class Block(object):
    ''' PC-8001 tape block

        Saves from the PC-8001 have no blocking, so we treat them as
        a single "block."

        The lead-in is a long stream of 1200 Hz, followed by a long stream
        of 2400 Hz. The data follows, and the lead-out is a long stream of
        1200 Hz.

        Binary saves (monitor ``W`` command) are just the raw binary data.

        BASIC saves are a simple header containing 9× $D3 bytes, the
        filename, a $00 byte, a short period (~650 pulses) of 2400 Hz, and
        the BASIC data.
    '''

    platform = "NEC PC-8001"

    MIN_FIRST_BLOCK_LEN = 10

    class BlockType(IntEnum):
        BASICHEADER  = 0x00
        BASICTEXT    = 0x01
        BINARYDATA   = 0x02

    def __repr__(self):
        return '{}.{}( data={})'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                self._data)

class BASICHeaderBlock(Block):

    MAGIC               = b'\xd3' * 10
    FILE_NAME_LENGTH    = 6

    @classmethod
    def make_block(cls, file_name):
        return cls(file_name)

    def __init__(self, file_name=None):
        'For internal use only.'
        self._file_name = file_name

    @classmethod
    def _check_magic(cls, bs):
        if bytes(bs[0:len(cls.MAGIC)]) != cls.MAGIC:
            raise ValueError('Bad magic,'
                ' expected={} actual={}'.format(repr(cls.MAGIC), repr(bs)))

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        return (cls(), 6)

    def setdata(self, data, checksum=None):
        self._file_name = data.decode().rstrip('\0')

    @property
    def filename(self):
        return self._file_name

    @property
    def checksum(self):
        return None

    @property
    def filedata(self):
        return bytearray()

    def to_bytes(self):
        bs = self.MAGIC + self._file_name.encode('iso-8859-1') + bytes(6)
        return bs[0:len(self.MAGIC)+self.FILE_NAME_LENGTH]


class BASICTextBlock(Block):

    def setdata(self, data):
        self._data = data

    @property
    def filedata(self):
        return self._data

    def to_bytes(self):
        return self._data



class BinaryDataBlock(Block):

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


class FileReader(object):
    'Read FM-7 data from audio'

    def __init__(self):
        self.pd = PulseDecoder(2400, 8, 1200, 4, False, True, (0,), (1,1,),
                               (0.25,0.5))


    def read_leader(self, pulses, i_next):
        '''Detect the next leader, read, confirm then return next pulse'''

        i_next = self.pd.next_space(pulses, i_next, 8)
        v3('Leader spaces detected at %d - %fs' %
            (i_next, pulses[i_next][0]))
        # read N pulses

        (i_next,_) = self.pd.next_mark(pulses, i_next)
        v3('Leader marks detected at %d - %fs' %
            (i_next, pulses[i_next][0]))
        # read N pulses

        i_next = self.pd.next_space(pulses, i_next, 2)

        v3('End of leader at %d - %fs' % (i_next, pulses[i_next][0]))
        return i_next


    # returns ( int, ( block, ) )
    def read_block(self, pulses, i_next):
        # leader
        i_next = self.read_leader(pulses, i_next)
        # header
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, BASICHeaderBlock.MIN_FIRST_BLOCK_LEN)
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
        i_next = self.read_leader(pulses, i_next)

        # Try to read BASIC header
        n = Block.MIN_FIRST_BLOCK_LEN
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, n)
        try:
            (hdrblk, l) = BASICHeaderBlock.from_header(bs)
            (i_next, bs) = self.pd.read_bytes(pulses, i_next, l)
            hdrblk.setdata(bs)

            # Intra-block 2400Hz pulses
            i_next = self.pd.expect_marks(pulses, i_next, int(2.5 * 8))
            # Start bit for next block
            i_next = self.pd.next_space(pulses, i_next, 2)

            data = bytearray()
            (i_next, b) = self.pd.read_byte(pulses, i_next)
            data.append(b)
            eof = False
            while not eof:
                try:
                    (i_next, b) = self.pd.read_byte(pulses, i_next)
                    data.append(b)
                except:
                    eof = True
            textblk = BASICTextBlock()
            textblk.setdata(data)
            return (i_next, (hdrblk, textblk))

        except ValueError:
            raise RuntimeError('XXX: WriteMe for BinaryDataBlock')



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
    return { 'edge_gradient_factor' : 0.4 }

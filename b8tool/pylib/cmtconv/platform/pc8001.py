''' cmtconv.platform.pc8001
'''
from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PulseDecoder, PULSE_MARK, PULSE_SPACE, \
        Encoder, silence, sound, ReadError
import  cmtconv.audio

####################################################################

class Block(object):
    ''' PC-8001 tape block

        Saves from the PC-8001 have no blocking, so we treat them as
        a single "block."

        The lead-in is a long stream of 1200 Hz, followed by a long stream
        of 2400 Hz. The data follows, and the lead-out is a long stream of
        1200 Hz.

        Mark is     2400Hz for 8 pulses
        Space is    1200Hz for 4 pulses
        Bits are    "reversed" (LSB first)
        Start is    (space,)
        Stop is     (mark, mark)

        A suitable analyze-cmt command line is:
            analyze-cmt -m 2400 --mark-pulses 8 -s 1200 --space-pulses 4 \
                  -B --reverse-bits --start s --stop mm ${input} ${outpu}


        BASIC saves are a simple header block containing 10× $D3 bytes,
        6 bytes for the filename, padded with $00, then  a short period
        (~650 pulses) of 2400 Hz, followed by the BASIC text block.
        The BASIC text block is just the tokenized MS-BASIC with no header,
        length, checksum or field delimiters. The BASIC program is followed
        by 10 bytes of 0x00.

        FIXME: data blocks can be > 256 bytes...but only one 'block'
            - multiple 'sub-blocks' encoded via field delims?

        For binary saves (monitor ``W`` command) ':' (0x3A) is used as
        a field delimiter. They have the following structure:
            ':' (0x3A)
            (0x00, 0x01) - load address (HI, LO))
            (checksum,)
            ':' (0x3A)
            (length,)
            (data, ... )
            (checksum, )
                - checksum = 0x0100 - ((length + sum(data)) & 0xff)

            [
                ':' (0x3A)
                (length,)
                (data, ...)
                (checksum,)
            ]*

            ':' (0x3A)
            00
            00

    '''

    platform = "NEC PC-8001"

    MIN_FIRST_BLOCK_LEN = 10

    class BlockType(IntEnum):
        BASICHEADER  = 0x00
        BASICTEXT    = 0x01
        BINARYDATA   = 0x02

    class ChecksumError(ValueError) : pass

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
            raise ReadError('Bad magic,'
                ' expected={} actual={}'.format(repr(cls.MAGIC), repr(bs)))

    @classmethod
    def from_header(cls, headerbytes):
        cls._check_magic(headerbytes)
        return (cls(), 6)

    def setdata(self, data, checksum=None):
        self._file_name = data.decode().rstrip('\0')

    @property
    def isoef(self):
        return False

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

    @classmethod
    def make_block(cls):
        return cls()

    @property
    def isoef(self):
        return True

    def setdata(self, data):
        self._data = data

    @property
    def filedata(self):
        return self._data

    def to_bytes(self):
        return self._data + bytes( (0x00, ) * 10 )



class BinaryDataBlock(Block):
    '''
    '''

    @classmethod
    def _calc_checksum(cls, data):
        return (0x100 - (sum(data) % 0x100)) % 0x100

    @classmethod
    def make_block(cls, addr = None):
        return cls(addr)

    def __init__(self, addr = None):
        'For internal use only.'
        self.addr = addr

    @classmethod
    def from_header(cls, headerbytes, first = False):
        # First block has load address
        if first:
            if headerbytes[0] != 0x3A:
                raise ReadError('First byte must be 0x3A: {}\n'
                                .format(repr(headerbytes)))
            else:
                addr = 256 * headerbytes[1] + headerbytes[2]
                blk = cls(addr)
            bs = headerbytes[4:]
        else:
            blk = cls()
            bs = headerbytes

        if bs[0] != 0x3A:
            raise ReadError('Expected 0x3A at start of block, got {:02X}'
                            .format(bs[0]))
        length = bs[1]
        return (blk, length)


    def setdata(self, data, checksum=None):
        expected_checksum = self._calc_checksum([len(data)] + list(data))
        if checksum is not None:
            v3('Checksum = {:02X}, Expected = {:02X}', checksum,
                expected_checksum)
        if checksum is not None and expected_checksum != checksum:
            raise self.ChecksumError('expected={:02X}, actual={:02X}'.format(
                expected_checksum, checksum))
        self.data = data

    @property
    def isoef(self):
        return len(self.data) == 0

    @property
    def checksum(self):
        return self._calc_checksum([len(self.data)] + list(self.data))

    @property
    def filedata(self):
        return self.data

    def to_bytes(self):
        b = bytearray()
        if self.addr is not None:
            b.extend(b':')
            b.append((self.addr >> 8) & 0xff)
            b.append(self.addr & 0xff)
            b.append(self._calc_checksum(b[1:]))
        b.extend(b':')
        b.append(len(self.data))
        b.extend(self.data)
        b.append(self.checksum)
        return b


class FileReader(object):
    'Read PC-8001 data from audio'

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

        i_next = self.pd.next_space(pulses, i_next, 4)

        v3('End of leader at %d - %fs' % (i_next, pulses[i_next][0]))
        return i_next


    # read a file
    # returns ( int, ( block, ) )
    def read_file(self, pulses, i_next):
        i_next = self.read_leader(pulses, i_next)

        i_start = i_next
        # FIRST byte = 0xD3 for BASIC header, 0x3A for binary

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
                except ReadError as e:
                    v3('Error on presumed last byte:\n{}'.format(e))
                    eof = True
            textblk = BASICTextBlock()
            textblk.setdata(data)
            return (i_next, (hdrblk, textblk))

        except ReadError:
            # Read Binary data
            try:
                blocks = []
                i_next = i_start
                n = 6 # FIXME: put in class
                (i_next, bs) = self.pd.read_bytes(pulses, i_next, n)
                (blk, l) = BinaryDataBlock.from_header(bs, first = True)
                v4('Block length: {:02X}'.format(l))

                (i_next, bs) = self.pd.read_bytes(pulses, i_next, l)
                v4('bytes read: {}', repr(bs))
                (i_next, checksum) = self.pd.read_byte(pulses, i_next)
                blk.setdata(bs, checksum)

                blocks = [blk]
                eof = False
                while not eof:
                    (i_next, bs) = self.pd.read_bytes(pulses, i_next, 2)
                    (blk,l) = BinaryDataBlock.from_header(bs)
                    (i_next, bs) = self.pd.read_bytes(pulses, i_next, l)
                    v4('bytes read: {}', repr(bs))
                    (i_next, checksum) = self.pd.read_byte(pulses, i_next)
                    blk.setdata(bs, checksum)
                    blocks.append(blk)
                    if l == 0:
                        eof = True

                return (i_next, tuple(blocks))

            except ReadError:
                raise ReadError('Unable to read BASIC or BINARY block')



def read_block_bytestream(stream):
    blocks = []
    blk = None
    bs = stream.read()
    magiclen = len(BASICHeaderBlock.MAGIC)
    if bs[0:magiclen] == BASICHeaderBlock.MAGIC:
        v3('Header block')
        (blk, datalen) = BASICHeaderBlock.from_header(bs[0:magiclen])
        blk.setdata(bs[magiclen:magiclen+datalen])
        blocks.append(blk)
        blk = BASICTextBlock()
        blk.setdata(bs[magiclen+datalen:])
        blocks.append(blk)
    else:
        raise ValueError('FIXME: BinaryDataBlock not yet supported')
    return tuple(blocks)

def blocks_from_bin(stream, loadaddr=0x8020, filename=None, filetype=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as data to be loaded
        as it would be saved on a PC-8001.

        If `filename` is `None`, a default (perhaps empty) filename
        will be generated. Otherwise `filename` will be processed with
        `native_filename()`.
    '''
    if filetype is None or filetype == 'BASIC':
        loadaddr = 0x8020
        blk = BASICTextBlock()
        blk.setdata(stream.read())
        return [ BASICHeaderBlock.make_block(filename), blk ]
    elif filetype == 'BINARY':
        bs = stream.read()
        blk = BinaryDataBlock.make_block(loadaddr)
        n = min(0xFF, len(bs))
        blk.setdata(bs[0:n])
        blocks = [blk]
        bs = bs[n:]
        n = min(0xFF, len(bs))
        while n > 0:
            blk = BinaryDataBlock.make_block()
            blk.setdata(bs[0:n])
            blocks.append(blk)
            bs = bs[n:]
            n = min(0xFF, len(bs))
        blk  = BinaryDataBlock.make_block()
        blk.setdata(bytearray())
        blocks.append(blk)
        return blocks
    else:
        raise RuntimeError('Unsupported filetype: {}', filetype)



####################################################################

class FileEncoder(object):
    def __init__(self):
        self.encoder = Encoder(2400, 8, 1200, 4, False, True, (0,), (1,1))

        self.file_leader = self.encoder.encode_bit(0) * 256
        self.block_leader = self.encoder.encode_bit(1) * 128


    #
    # block     : Block
    # ->
    # audio     : [AudioMarker]
    def encode_block(self, blk):
        widths = []
        widths.extend(self.block_leader)
        widths.extend(self.encoder.encode_bytes(blk.to_bytes()))
        widths.extend(self.block_leader)
        return [sound(widths)]

    #
    # blocks    : Block
    # ->
    # audio     : (AudioMarker,)
    #
    def encode_blocks(self, blocks):
        if isinstance(blocks[0], BASICHeaderBlock):
            audio = [sound(self.file_leader)]
            for b in blocks:
                audio.extend(self.encode_block(b))
            return tuple(audio)
        else:
            audio = list(self.file_leader)
            audio.extend(self.block_leader)
            for b in blocks:
                audio.extend(self.encoder.encode_bytes(b.to_bytes()))
            audio.extend(self.block_leader)
            return (sound(audio),)


    def encode_file(self, blocks):
        return self.encode_blocks(blocks)


def write_file_bytestream(blocks, stream):
    bs = bytes(chain(*( b.filedata for b in blocks)))
    stream.write(bs)

def parameters():
    return { 'edge_gradient_factor' : 0.4 }

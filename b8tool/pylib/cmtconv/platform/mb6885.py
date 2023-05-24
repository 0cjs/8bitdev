''' cmtconv.platform.mb6885
'''
from    enum  import IntEnum
from    itertools  import chain
from    cmtconv.logging  import *
from    cmtconv.audio  import PULSE_MARK, PULSE_SPACE, Encoder, silence, sound
import  cmtconv.audio

####################################################################

class Block(object):
    'MB-6885 tape block'
    #
    # The MB-6686 block format is as follows:
    #
    #
    # Format is the same for each block, there is no separate header block
    #
    # Leader: 64 bytes of 0xff
    #   Note: there are 64 bytes of 0xff for the leader, which is terminated
    #         by 0x01. Could consider this separate from the header.
    #
    # Header:
    #
    # Offset    Description
    # 0:        Magic: 0xff, 0x01
    # 2:        File type:
    #               BASIC first block: 0x10, followed by block_num
    #               BASIC second block: 0x00, followed by block_num
    #               BINARY: 0x01
    #               BINARY last block: 0x00
    # 3:        BASIC block number, 0x00 for BINARY
    # 4:        File name, 8 bytes including suffix, .S for BASIC, .B for BINARY
    # 12:       Block number: Starts at 1, always 0x01 for BASIC
    # 13:       Block data length (excludes header)
    # 14:       Start address (HI, LO) - always 0600 for BASIC
    # 16:       Header checksum
    # 17..n:    data
    # n+1:      data checksum
    # n+2:      Magic: 0x00
    platform = "Hitachi MB-6885"

    HEADERLEN = 17
    MAGIC     = b'\xff\x01'
    END_MAGIC = b'\x00'

    class FileType(IntEnum):
        BASIC  = 0x10 # BASIC "main" block
        BINARY = 0x01 # BINARY "main" block
        AUX    = 0x00 # Used for BASIC intermediate blocks, last BINARY block
    BASIC  = FileType.BASIC
    BINARY = FileType.BINARY
    AUX    = FileType.AUX

    class ChecksumError(ValueError) : pass

    @classmethod
    def make_block(cls, file_type, basic_block_num, file_name, block_num, addr,
            data=b''):
        if file_type not in cls.FileType:
            raise ValueError('file_type must be BASIC, BINARY or AUX, not {}'
                .format(repr(file_type)))
        have_suffix = False
        if len(file_name) >= 2:
            suffix = file_name[-2:]
            if suffix[0] == '.':
                have_suffix=True
                if suffix not in ('.B', '.S'):
                    raise ValueError(
                        'Filename suffix must be .S (BASIC) or .B (BINARY)'
                        ' not {}'.format(repr(suffix)))
                if file_type == cls.FileType.BASIC and suffix != '.S':
                    raise ValueError('file name suffix must be .S for BASIC')
                if file_type == cls.FileType.BINARY and suffix != '.B':
                    raise ValueError('file name suffix must be .B for BINARY')
        if not have_suffix:
            if   file_type == cls.FileType.BASIC:   file_name += '.S'
            elif file_type == cls.FileType.BINARY:  file_name += '.B'
            else: raise ValueError(
                'Filename suffix must be .S (BASIC) or .B (BINARY)')
        # Pad file_name to 8 characters including suffix
        file_name_base = bytearray(file_name[:-2], encoding='ascii')
        if len(file_name_base) > 6:
            raise ValueError('file name must be <= 8 including suffix, '
                ' length = {}'.format(len(file_name)))
        suffix = bytearray(file_name[-2:], encoding='ascii')
        fn_pad = bytearray(b'        ')
        fn_pad[:len(file_name_base)] = file_name_base
        fn_pad[-2:] = suffix
        v3('fn_pad = {}', fn_pad)
        block = cls(file_type, basic_block_num, fn_pad, block_num, addr,
            data)
        return block

    @classmethod
    def _calc_checksum(cls, data):
        return (((sum(data) & 0xff) ^ 0xff) + 1) & 0xff

    @classmethod
    def from_header(cls, headerbytes):
        ''' Create a `Block` from exactly `HEADERLEN` header bytes, returning
            a pair ``(block, datalen)`` of the new block and the data
            length given in the header. The caller will normally read
            ``datalen`` more bytes plus the checksum byte and final magic
            from the source and call `setdata()` with those.
        '''
        v3('reading header: {}', headerbytes)
        if len(headerbytes) != cls.HEADERLEN:
            raise ValueError('Bad length: expected={} actual={}'
                .format(cls.HEADERLEN, len(headerbytes)))
        cls._check_magic(headerbytes)
        datalen = headerbytes[13]
        if datalen == 0:
            datalen = 256
        checksum = headerbytes[16]
        expected_checksum = cls._calc_checksum(headerbytes[:16])
        if expected_checksum != checksum:
            raise cls.ChecksumError('expected={:02X}, actual={:02X}'
                .format(expected_checksum, checksum))
        # FIXME: should keep track of overall file type from first block
        file_type = cls.FileType(headerbytes[2])
        basic_block_num = headerbytes[3]
        file_name = headerbytes[4:12].decode()
        block_num = headerbytes[12]
        addr = headerbytes[14] * 256 + headerbytes[15]

        block = cls.make_block(file_type, basic_block_num, file_name,
            block_num, addr)
        return (block, datalen)

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

    def __init__(self, file_type, basic_block_num, file_name, block_num, addr,
            data):
        'For internal use only.'
        self.file_type = file_type
        self.basic_block_num = basic_block_num
        self.file_name = file_name
        self.block_num = block_num
        self.addr = addr
        self._data = data

    def setdata(self, data, checksum=None, end_magic=None):
        self._data = bytes(data)
        expected_checksum = self._calc_checksum(self._data)
        if checksum is not None and expected_checksum != checksum:
            raise self.ChecksumError('expected={:02X}, actual={:02X}'
                .format(expected_checksum, checksum))
        if end_magic is not None and end_magic != self.END_MAGIC[0]:
            raise ValueError('Bad magic at end of block ${:02X}: '
                'expected=${:02X}, actual=${:02X}'.format(
                    self.block_num, self.END_MAGIC[0], end_magic))

    @property
    def is_eof(self):
        v3( 'is_eof, file_type = {:s}, basic_block_num = {:s}'
            ', addr = {:04X}, data_len = {:d}'
            .format(str(self.file_type), str(self.basic_block_num),
                self.addr, len(self._data)
            ))
        if self.file_type == self.FileType.AUX:
            if self.basic_block_num == 0:
                # BINARY uses file type and block num of zero for last block
                # FIXME: Looks like we sometimes get non-zero number here...
                # Should keep track of file format and exit on
                # AUX....
                # Note: last block for BINARY seems to always be of length 1,
                # contain 0x7e and have the start address as the block address.
                return True
            else:
                # BASIC
                # We have variable length blocks that seem to be filled
                # with 0xff, and the last block seems to be length 1
                v3('is_eof, AUX, data = {:s}', str(self._data))
                return (self.addr == 0x0600 and len(self._data) == 1
                    and self._data[0] == 0xff)
        else:
            return False

    # FIXME: return empty data for BASIC AUX blocks
    # Need to distinguish "file" data vs (raw) block data
    @property
    def filedata(self):
        return self._data

    @property
    def filename(self):
        return self.file_name

    @property
    def filetype(self):
        return self.file_type

    def to_bytes(self):
        b = bytearray(self.MAGIC)
        b.append(self.file_type)
        b.append(self.basic_block_num)
        b.extend(self.file_name)
        b.append(self.block_num)
        b.append(0 if len(self._data) == 0x100 else len(self._data))
        b.append((self.addr >> 8) & 0xff)
        b.append(self.addr & 0xff)
        header_checksum = self._calc_checksum(b)
        b.append(header_checksum)
        b.extend(self._data)
        b.append(self._calc_checksum(self._data))
        b.extend(self.END_MAGIC)
        return b

    def __repr__(self):
        return ('{}.{}(file_type={}, basic_block_num={}, file_name={}, '
            'block_num={}, addr={}, data={}').format(
                self.__class__.__module__,
                self.__class__.__name__,
                self.file_type, hex(self.basic_block_num),
                self.file_name, hex(self.block_num),
                hex(self.addr), self._data)

class PulseDecoder(cmtconv.audio.PulseDecoder):
    def __init__(self, *args) :
        super().__init__(*args)

    def expect_stop_bits(self, pulses, i_next):
        (i_next, bit) = self.read_bit(pulses, i_next)
        if bit != 1:
            raise ValueError('Expected 1 for stop bit')
        # The last stop bit is often a malformed pulse
        for i in range(0, 15):
            e = pulses[i_next + i]
            if self.classify_pulse(e) != PULSE_MARK:
                raise ValueError('Expected stop bit, non MARK pulse at %d - %fs' %
                        (i_next, pulses[i_next][0]))
        # last pulse is often malformed, skip
        return i_next + 16


class FileReader(object):
    'Read MB-6885 data from audio'

    def __init__(self):
        self.pd = PulseDecoder(2400, 16, 1200, 8, False, True, (0,), (1,1,))

    # This is horribly messy, as we are geting incorrect starting pulses
    # as we only have H/L, not H,M,L
    #
    # Depending on whether the first edge is rising or falling
    # and the cutoff for H/L, the first pulse can be merged with silence
    # before it
    # The workaround is to check for 7 or 8 space cycles, then
    #
    # FIXME: below is better solution
    #
    # This could be replaced by loosening it: search for 8 consecutive spaces
    # then read bytes until we get something other than 0xff

    # read_first_bit
    def read_first_bit(self, pulses, i_next):
        '''Read the first start bit, which can have 7 or 8 space pulses'''
        v3('read_first_bit: %d - %s' % (i_next,str(pulses[i_next:i_next+12])))
        i_next = self.pd.expect_spaces(pulses, i_next, 7)
        if self.pd.classify_pulse(pulses[i_next]) == PULSE_SPACE:
            i_next += 1
            # Yes, 9... if we miss the first 8 cycles and catch the second,
            # the "long mark" on the last stop bit can get detected as the
            # start of 8 spaces for the stop...
            if self.pd.classify_pulse(pulses[i_next]) == PULSE_SPACE:
                v3('read_first_bit: got 9 spaces')
                i_next += 1
            else:
                v3('read_first_bit: got 8 spaces')
        else:
            v3('read_first_bit: got 7 spaces')
        return (i_next, 0)

    # read_first_byte
    def read_first_byte(self, pulses, i_next):
        (i_next, bit) = self.read_first_bit(pulses, i_next)
        (i_next, b) = self.pd.read_raw_byte(pulses, i_next)
        i_next = self.pd.expect_stop_bits(pulses, i_next)
        return (i_next, b)

    def read_leader(self, pulses, i_next):
        '''Detect the next leader, read, confirm then return next pulse'''
        leader_start = self.pd.next_space(pulses, i_next, 7)
        v3('Leader pulses detected at %d - %fs' %
            (leader_start, pulses[leader_start][0]))
        (i_next, b) = self.read_first_byte(pulses, leader_start)
        # We can miss the first byte due to analogue effects limiting the
        # amplitude of waves, ruining detection.
        # Could attempt to fix this with a moving average.
        # Instead, just accept we might miss some FF bytes in the leader
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, 32)
        bs = bytearray( (b,) ) + bs
        indices = []
        while True:
            indices.append(i_next)
            (i_next, b) = self.pd.read_byte(pulses, i_next)
            if b == 0xFF:
                bs = bs + bytearray( (b,) )
            elif b == 0x01:
                i_next = indices[-2]
                break
            else:
                raise ValueError("Unexpected byte reading leader: %02x" % b)
        for i in range(0,len(bs)):
            if bs[i] != 0xff:
                raise ValueError(
                    'Expected 64 bytes of 0xff for leader, got: %s' % str(bs))
        return i_next

    # returns ( int, ( block, ) )
    def read_block(self, pulses, i_next):
        # leader
        i_next = self.read_leader(pulses, i_next)
        # header
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, 17)
        (block, datalen) = Block.from_header(bs)
        v3('Block length: %d' % datalen)
        # consume data
        (i_next, bs) = self.pd.read_bytes(pulses, i_next, datalen)
        (i_next, checksum) = self.pd.read_byte(pulses, i_next)
        (i_next, end_magic) = self.pd.read_byte(pulses, i_next)
        block.setdata(bs, checksum, end_magic)
        # verify end of block
        return (i_next, block)

    # returns ( int, ( block, ) )
    def read_blocks(self, pulses, i_next):
        blocks = []
        block = None
        while block is None or not block.is_eof:
            #i_next = self.pd.next_space(pulses, i_next, 8)
            ## i_next = i_next - 8
            ## i_next = i_next - 1
            v4('Spaces detected at %d - %fs' % (i_next, pulses[i_next][0]))
            (i_next, block) = self.read_block(pulses, i_next)
            blocks.append(block)
        return (i_next, blocks)

    # read a file
    # returns ( int, ( block, ) )
    def read_file(self, pulses, i_next):
        return self.read_blocks(pulses, i_next)

def read_block_bytestream(stream):
    ''' Read bytes from `stream`, parse them as MB-6885 blocks
        and return a sequence of the block objects.
    '''
    blocks = []
    return tuple(blocks)

def blocks_from_bin(stream, loadaddr=0x0000, filename=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as data to be loaded
        as it would be saved on an MB-6885. `loadaddr` is the load
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
        start_bits=(0,)
        stop_bits=(1,1)
        self.encoder = Encoder(2400, 16, 1200, 8, False, True, (0,), (1,1,))

    def leader(self):
        return self.encoder.encode_bytes( (0xff,) * 63 )
        #return self.encoder.encode_bytes( (0xff,) * 64 )
        #return self.encoder.encode_bytes( (0xff,) * 65 )

    def encode_block(self, blk):
        res = self.leader()
        res += self.encoder.encode_bytes(blk.to_bytes())
        return (silence(1.0), sound(res))

    def encode_blocks(self, blocks):
        res = ()
        for b in blocks:
            res += self.encode_block(b)
        return res

    def encode_file(self, blocks):
        return self.encode_blocks(blocks)


def write_file_bytestream(blocks, stream):
    bs = bytes(chain(*( b.filedata for b in blocks[:-1])))
    stream.write(bs)

def parameters():
    return {
        'edge_gradient_factor' : 0.65
    }

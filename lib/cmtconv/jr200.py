''' Library to read/write National JR-200 tape format.
'''

from __future__ import print_function
import sys
from collections import namedtuple
from enum import Enum
from testmc.memimage import MemImage
import itertools

# General approach is to use layered abstractions in
# a simple top-down parser.
# - came out of investigative approach, supports easy debugging
# - not the most efficient
#
# Layers are as follows:
# - waveform -> timed rising/falling edges
# - edges -> mark/space cycles
# - mark/space patterns -> bits
# - bits -> bytes
# - bytes -> file header, blocks


# TODO
#
# take out former code to plot histogram of cycle lengths
#   - useful for investigating other formats
# base cutoff on mean and stddev, instead of/in addition to max/min
# make cutoff a parameter & command line option (?)
# gracefully deal with end of samples and try to read multiple files
#
# Generate cjr file from header and blocks
# Documentation
#

def err(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def info(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def debug(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# samples   : [ float ]
# ->
# levels    : ( bool, )
def samples_to_levels(samples):
    if len(samples) > 0:
        sample_max = max(samples)
        sample_min = min(samples)
        cutoff = sample_min + 0.45 * (sample_max - sample_min)
        debug('Max: %d, min: %d, cutoff: %d' %
              (sample_max, sample_min, cutoff))
        return tuple(x > cutoff for x in samples)
    else:
        return ()

# levels        : ( bool, )
# sample_dur    : float
# ->
# edges         : ( ( float, bool, float ), )
#
# The edges returned are a triple of:
# - time
# - rising/falling - rising = True, falling = False
# - pulse length - length of the pulse up to this point
def levels_to_timed_edges(levels, sample_dur):
    edges = []
    if len(levels) > 0:
        last_t = 0.0
        last_level = levels[0]
        for (i, l) in enumerate(levels):
            t = sample_dur * i
            if l != last_level:
                edges.append((t, l, t - last_t))
                last_t = t
                last_level = l
    return tuple(edges)

# edges         : ( ( float, bool, float ), )
# i_next        : int
# edges_needed  : int
# ->
# i_next        : int
def next_space(edges, i_next, edges_needed):
    consecutive = 0
    i = i_next
    while i < len(edges):
        dur = 1000000 * edges[i][2]
        if dur >= 300 and dur <= 500:
            consecutive += 1
            if consecutive >= edges_needed:
                # FIXME: below is hack to get some troublesome audio to  work
                # shoud split functionality into 'next_space' and 'read_leader'
                #return i - consecutive
                return i
        else:
            consecutive = 0
        i += 1
    raise Exception('unable to find %d consecutive edges of space'
                    % edges_needed)

# edge      : ( ( float, bool, float ), )
# ->
# result    : bool
#
# FIXME: in-band error handling
# FIXME: tolerance argument(s)
def is_mark(edge):
    dur = 1000000 * edge[2]
    if dur > 150 and dur < 300:
        return 1
    #elif dur > 300 and dur < 500:
    # FIXME: hack to deal with weird pulses at end of block
    elif dur > 300 and dur < 900:
        return 0
    else:
        raise Exception('wavelength out of range: %f (at %f)'
                        % (dur, edge[0]))


# edges         : ( ( float, bool, float ), )
# i_next        : int
# ->
# i_next        : int
def eat_until_mark(edges, i_next):
    i = i_next
    edge = edges[i]
    while not is_mark(edge):
        i += 1
        edge = edges[i]
    return (i, i - i_next)


# FIXME: below is parameterised over mark/space definition above
#  (i.e. 2400Hz/1200Hz waves)
class Decoder(object):

    # mark_edges    : int -- number of 2400Hz edges for a mark or '1'
    # space_edges   : int -- number of 1200Hz edges for a space or '0'
    def __init__(self, mark_edges, space_edges):
        self.mark_edges     = mark_edges
        self.space_edges    = space_edges

    # edges     : ( ( float, bool, float ), )
    # idx       : int
    # ->
    # ( i_next, bit )   : ( int, int )
    def eat_bit(self, edges, idx):
        e = edges[idx]
        if is_mark(e):
            for i in range(self.mark_edges):
                e = edges[idx + i]
                if not is_mark(e):
                    dur = 1000000 * e[2]
                    raise Exception('Expected %d mark edges: %f (at %f) ' %
                                    (self.mark_edges, dur, e[0]))
            return (idx + self.mark_edges, 1)
        else:
            for i in range(self.space_edges):
                e = edges[idx + i]
                if is_mark(e):
                    dur = 1000000 * e[2]
                    raise Exception('Expected %d space edges: %f (at %f) ' %
                                    (self.space_edges, dur, e[0]))
            return (idx + self.space_edges, 0)

    # edges     : ( ( float, bool, float ), )
    # idx       : int
    # n         : int
    # ->
    # ( i_next, bits )   : ( int, ( int, ) )
    def eat_bits(self, edges, idx, n):
        bits = []
        i_next = idx
        for _ in range(n):
            (i_next, bit) = self.eat_bit(edges, i_next)
            bits.append(bit)
        return (i_next, tuple(bits))

    # Bit pattern for a byte is 1 xxxx xxxx 000

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def eat_start_bits(self, edges, i_next):
        (i_next, bits) = self.eat_bits(edges, i_next, 1)
        #debug(bits)
        if bits == (1,):
            return i_next
        else:
            raise Exception('Expected start bits: ( 1, ), got: %s ' %
                            str(bits))

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def eat_stop_bits(self, edges, i_next):
        (i_next, bits) = self.eat_bits(edges, i_next, 3)
        #debug(bits)
        if bits == (0, 0, 0):
            return i_next
        else:
            raise Exception('Expected stop bits ( 0, 0, 0 ), got: %s ' %
                            str(bits))

    # We use the definition of mark/1 and space/0 as per the service manual,
    # but the actual bits seem to be inverted. They are also little-endian,
    # with the LSB first.
    #
    # edges     : ( ( float, bool, float ), )
    # i_nexy    : int
    # ->
    # ( i_next, res ) : ( int, int )
    def eat_raw_byte(self, edges, i_next):
        (i_next, bits) = self.eat_bits(edges, i_next, 8)
        # debug(bits)
        res = 0
        for b in reversed(bits):
            res = 2 * res + (1 - b)
        return (i_next, res)

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # n         : int
    # ->
    # ( i_next, res ) : ( int, ( int, ) )
    def eat_bytes(self, edges, i_next, n):
        res = []
        for _ in range(n):
            i_next = self.eat_start_bits(edges, i_next)
            (i_next, x) = self.eat_raw_byte(edges, i_next)
            i_next = self.eat_stop_bits(edges, i_next)
            res.append(x)
        return (i_next, tuple(res))

class FileType(Enum):
    '''File type as it appears in the file header'''
    BASIC   = 0
    BINARY  = 1

class BaudRate(Enum):
    '''Baud rate as it appears in the file header'''
    BAUD_2400   = 0
    BAUD_600    = 1

class FileHeader(object):
    '''This represents the 33 byte file header.

    Format is as below:
    0-1: signature/header - should be 2, 42
    2: block number
    3: length: 26
    4-5: pad: 255
    6-21: file name
    22: BASIC(0)/Binary(1)
    23: Baud rate 2400 - 0, 600 - 1
    24-31: pad: 255
    32: checksum
    '''

    def __init__(self, header, block_number, length, pad0, filename, filetype,
                 baud_rate, pad1, checksum, raw_bytes):
        '''Caller is responsible for ensuring interpreted values match bytes'''
        self.header         = header
        self.block_number   = block_number
        self.length         = length
        self.pad0           = pad0
        self.filename       = filename
        self.filetype       = filetype
        self.baud_rate      = baud_rate
        self.pad1           = pad1
        self.checksum       = checksum
        self.raw_bytes      = raw_bytes

    @staticmethod
    def from_bytes(raw_bytes):
        '''Construct a block header from bytes'''
        b = raw_bytes
        return FileHeader(
            (b[0], b[1]),
            b[2],
            b[3],
            (b[4], b[5]),
            ''.join(chr(x) for x in b[6:22] if x > 0),
            FileType(b[22]),
            BaudRate(b[23]),
            tuple(b[24:32]),
            b[32],
            b)

    @staticmethod
    def make(file_name, file_type, baud_rate):
        '''Construct a block header for given args'''
        if len(file_name) > 16:
            raise ValueError('file name too long (16 characters max): "{}"' %
                             file_name)
        header          = (2, 42)
        block_number    = 0
        length          = 26
        pad0            = (0xff,) * 2
        pad1            = (0xff,) * 8
        filetype        = 0 if file_type == FileType.BASIC else 1
        baudrate        = 0 if baud_rate == BaudRate.BAUD_2400 else 1

        raw_bytes = bytearray()
        raw_bytes.extend(header)
        raw_bytes.append(block_number)
        raw_bytes.append(26)
        raw_bytes.extend(pad0)
        raw_bytes.extend(ord(x) for x in file_name)
        raw_bytes.extend((0x00,) * (16-len(file_name)))
        raw_bytes.append(filetype)
        raw_bytes.append(baudrate)
        raw_bytes.extend(pad1)
        chksum = sum(raw_bytes) % 256
        raw_bytes.append(chksum)

        return FileHeader(
            header,
            block_number,
            length,
            pad0,
            file_name,
            file_type,
            baud_rate,
            pad1,
            chksum,
            raw_bytes
        )

    def __str__(self):
        s = ''
        s += 'JR-200 File header block\n'
        s += 'Header: {}\n'.format(tuple(hex(x) for x in self.header))
        s += 'Block: {}\n'.format(self.block_number)
        s += 'Length: {}\n'.format(self.length)
        s += 'Pad0: {}\n'.format(tuple(hex(x) for x in  self.pad0))
        s += 'Filename: "{}"\n'.format(self.filename)
        s += 'File type: {}\n'.format(self.filetype)
        s += 'Baud rate: {}\n'.format(self.baud_rate)
        s += 'Pad1: {}\n'.format(tuple(hex(x) for x in self.pad1))
        s += 'Checksum: {} (calculated: {})\n'.format(
            hex(self.checksum), hex(sum(self.raw_bytes[:-1]) % 256))
        return s

    # FIXME: add proper checksum calc to allow checking


class BlockHeader(object):
    '''Interprets the block header'''

    def __init__(self, header, block_number, length, addr, raw_bytes):
        '''Caller is responsible for ensuring bytes match interpretation'''
        self.header         = header
        self.block_number   = block_number
        self.length         = length
        self.addr           = addr
        self.raw_bytes      = raw_bytes

    @staticmethod
    def from_bytes(raw_bytes):
        '''Construct the block header from raw bytes'''
        b = raw_bytes
        header = (b[0], b[1])
        if header != (2, 42):
            raise ValueError('Invalid signature in header: {}'.format(header))

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

File = namedtuple('File', 'header blocks')

class FileReader(object):
    def __init__(self):
        self.baud600_decoder = Decoder(8, 4)
        self.baud2400_decoder = Decoder(2, 1)

    # Read a number of space edges up to the mark for the start-bit of the
    # first byte
    def read_leader(self, edges, i_next):
        i_next = next_space(edges, i_next, 100)
        debug('Leader cycles detected at %d - %fs (%s)' %
              (i_next, edges[i_next][0], str(edges[i_next][1])))

        # Read up to the start bit of the first byte
        (i_next, _) = eat_until_mark(edges, i_next)
        debug('Start of data at %d - %fs (%s)' %
              (i_next, edges[i_next][0], edges[i_next][1]))

        return i_next

    def read_file_header(self, edges, i_next):
        i_next = self.read_leader(edges, i_next)

        (i_next, header_bytes) = self.baud600_decoder.eat_bytes(
            edges, i_next, 33)
        #debug(header_bytes)
        hdr = FileHeader.from_bytes(header_bytes)
        debug(hdr)

        debug('i_next: %d( %f )' % (i_next, edges[i_next][0]))
        return (i_next, hdr)

    def read_block(self, bit_decoder, edges, i_next):
        # # Read the leader
        i_next = self.read_leader(edges, i_next)

        # Read the block header
        (i_next, block_header_bytes) = bit_decoder.eat_bytes(edges, i_next, 6)
        block_hdr = BlockHeader.from_bytes(block_header_bytes)
        #debug(block_hdr)
        if block_hdr.is_tail():
            return (i_next, Block(block_hdr, [], 0))
        else:
            # Read the data
            actual_length = block_hdr.length if block_hdr.length > 0 else 256
            (i_next, block_data_bytes) = bit_decoder.eat_bytes(
                edges, i_next, actual_length + 1)
            block_data_chksum = block_data_bytes[-1]
            block_data_bytes = block_data_bytes[:-1]

            blk = Block(block_hdr, block_data_bytes, block_data_chksum)
            # debug(blk)
            debug('i_next: %d( %f )' % (i_next, edges[i_next][0]))
            return (i_next, blk)

    # read blocks
    # returns ( int, ( block, ) )
    def read_blocks(self, bit_decoder, edges, i_next):
        blocks = []

        while True:
            (i_next, blk) = self.read_block(bit_decoder, edges, i_next)
            blocks.append(blk)
            debug(blk)
            if blk.header.is_tail():
                break

        return (i_next, tuple(blocks))

    # read a file header and all blocks
    # returns ( int, File )
    def read_file(self, edges, i_next):
        (i_next, file_hdr) = self.read_file_header(edges, i_next)
        if file_hdr.baud_rate == BaudRate.BAUD_2400:
            bit_decoder = self.baud2400_decoder
        else:
            bit_decoder = self.baud600_decoder
        (i_next, blocks) = self.read_blocks(bit_decoder, edges, i_next)
        return (i_next, File(file_hdr, blocks))

    # FIXME: read_files - return ( File, )


# Check checksums are valid
#
# blocks : ( block, )
# ->
# bool
def checksums_valid(blocks):
    for block in blocks:
        chksum = block.calc_checksum()
        if block.checksum != chksum:
            err('Block %d has checksum %d, calculated checksum is %d'
                % (block.header.block_number, block.checksum, chksum))
            return False
    return True


# Convert blocks to bytes
#
# blocks : ( block, )
# ->
# bytearray
def blocks_to_bytes(blocks):
    res = bytearray()
    for block in blocks:
        res.extend(block.data)
    return res


# Convert bytes to a file
#
# filename  : str
# data      : bytearray
# addr      : int
# filetype  : int
# baud      : int
# ->
# File
def bytes_to_file(filename, data, addr, filetype, baud):
    '''Convert file info and bytes to File object'''
    file_header = FileHeader.make(filename, filetype, baud)
    blocks = []
    idx = 0
    a = addr
    bn = 1
    remaining = len(data)
    while remaining > 0:
        block_size = min(256, remaining)
        block_data = data[idx:idx + block_size]
        bh = BlockHeader.make(bn, block_size, a)
        chksum = (sum(block_data) + bh.calc_checksum()) % 256
        blocks.append(Block(bh, block_data, chksum))
        idx += block_size
        a += block_size
        bn += 1
        remaining -= block_size
    #blocks.append(Block(BlockHeader.make_tail(), tuple(), 0))
    blocks.append(Block(BlockHeader.make(255, 255, a), (), 0))
    return File(file_header, tuple(blocks))

# Convert a 'cjr' file to a file header and blocks
#
# bytes : bytearray
# ->
# File
def cjr_to_file(bytes):
    file_hdr = FileHeader.from_bytes(bytes[0:33])
    debug(file_hdr)
    blocks = []
    i = 33
    while True:
        data = bytes[i:i+6]
        debug('Header raw data: {}'.format(tuple(data)))
        block_hdr = BlockHeader.from_bytes(bytes[i:i+6])
        debug(block_hdr)
        if block_hdr.is_tail():
            blk = Block(block_hdr, (), 0)
            blocks.append(blk)
            break
        else:
            i += 6
            l = block_hdr.length
            if l == 0:
                l = 256 # FIXME: push into class
            block_bytes = bytes[i:i + l]
            i += l
            checksum = bytes[i]
            i += 1
            blk = Block(block_hdr, block_bytes, checksum)
            blocks.append(blk)
    return File(file_hdr, tuple(blocks))


# Convert a file to a cjr format
#
# f : File
# ->
# bytes : bytearray
def file_to_cjr(f):
    (file_hdr, blocks) = f
    res = bytearray()
    res.extend(file_hdr.raw_bytes)
    for blk in blocks:
        res.extend(blk.header.raw_bytes)
        if not blk.header.is_tail():
            res.extend(blk.data)
            res.append(blk.checksum)
    return res


# Encoder class
class Encoder(object):
    # mark_edges    : Int -- number of 2400Hz edges for a mark or '1'
    # space_edges   : Int -- number of 1200Hz edges for a space or '0'
    def __init__(self, mark_edges, space_edges):
        self.mark_edges     = mark_edges
        self.space_edges    = space_edges

    # bit
    def encode_bit(self, bit):
        # FIXME: push into init
        res = []
        if bit:
            for _ in range(self.mark_edges):
                res.append(0.5 / 2400.0)
        else:
            for _ in range(self.space_edges):
                res.append(0.5 / 1200.0)
        return res

    # byte
    def encode_byte(self, b):
        mark  = self.encode_bit(1) # FIXME: push into init
        space = self.encode_bit(0)
        res = []
        # Start bit
        res.extend(mark)
        #debug( hex( b ) )
        for _ in range(8):
            #debug( '{0:b}'.format( b ) )
            if b & 1:
                res.extend(space)
            else:
                res.extend(mark)
            b >>= 1
        # Stop bits
        res.extend(space)
        res.extend(space)
        res.extend(space)
        return res

    # bytes
    def encode_bytes(self, bytes):
        res = []
        for b in bytes:
            res.extend(self.encode_byte(b))
        return res


class AudioMarker(Enum):
    SILENCE = 1
    SOUND   = 2

def silence(dur):
    return (AudioMarker.SILENCE, dur)

def sound(edges):
    return (AudioMarker.SOUND, edges)


class FileEncoder(object):
    def __init__(self):
        self.baud600_encoder    = Encoder(8, 4)
        self.baud2400_encoder   = Encoder(2, 1)

    def leader(self, n):
        return [0.5 / 1200.0] * n

    def header(self, file_hdr):
        # silence, leader, header
        #leader_edges = self.leader(3200) # According to web docs
        #leader_edges = self.leader(2400) # Measured from actual recording
        leader_edges = self.leader(1600) # Shorter leader works OK
        debug(' '.join(hex(x) for x in file_hdr.raw_bytes))
        header_edges = self.baud600_encoder.encode_bytes(file_hdr.raw_bytes)
        return (silence(1.0), sound(leader_edges + header_edges))

    def block(self, encoder, blk):
        # silence, leader, header, data
        leader_edges = self.leader(200) # measured from actual recording
        if blk.header.is_tail():
            data = blk.header.raw_bytes
        if not blk.header.is_tail():
            data = blk.header.raw_bytes + blk.data + bytearray((blk.checksum,))
        debug(len(data))
        debug(' '.join(hex(x) for x in data))
        data_edges = encoder.encode_bytes(data)
        return (sound(leader_edges + data_edges),)

    def blocks(self, encoder, blocks):
        edges = ()
        for blk in blocks:
            edges += self.block(encoder, blk)
        return edges

    def encode_file(self, f):
        if f.header.baud_rate == BaudRate.BAUD_2400:
            encoder = self.baud2400_encoder
        elif f.header.baud_rate == BaudRate.BAUD_600:
            encoder = self.baud600_encoder
        else:
            raise Exception('Unsupported baud setting: %d' %
                            f.header.baud_rate)
        return self.header(f.header) + self.blocks(encoder, f.blocks)


# Convert edges to samples
#
# edges     : tuple of (SILENCE, duration) or (SOUND, edges)
# dur       : float
# silence   : float
# low       : float
# high      : float
# ->
# samples   : tuple( float )
def edges_to_samples(chunks, sample_dur, silence, low, high):
    res = []
    lvl = True
    for chunk in chunks:
        if chunk[0] == AudioMarker.SILENCE:
            dur = chunk[1]
            res.extend(silence for _ in range(int(dur/sample_dur)))
            lvl = True
        elif chunk[0] == AudioMarker.SOUND:
            edges = chunk[1]
            for dur in itertools.chain(edges, (0.01,)):
                sample_lvl = high if lvl else low
                res.extend(sample_lvl for _ in range(int(dur/sample_dur)))
                lvl = not lvl
        else:
            raise Exception('Unknown audio marker')
    return res


# Convert file to samples
#
# f     : File
# rate  : double
# ->
# ( double, )
def file_to_samples(f, rate):
    raise NotImplementedError

# Convert MemImage to blocks
#
# mi    : MemImage
# fname : filename
#

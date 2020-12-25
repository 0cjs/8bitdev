''' Library to read/write National JR-200 tape format.
'''

from __future__ import print_function
import sys
from collections import namedtuple
from enum import Enum
from testmc.memimage import MemImage
import itertools

from    cmtconv.data  import Block, FileHeader

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
            edges, i_next, FileHeader.blocklen)
        #debug(header_bytes)
        hdr = FileHeader.from_bytes(header_bytes)
        debug(hdr)

        debug('i_next: %d( %f )' % (i_next, edges[i_next][0]))
        return (i_next, hdr)

    def read_block(self, bit_decoder, edges, i_next):
        i_next = self.read_leader(edges, i_next)
        (i_next, header) = bit_decoder.eat_bytes(edges, i_next, Block.headerlen)
        #   XXX bit_decoder.eat_bytes is no longer returning a `bytes`!
        #   instead it's a tuple of ints.
        header = bytes(header)
        (block, datalen) = Block.from_header(header)
        (i_next, body) = bit_decoder.eat_bytes(edges, i_next, datalen + 1)
        #   XXX bit_decoder.eat_bytes is no longer returning a `bytes`!
        #   instead it's a tuple of ints.
        body = bytes(body)
        block.setdata(body[:-1], body[-1])
        #debug(block)
        if not block.is_eof:
            #   The read for a tail block gives IndexError below.
            debug('i_next: %d( %f )' % (i_next, edges[i_next][0]))
        return (i_next, block)

    # read blocks
    # returns ( int, ( block, ) )
    def read_blocks(self, bit_decoder, edges, i_next):
        blocks = []
        while True:
            (i_next, blk) = self.read_block(bit_decoder, edges, i_next)
            blocks.append(blk)
            debug(blk)
            if blk.is_eof:
                break
        return (i_next, tuple(blocks))

    # read a file header and all blocks
    # returns ( int, File )
    def read_file(self, edges, i_next):
        (i_next, file_hdr) = self.read_file_header(edges, i_next)
        if file_hdr.baudrate == file_hdr.B_2400:
            bit_decoder = self.baud2400_decoder
        else:
            bit_decoder = self.baud600_decoder
        (i_next, blocks) = self.read_blocks(bit_decoder, edges, i_next)
        return (i_next, File(file_hdr, blocks))

    # FIXME: read_files - return ( File, )

# Convert blocks to bytes
#
# blocks : ( block, )
# ->
# bytearray
def blocks_to_bytes(blocks):
    res = bytearray()
    for block in blocks:
        res.extend(block.filedata)
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
    file_header = FileHeader.make_block(filename, filetype, baud)
    blocks = []
    idx = 0
    a = addr
    bn = 1
    remaining = len(data)
    while remaining > 0:
        block_size = min(256, remaining)
        block_data = data[idx:idx + block_size]
        blocks.append(Block.make_block(bn, a, block_data))
        idx += block_size
        a += block_size
        bn += 1
        remaining -= block_size
    blocks.append(Block.make_eof_block(a))
    return File(file_header, tuple(blocks))

# Convert a 'cjr' file to a file header and blocks
#
# bytes : bytearray
# ->
# File
def cjr_to_file(bstream):
    fhlen = FileHeader.blocklen
    file_hdr = FileHeader.from_bytes(bstream[0:fhlen])
    debug(file_hdr)
    blocks = []
    bstream = bstream[fhlen:]
    hdrlen = Block.headerlen
    while True:
        block, datalen = Block.from_header(bstream[:hdrlen])
        checksum = hdrlen + datalen
        block.setdata(bstream[hdrlen:checksum], bstream[checksum])
        blocks.append(block)
        bstream = bstream[checksum+1:]
        if block.is_eof:
            break
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
        if not blk.is_eof:
            res.extend(blk.filedata)
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
        debug(' '.join(hex(x) for x in file_hdr.to_bytes()))
        header_edges = self.baud600_encoder.encode_bytes(file_hdr.to_bytes())
        return (silence(1.0), sound(leader_edges + header_edges))

    def block(self, encoder, blk):
        # silence, leader, header, data
        leader_edges = self.leader(200) # measured from actual recording
        data = blk.to_bytes()
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
        fh = f.header
        if    fh.baudrate == fh.B_2400:  encoder = self.baud2400_encoder
        elif  fh.baudrate == fh.B_600:   encoder = self.baud600_encoder
        else: raise RuntimeError('Unknown baudrate: {!r}'.format(fh.baudrate))
        return self.header(fh) + self.blocks(encoder, f.blocks)


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

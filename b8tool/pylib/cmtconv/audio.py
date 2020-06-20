''' Library to read/write National JR-200 tape format.
'''

from    enum  import Enum
from    itertools  import chain
from    collections  import namedtuple
from    enum  import IntEnum
import  math

from    testmc.memimage  import MemImage
from    cmtconv.logging  import *

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


# samples   : [ float ]
# ->
# edges         : ( ( float, bool, float ), )
# FIXME: parameterise the cutoff
def samples_to_timed_edges(samples, sample_dur):
    edges = []
    if len(samples) > 0:
        sample_max = max(samples)
        sample_min = min(samples)
        cutoff = sample_min + 0.6 * (sample_max - sample_min)
        v3('Max: %d, min: %d, cutoff: %d' % (sample_max, sample_min, cutoff))
        last_t = 0.0
        last_level = samples[0] > cutoff
        i = 0
        for s in samples:
            l = s > cutoff
            if l != last_level:
                t = sample_dur * i
                edges.append((t, l, t - last_t))
                last_t = t
                last_level = l
            i = i + 1
    return tuple(edges)


# samples   : [ float ]
# ->
# levels    : ( bool, )
def samples_to_levels(samples):
    if len(samples) > 0:
        sample_max = max(samples)
        sample_min = min(samples)
        cutoff = sample_min + 0.45 * (sample_max - sample_min)
        v3('Max: %d, min: %d, cutoff: %d' % (sample_max, sample_min, cutoff))
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
            if l != last_level:
                t = sample_dur * i
                edges.append((t, l, t - last_t))
                last_t = t
                last_level = l
    return tuple(edges)

# Classify edges into mark/space/other pulses

PulseOther = namedtuple('PulseOther', 'width')
PulseOther.__docs__ = \
    '''A pulse of an unrecognised width'''

class Pulse(IntEnum): PULSE_SPACE = 0; PULSE_MARK = 1
PULSE_SPACE = Pulse.PULSE_SPACE
PULSE_MARK  = Pulse.PULSE_MARK


# Rename: MarkSpace decoder, or just fold in with decoder?
# 2 levels of decoder
# base maps edges to mark/space pulses and knows baud rates of mark and space
# also knows how many pulses represent mark and space, and maps these to 0/1
# upper level knows about start/stop bits
# Can then model JR-200 flipping of mark/space at this lower level, instead
# of having logic at the upper level
#
# For dealing with dodgy pulse widths, could
#
# 1) have patterns to match, e.g. M,M,M,M,M,M,M,X
# 2) Specify that only the first n have to match
#       e.g. 8 pulses of mark, but only check first 4
# 3) Sub-class this and override expect_stop_bits as necessary
#
#
class PulseDecoder:
    __docs__ = \
        ''' A class to decode pulses into mark and space
            pulses, given the baud rate of each,
            and into mark and space symbols, given the number of pulses
            of each.
            '''
    def __init__(self, mark_baud, mark_pulses, space_baud, space_pulses,
        invert_sense, lsb_first, start_bits, stop_bits,
        mark_tol = (0.2, 0.3), space_tol = (0.25, 2.0)):

        self.mark_baud      = mark_baud
        self.mark_pulses    = mark_pulses
        self.space_baud     = space_baud
        self.space_pulses   = space_pulses
        self.invert_sense   = invert_sense
        self.lsb_first      = lsb_first
        self.start_bits     = start_bits
        self.stop_bits      = stop_bits

        mark_width = 0.5 / mark_baud
        self.mark_lower = (1.0 + math.log(1.0 - mark_tol[0])) * mark_width
        self.mark_upper = (1.0 + math.log(1.0 + mark_tol[1])) * mark_width

        space_width = 0.5 / space_baud
        self.space_lower = (1.0 + math.log(1.0 - space_tol[0])) * space_width
        self.space_upper = (1.0 + math.log(1.0 + space_tol[1])) * space_width

        # mask sequence
        if lsb_first:
            self.mask_sequence = ( 1, 2, 4, 8, 16, 32, 64, 128 )
        else:
            self.mask_sequence = ( 128, 64, 32, 16, 8, 4, 2, 1 )



    # edge      : ( float, bool, float )
    # ->
    # result    : PULSE_MARK, PULSE_SPACE or PulseOther( width )
    #
    def classify_edge(self, edge):
        dur = edge[2]
        if dur >= self.mark_lower and dur <= self.mark_upper:
            return PULSE_MARK
        elif dur >= self.space_lower and dur <= self.space_upper:
            return PULSE_SPACE
        else:
            return PulseOther(dur)

    # edges         : ( ( float, bool, float ), )
    # i_next        : int
    # edges_needed  : int
    # ->
    # i_next        : int
    def next_space(self, edges, i_next, edges_needed):
        consecutive = 0
        i = i_next
        while i < len(edges):
            dur = edges[i][2]
            if dur >= self.space_lower and dur <= self.space_upper:
                consecutive += 1
                if consecutive >= edges_needed:
                    return i - (consecutive - 1)
            else:
                consecutive = 0
            i += 1
        raise Exception('unable to find %d consecutive edges of space'
                        % edges_needed)


    # edges         : ( ( float, bool, float ), )
    # i_next        : int
    # ->
    # i_next        : ( int, int )
    def next_mark(self, edges, i_next):
        i = i_next
        while self.classify_edge(edges[i]) != PULSE_MARK:
            i += 1
        return (i, i - i_next)


    #
    # Expect marks
    #
    # Biased towrards marks - we accept a wider range of pulse widths
    def expect_marks(self, edges, i_next, n):
        for i in range(0, n):
            idx = i_next + i
            dur = edges[idx][2]
            if dur < self.mark_lower * .75 or dur > self.mark_upper * 1.5:
                raise Exception('Expected %d mark pulses at %d (%f)'
                    ', failed on pulse %d with pulse width %f'
                    ', edges = %s'
                        % (n, i_next, edges[i_next][0], i, dur,
                            repr(edges[i_next:i_next + n])))
        return i_next + n
    #
    # Expect spaces
    #
    # Biased towrards spaces - we accept a wider range of pulse widths
    def expect_spaces(self, edges, i_next, n):
        for i in range(0, n):
            idx = i_next + i
            dur = edges[idx][2]
            if dur < self.space_lower * .75 or dur > self.space_upper * 1.35:
                raise Exception('Expected %d space pulses at %d (%f)'
                    ', failed on pulse %d with pulse width %f'
                    ', edges = %s'
                        % (n, i_next, edges[i_next][0], i, dur,
                            repr(edges[i_next:i_next + n])))
        return i_next + n

    # read one bit represented by a mark/space symbol
    #
    # throws if sequence of pulses is not a mark or space symbol
    #
    # edges     : ( ( float, bool, float ), )
    # idx       : int
    # ->
    # ( i_next, bit )   : ( int, int )
    def read_bit(self, edges, idx):
        e = edges[idx]
        p = self.classify_edge(e)
        #v4('read_bit, first: %s' % p)  # XXX very slow
        if p == PULSE_MARK:
            return (self.expect_marks(edges, idx, self.mark_pulses), 1)
        elif p == PULSE_SPACE:
            return (self.expect_spaces(edges, idx, self.space_pulses), 0)
        else:
            raise Exception('Unexpected pulse width at: %f, '
                'with pulse width: %f'
                % (edges[idx][0], edges[idx][2]))

    # edges     : ( ( float, bool, float ), )
    # idx       : int
    # n         : int
    # ->
    # ( i_next, bits )   : ( int, ( int, ) )
    def read_bits(self, edges, idx, n):
        bits = []
        i_next = idx
        for _ in range(n):
            (i_next, bit) = self.read_bit(edges, i_next)
            bits.append(bit)
        return (i_next, tuple(bits))

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def expect_start_bits(self, edges, i_next):
        (i_next, bits) = self.read_bits(edges, i_next, len(self.start_bits))
        #v4('expect_start_bits:', bits) # XXX very slow
        if bits == self.start_bits:
            return i_next
        else:
            raise Exception('Expected start bits: %s, got: %s ' %
                            (str(self.start_bits), str(bits)))

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def expect_stop_bits(self, edges, i_next):
        (i_next, bits) = self.read_bits(edges, i_next, len(self.stop_bits))
        #v4('expect_stop_bits:', bits)  # XXX very slow
        if bits == self.stop_bits:
            return i_next
        else:
            raise Exception('Expected stop bits: %s, got: %s ' %
                            (str(self.stop_bits), str(bits)))

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # ->
    # ( i_next, res ) : ( int, int )
    def read_raw_byte(self, edges, i_next):
        (i_next, bits) = self.read_bits(edges, i_next, 8)
        #v4('read_raw_byte:', bits) # XXX very slow
        res = 0
        if self.invert_sense:
            for i in range(8):
                res |= self.mask_sequence[i] if not bits[i] else 0
        else:
            for i in range(8):
                res |= self.mask_sequence[i] if bits[i] else 0
        return (i_next, res)

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # n         : int
    # ->
    # ( i_next, res ) : ( int, int )
    def read_byte(self, edges, i_next):
        i_next = self.expect_start_bits(edges, i_next)
        (i_next, res) = self.read_raw_byte(edges, i_next)
        i_next = self.expect_stop_bits(edges, i_next)
        return (i_next, res)

    # edges     : ( ( float, bool, float ), )
    # i_next    : int
    # n         : int
    # ->
    # ( i_next, res ) : ( int, bytearray )
    def read_bytes(self, edges, i_next, n):
        res = bytearray()
        for _ in range(n):
            i_next = self.expect_start_bits(edges, i_next)
            (i_next, x) = self.read_raw_byte(edges, i_next)
            i_next = self.expect_stop_bits(edges, i_next)
            res.append(x)
        return (i_next, res)

# Encoder class
class Encoder(object):
    # mark_baud     : int   -- mark baud rate
    # mark_edges    : int   -- number of edges for a mark or '1'
    # space_baud    : int   -- space baud rate
    # space_edges   : int   -- number of edges for a space or '0'
    # invert_sense  : bool  -- False -  1 = mark, 0 = space
    #                       -- True  -  0 = mark, 1 = space
    # lsb_first     : bool  -- stream bits LSB first (True) or last (False)
    # start_bits    : (int,)    -- start bits pattern
    # stop_bits     : (int,)    -- stop bit pattern
    def __init__(self, mark_baud, mark_edges, space_baud, space_edges,
        invert_sense, lsb_first, start_bits, stop_bits):
        self.mark_baud      = mark_baud
        self.mark_edges     = mark_edges
        self.space_baud     = space_baud
        self.space_edges    = space_edges
        self.invert_sense   = invert_sense
        self.lsb_first      = lsb_first
        self.start_bits     = start_bits
        self.stop_bits      = stop_bits

        # pre-compute mark/space patterns
        self.mark_pattern   = (0.5 / self.mark_baud,) * mark_edges
        self.space_pattern  = (0.5 / self.space_baud,) * space_edges

        # bit 0/1 -> mark/space patterns
        if invert_sense:
            self.ms_pattern = (self.mark_pattern, self.space_pattern)
        else:
            self.ms_pattern = (self.space_pattern, self.mark_pattern)

        # mask sequence
        if lsb_first:
            self.mask_sequence = ( 1, 2, 4, 8, 16, 32, 64, 128 )
        else:
            self.mask_sequence = ( 128, 64, 32, 16, 8, 4, 2, 1 )

        p = []
        for b in start_bits:
            p.extend(self.ms_pattern[b])
        self.start_pattern = tuple(p)

        p = []
        for b in stop_bits:
            p.extend(self.ms_pattern[b])
        self.stop_pattern = tuple(p)


    # bit
    # bit       : int           -- 1/0 => mark/space
    # result    : ( float , )   -- pattern
    def encode_bit(self, bit):
        return self.ms_pattern[bit]

    # FIXME: use a list of tuples or objects instead of a flat list
    # to avoid all these extends and allocations...
    #
    # byte
    #
    # b         : int       -- byte
    # result    : [ float ] -- pulse widths
    def encode_byte(self, b):
        res = []
        res.extend(self.start_pattern)
        for m in self.mask_sequence:
            res.extend(self.ms_pattern[0 if b & m == 0 else 1])
        res.extend(self.stop_pattern)
        return res

    # bytes
    def encode_bytes(self, bytes):
        res = []
        for b in bytes:
            res.extend(self.encode_byte(b))
        return res


# FIXME: fn to get FileEncoder and ByteEncoder for each platform

class AudioMarker(Enum):
    SILENCE = 1
    SOUND   = 2

def silence(dur):
    return (AudioMarker.SILENCE, dur)

def sound(edges):
    return (AudioMarker.SOUND, edges)


# Convert edges to samples
#
# chunks     : tuple of (SILENCE, duration) or (SOUND, edges)
# sample_dur : float
# silence    : int
# low        : int
# high       : int
# ->
# samples   : [ int ]
def edges_to_samples(chunks, sample_dur, silence, low, high):
    res = []
    lvl = True
    for chunk in chunks:
        if chunk[0] == AudioMarker.SILENCE:
            dur = chunk[1]
            res.extend([silence] * int(dur/sample_dur))
            lvl = True
        elif chunk[0] == AudioMarker.SOUND:
            edges = chunk[1]
            for dur in chain(edges, (0.01,)):
                sample_lvl = high if lvl else low
                res.extend([sample_lvl] * int(dur/sample_dur))
                lvl = not lvl
        else:
            raise Exception('Unknown audio marker')
    return res

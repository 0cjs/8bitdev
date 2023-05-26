''' Library to read/write Kansas City format tape audio
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
# - waveform -> timed pulses
# - pulses -> mark/space
# - mark/space patterns -> bits
# - bits -> bytes
# - bytes -> file header, blocks

def merge_mids(pulses, sample_dur):
    res = []
    i = 0
    # FIXME: Would be better to do this in terms of integer indices
    for (t, l, dur) in pulses:
        # Merge short periods of mid level with previous pulse
        if l == 0 and dur < 8 * sample_dur:
            pass
        else:
            res.append( (t, l, dur) )
    return res


def filter_clicks(pulses, sample_dur, tol = 4):
    res = []
    i = 0
    # FIXME: Would be better to do this in terms of integer indices
    for (t, l, dur) in pulses:
        if dur < tol * sample_dur:
            # FIXME: should maybe modify previous/next pulse
            pass
        else:
            res.append( (t, l, dur) )
    return res


#
# statistics.mean and statistics.stdev{p} are accureate but slow
# so we do a simple two-pass population stdev calc and combine with mean
#
def stats(samples):
    n=len(samples)
    if n == 0:
        return (None, None)
    elif n == 1:
        return (samples[0], None)
    else:
        mean = sum(samples)/n
        ss = sum( (x - mean) ** 2 for x in samples )
        return (mean, math.sqrt(ss / n))


# samples   : [ float ]
# ->
# pulses    : ( (float, int, float) )
#
def samples_to_pulses_via_edge_detection(samples, sample_dur, grad_factor=0.5):
    res=[]
    n = len(samples)
    if n > 1:
        v2("edge detection, starting stats calc...")

        #sample_mean = statistics.mean(samples)
        #sample_stdev = statistics.stdev(samples)
        (sample_mean, sample_stdev) = stats(samples)
        v2("edge detection: mean = {:5.3f}, stdev = {:5.3f}"
           .format(sample_mean, sample_stdev))

        # Note, working absolute values are as follows:
        # 10 for FM-7, JR-200, PC-8001
        # 32 for MB-6885
        grad=grad_factor * sample_stdev

        i=1
        prev=0
        lvl=0
        v2("edge detection: required gradient={:5.3f} ...".format(grad))
        while i<n:
            d = samples[i] - samples[i-1]
            if abs(d) < grad:
                i += 1
            else:
                i0=i
                # roll forward
                d0=d
                while abs(d) >= grad and math.copysign(d,d0) == d and i<n-1:
                    i += 1
                    d = samples[i] - samples[i-1]
                # mark mid point
                idx = int((i+i0)/2)
                t0=sample_dur*prev
                t1=sample_dur*idx
                # Use mid-point of pulse to get level
                mid = int((prev+idx)/2)
                if samples[mid] > sample_mean + 0.5 * sample_stdev:
                    lvl=1
                elif samples[mid] < sample_mean - 0.5 * sample_stdev:
                    lvl=-1
                else:
                    lvl=0
                res.append((t1,lvl,t1-t0))
                prev=idx
        # deal with final pulse
        mid = int((i+prev)/2)
        if samples[mid] > sample_mean + 0.5 * sample_stdev:
            lvl=1
        elif samples[mid] < sample_mean - 0.5 * sample_stdev:
            lvl=-1
        else:
            lvl=0
        t0=sample_dur*prev
        t1=sample_dur*n
        res.append((t1,lvl,t1-t0))
        v2("edge detection: done, found {} edges".format(len(res)))
        v2( "first pulses: {}" .format(list(res[:10])))
        v2( "last pulses: {}" .format(list(res[-10:])))
        return tuple(res)
    else:
        return tuple()



# samples   : [ float ]
# ->
# pulses     : ( (float, int, float) )
def samples_to_pulses(samples, sample_dur):
    pulses=[]
    if len(samples) > 0:
        sample_max = max(samples)
        sample_min = min(samples)
        high_cutoff = sample_min + 0.6 * (sample_max - sample_min)
        low_cutoff  = sample_min + 0.4 * (sample_max - sample_min)
        v3('Max: %d, min: %d, high cutoff: %d, low cutoff: %d'
            % (sample_max, sample_min, high_cutoff, low_cutoff))
        classify = lambda x: -1 if x <= low_cutoff else (1 if x >= high_cutoff else 0)

        last_t = 0.0
        last_level = classify(samples[0])
        i = 0
        for s in samples:
            l = classify(s)
            # FIXME: hangover from True/False rising edges
            if l != last_level:
                if last_level == 0:
                    l_ = 1 if l == 1 else -1
                else:
                    l_ = last_level
                t = sample_dur * i
                pulses.append((t, l_, t-last_t))
                last_t = t
                last_level = l
            i += 1
    return tuple(pulses)

# FIXME: remove
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

# FIXME: remove
# levels        : ( bool, )
# sample_dur    : float
# ->
# pulses        : ( ( float, bool, float ), )
#
# The pulses returned are a triple of:
# - time
# - level
# - pulse length - length of the pulse up to this point
def levels_to_pulses(levels, sample_dur):
    pulses = []
    if len(levels) > 0:
        last_t = 0.0
        last_level = levels[0]
        for (i, l) in enumerate(levels):
            if l != last_level:
                t = sample_dur * i
                pulses.append((t, l, t - last_t))
                last_t = t
                last_level = l
    return tuple(pulses)

# Classify pulses into mark/space/other pulses

PulseOther = namedtuple('PulseOther', 'width')
PulseOther.__docs__ = \
    '''A pulse of an unrecognised width'''

class Pulse(IntEnum): PULSE_SPACE = 0; PULSE_MARK = 1
PULSE_SPACE = Pulse.PULSE_SPACE
PULSE_MARK  = Pulse.PULSE_MARK


# Rename: MarkSpace decoder, or just fold in with decoder?
# 2 levels of decoder
# base maps pulses to mark/space and knows baud rates of mark and space
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



    # pulse     : ( float, int, float )
    # ->
    # result    : PULSE_MARK, PULSE_SPACE or PulseOther( width )
    #
    def classify_pulse(self, pulse):
        dur = pulse[2]
        if dur >= self.mark_lower and dur <= self.mark_upper:
            return PULSE_MARK
        elif dur >= self.space_lower and dur <= self.space_upper:
            return PULSE_SPACE
        else:
            return PulseOther(dur)

    # pulses        : ( ( float, int, float ), )
    # i_next        : int
    # needed        : int
    # ->
    # i_next        : int
    def next_space(self, pulses, i_next, needed):
        consecutive = 0
        i = i_next
        while i < len(pulses):
            dur = pulses[i][2]
            if dur >= self.space_lower and dur <= self.space_upper:
                consecutive += 1
                if consecutive >= needed:
                    return i - (consecutive - 1)
            else:
                consecutive = 0
            i += 1
        raise Exception('unable to find %d consecutive pulses of space'
                        % needed)

    # FIXME: add needed pulses as per next_space
    #
    # pulses        : ( ( float, int, float ), )
    # i_next        : int
    # ->
    # i_next        : ( int, int )
    def next_mark(self, pulses, i_next):
        i = i_next
        while self.classify_pulse(pulses[i]) != PULSE_MARK:
            i += 1
        return (i, i - i_next)


    #
    # Expect marks
    #
    # Biased towrards marks - we accept a wider range of pulse widths
    def expect_marks(self, pulses, i_next, n):
        for i in range(0, n):
            idx = i_next + i
            if idx >= len(pulses):
                raise Exception('Out of pulses at %d, on pulse %d of expected'
                    ' %d mark pulses'
                    % (idx, i, n))
            dur = pulses[idx][2]
            if dur < self.mark_lower * .75 or dur > self.mark_upper * 1.5:
                raise Exception('Expected %d mark pulses at %d (%f)'
                    ', failed on pulse %d with pulse width %f'
                    ', pulses = %s'
                        % (n, i_next, pulses[i_next][0], i, dur,
                            repr(pulses[i_next:i_next + n])))
        return i_next + n
    #
    # Expect spaces
    #
    # Biased towrards spaces - we accept a wider range of pulse widths
    def expect_spaces(self, pulses, i_next, n):
        for i in range(n):
            idx = i_next + i
            if idx >= len(pulses):
                raise Exception('Out of pulses at %d, on pulse %d of expected'
                    ' %d space pulses'
                    % (idx, i, n))
            dur = pulses[idx][2]
            if dur < self.space_lower * .75 or dur > self.space_upper * 1.35:
                raise Exception('Expected %d space pulses at %d (%f)'
                    ', failed on pulse %d with pulse width %f'
                    ', pulses = %s'
                        % (n, i_next, pulses[i_next][0], i, dur,
                            repr(pulses[i_next:i_next + n])))
        return i_next + n

    # read one bit represented by a mark/space symbol
    #
    # throws if sequence of pulses is not a mark or space symbol
    #
    # pulses    : ( ( float, pulse, float ), )
    # idx       : int
    # ->
    # ( i_next, bit )   : ( int, int )
    def read_bit(self, pulses, idx):
        i_next = idx
        e = pulses[i_next]
        p = self.classify_pulse(e)
        #v4( 'classify: {}, {}, {}, {}'.format(str(p), i_next, e[0], e[2]))
        #v4('read_bit, first: %s' % p)  # XXX very slow
        if p == PULSE_MARK:
            return (self.expect_marks(pulses, i_next, self.mark_pulses), 1)
        elif p == PULSE_SPACE:
            return (self.expect_spaces(pulses, i_next, self.space_pulses), 0)
        else:
            raise Exception('Unexpected pulse width at: %f, '
                'with pulse width: %f'
                % (pulses[i_next][0], pulses[i_next][2]))

    # pulses    : ( ( float, int, float ), )
    # idx       : int
    # n         : int
    # ->
    # ( i_next, bits )   : ( int, ( int, ) )
    def read_bits(self, pulses, idx, n):
        bits = []
        i_next = idx
        for _ in range(n):
            (i_next, bit) = self.read_bit(pulses, i_next)
            bits.append(bit)
        return (i_next, tuple(bits))

    # pulses    : ( ( float, int, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def expect_start_bits(self, pulses, i_next):
        (i_next, bits) = self.read_bits(pulses, i_next, len(self.start_bits))
        #v4('expect_start_bits:', bits) # XXX very slow
        if bits == self.start_bits:
            return i_next
        else:
            raise Exception('Expected start bits: %s, got: %s ' %
                            (str(self.start_bits), str(bits)))

    # pulses    : ( ( float, int, float ), )
    # i_next    : int
    # ->
    # i_next    : int
    def expect_stop_bits(self, pulses, i_next):
        (i_next, bits) = self.read_bits(pulses, i_next, len(self.stop_bits))
        #v4('expect_stop_bits:', bits)  # XXX very slow
        if bits == self.stop_bits:
            return i_next
        else:
            raise Exception('Expected stop bits: %s, got: %s ' %
                            (str(self.stop_bits), str(bits)))

    # pulses    : ( ( float, int, float ), )
    # i_next    : int
    # ->
    # ( i_next, res ) : ( int, int )
    def read_raw_byte(self, pulses, i_next):
        (i_next, bits) = self.read_bits(pulses, i_next, 8)
        #v4('read_raw_byte:', bits) # XXX very slow
        res = 0
        if self.invert_sense:
            for i in range(8):
                res |= self.mask_sequence[i] if not bits[i] else 0
        else:
            for i in range(8):
                res |= self.mask_sequence[i] if bits[i] else 0
        return (i_next, res)

    # pulses    : ( ( float, int, float ), )
    # i_next    : int
    # n         : int
    # ->
    # ( i_next, res ) : ( int, int )
    def read_byte(self, pulses, i_next):
        i_next = self.expect_start_bits(pulses, i_next)
        (i_next, res) = self.read_raw_byte(pulses, i_next)
        i_next = self.expect_stop_bits(pulses, i_next)
        return (i_next, res)

    # pulses    : ( ( float, int, float ), )
    # i_next    : int
    # n         : int
    # ->
    # ( i_next, res ) : ( int, bytearray )
    def read_bytes(self, pulses, i_next, n):
        res = bytearray()
        for _ in range(n):
            i_next = self.expect_start_bits(pulses, i_next)
            (i_next, x) = self.read_raw_byte(pulses, i_next)
            i_next = self.expect_stop_bits(pulses, i_next)
            res.append(x)
        return (i_next, res)

# Encoder class
class Encoder(object):
    # mark_baud     : int   -- mark baud rate
    # mark_pulses   : int   -- number of pulses for a mark or '1'
    # space_baud    : int   -- space baud rate
    # space_pulses  : int   -- number of pulses for a space or '0'
    # invert_sense  : bool  -- False -  1 = mark, 0 = space
    #                       -- True  -  0 = mark, 1 = space
    # lsb_first     : bool  -- stream bits LSB first (True) or last (False)
    # start_bits    : (int,)    -- start bits pattern
    # stop_bits     : (int,)    -- stop bit pattern
    def __init__(self, mark_baud, mark_pulses, space_baud, space_pulses,
        invert_sense, lsb_first, start_bits, stop_bits):
        self.mark_baud      = mark_baud
        self.mark_pulses    = mark_pulses
        self.space_baud     = space_baud
        self.space_pulses   = space_pulses
        self.invert_sense   = invert_sense
        self.lsb_first      = lsb_first
        self.start_bits     = start_bits
        self.stop_bits      = stop_bits

        # pre-compute mark/space patterns
        self.mark_pattern   = (0.5 / self.mark_baud,) * mark_pulses
        self.space_pattern  = (0.5 / self.space_baud,) * space_pulses

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

def sound(pulses):
    return (AudioMarker.SOUND, pulses)


# Convert pulses to samples
#
# chunks     : tuple of (SILENCE, duration) or (SOUND, pulse_widths)
# sample_dur : float
# silence    : int
# low        : int
# high       : int
# ->
# samples   : [ int ]
def pulses_to_samples(chunks, sample_dur, silence, low, high):
    # FIXME: Use HML levels, get rid of AudioMarker
    res = []
    lvl = True
    for chunk in chunks:
        if chunk[0] == AudioMarker.SILENCE:
            dur = chunk[1]
            res.extend([silence] * int(dur/sample_dur))
            lvl = True
        elif chunk[0] == AudioMarker.SOUND:
            pulses = chunk[1]
            for dur in pulses:
                sample_lvl = high if lvl else low
                res.extend([sample_lvl] * int(dur/sample_dur))
                lvl = not lvl
            # Below is a hack to force the end of a pulse
            # Calling code should be putting silence beween blocks of bytes
            # and we need to model levels as H/M/L insteasd of H/L
            res.append(silence)
        else:
            raise Exception('Unknown audio marker')
    return res


def pulses_to_samples2(chunks, sample_dur, low, mid, high):
    res = []
    lvl = 0
    for chunk in chunks:
        if chunk[0] == AudioMarker.SILENCE:
            dur = chunk[1]
            res.extend([mid] * int(0.5 + dur/sample_dur))
            lvl = 0
        elif chunk[0] == AudioMarker.SOUND:
            pulses = chunk[1]
            for d in pulses:
                if type(d) is tuple:
                    # tuple is width, level
                    w = d[0]
                    lvl_ = d[1]
                    lvl = lvl_
                    #v3('tuple: ({},{},{})'.format(w, lvl, lvl_))
                else:
                    w = d
                    lvl_ = 1 if lvl == 0 else -lvl
                    #v3('other: ({},{},{})'.format(w, lvl, lvl_))
                if lvl_==-1:
                    sample_lvl=low
                elif lvl_==1:
                    sample_lvl=high
                else:
                    sample_lvl=mid
                res.extend([sample_lvl] * int(0.5 + w/sample_dur))
                lvl=lvl_
            res.append(mid)
        else:
            raise Exception('Unknown audio marker')
    return res

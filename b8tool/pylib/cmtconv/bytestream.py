''' Generic bytestream operations.

    These are functions that deal with and convert between three
    different representations of files on microcomputer cassette
    tape stoarge systems:
    - _File bytestreams_ of the contents of files on tape.
    - _Block objects_ representing blocks on tape.
    - _Block bytestreams_ of the contents of blocks on tape.

    The API of the block modules and their classes is subject to change as
    we try to genericise it for different platforms.
'''

from    importlib  import  import_module
from    itertools  import chain
from    io  import BytesIO
import  wave

from    cmtconv.audio  import samples_to_pulses, pulses_to_samples, \
    filter_clicks, samples_to_pulses_via_edge_detection
from    cmtconv.logging  import *
from    testmc.tool  import asl

def get_block_module(platform):
    ''' Find, load and return the module containing the block classes for
        `platform`. Upper-case letters in `platform` will be translated to
        lower-case and hyphens will be removed, E.g., ``JR-200`` will be
        translated to ``jr200``.
    '''
    pnames = __package__.split('.')         # parent package
    pnames.append('platform')               # package w/block modules
    pnames.append(platform.lower().replace('-', ''))
    return import_module('.'.join(pnames))

####################################################################
#   bytestream → blocks

def read_block_bytestream(platform, stream):
    ''' Read bytes from `stream`, parse them as tape blocks for `platform`
        and return a sequence of the block objects.
    '''
    bm = get_block_module(platform)
    return bm.read_block_bytestream(stream)

def native_filename(filename):
    ''' Ensure `filename` is a `bytes` to be interpreted in the
        platform-specific character set/encoding.

        If we're given an object that includes character encoding
        information (typically `str`), we convert it to ASCII (or raise an
        error if it cannot be converted). Otherwise we assume that it's
        something that can be converted to `bytes` without specifying
        encoding information.

        `filename` may be `None`, in which case `None` will be returned.
    '''
    if filename is None:    return filename
    try:                    return bytes(filename, encoding='ASCII')
    except TypeError:       return bytes(filename)

def blocks_from_bin(platform, stream, loadaddr=0x0000, filename=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as a machine-langauge program
        as it would be saved on `platform`. `loadaddr` is the default load
        address for the file; this may be ignored if load addresses are not
        supported.

        If `filename` is `None`, a default (perhaps empty) filename
        will be generated. Otherwise `filename` will be processed with
        `native_filename()`.
    '''
    bm = get_block_module(platform)
    return bm.blocks_from_bin(stream, loadaddr, filename)

def blocks_from_obj(platform, stream, filename=None):
    '''Read an as object and create the corresponding blocks.'''
    bm = get_block_module(platform)
    if "blocks_from_obj" in dir(bm):
        return bm.blocks_from_obj(stream, filename=filename)
    else:
        image = asl.parse_obj(stream)
        length = image.contiglen()
        start = image.startaddr
        data = image.contigbytes()
        bin_stream = BytesIO(data)
        return blocks_from_bin(platform, bin_stream, loadaddr=start,
            filename=filename)


def blocks_from_audio(platform, stream):
    '''Convert from audio to a sequence of blocks'''
    bm = get_block_module(platform)
    w = wave.open(stream, 'rb')
    if w.getnchannels() != 1 or w.getsampwidth() != 1:
        raise ValueError('Only mono 8-bit wav files are supported')
    rate = w.getframerate()
    n_samples = w.getnframes()
    samples = w.readframes(n_samples)
    sample_dur = 1.0 / rate
    v2('Rate: %d' % rate)
    v2('Duration: %f' % (sample_dur * n_samples))
    v3('Sample duration: %f microseconds' % (1000000 * sample_dur))
    v3('Samples: %d' % n_samples)
    v2('Samples min: %d' % min(samples))
    v2('Samples max: %d' % max(samples))
    # pulses = samples_to_pulses(samples, sample_dur)
    params = bm.parameters()
    gf = params.get("edge_gradient_factor", 0.5)
    pulses = samples_to_pulses_via_edge_detection(samples, sample_dur, gf)
    pulses = filter_clicks(pulses, sample_dur)
    v2('Number of pulses: %d ' % len(pulses))
    pulse_widths = [dur for (_,_,dur) in pulses]
    v2('Min pulse: %f' % min(pulse_widths))
    v2('Max pulse: %f' % max(pulse_widths))
    fr = bm.FileReader()
    (_,blocks) = fr.read_file(pulses, 0)
    return blocks

####################################################################
#   blocks → bytestream

def write_block_bytestream(platform, blocks, stream):
    ' Write out the bytes of the blocks, as they would be recorded on tape. '
    bm = get_block_module(platform)
    if 'write_block_bytestream' in dir(bm):
        return bm.write_block_bytestream(blocks, stream)
    else:
        stream.write(get_block_bytestream(blocks))

def get_block_bytestream(blocks):
    ''' Return a `bytes` containing the contents of the blocks as they
        would be recorded on tape.
    '''
    return bytes(chain(*( b.to_bytes() for b in blocks )))

def write_file_bytestream(platform, blocks, stream):
    bm = get_block_module(platform)
    if 'write_file_bytestream' in dir(bm):
        return bm.write_file_bytestream(blocks, stream)
    else:
        stream.write(get_file_bytestream(blocks))

def get_file_bytestream(blocks):
    ''' Return a `bytes` containing the contents of the file represented
        by the list of blocks.
    '''
    return bytes(chain(*( b.filedata for b in blocks )))


def blocks_to_audio(platform, blocks, stream):
    '''Write out the blocks as audio'''
    bm = get_block_module(platform)
    # Convert File to pulses
    pulses = bm.FileEncoder().encode_file(blocks)

    # Convert pulses to samples
    rate        = 44100
    sample_dur  = 1.0 / rate
    amp         = 127
    mid         = 128
    samples     = pulses_to_samples(pulses, sample_dur, mid, mid-amp, mid+amp)

    # Write out WAV file
    w = wave.open(stream,'wb')
    w.setnchannels(1)
    w.setsampwidth(1)
    w.setframerate(rate)
    w.writeframes(bytes(samples))


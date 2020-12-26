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

from    importlib  import import_module
from    itertools  import chain

def get_block_module(platform):
    ''' Find, load and return the module containing the block classes for
        `platform`. Upper-case letters in `platform` will be translated to
        lower-case and hyphens will be removed, E.g., ``JR-200`` will be
        translated to ``jr200``.
    '''
    pnames = __package__.split('.')         # parent package
    pnames.append('block')                  # package w/block modules
    pnames.append(platform.lower().replace('-', ''))
    return import_module('.'.join(pnames))

####################################################################
#   bytestream → blocks

def read_block_bytestream(platform, stream):
    ''' Read bytes from `stream`, parse them as tape blocks for `platform`
        and return a sequence of the block objects.
    '''
    bm = get_block_module(platform)
    FH = bm.FileHeader
    B  = bm.Block

    blocks = []
    fh = FH.from_bytes(stream.read(FH.blocklen))
    blocks.append(fh)
    while True:
        b, len = B.from_header(stream.read(B.headerlen))
        b.setdata(stream.read(len), stream.read(1)[0])
        blocks.append(b)
        if b.is_eof:
            break
    return tuple(blocks)

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

def make_blocks_binary(platform, stream, loadaddr, filename=None):
    ''' Read file content bytes from `stream` and create a sequence of tape
        block objects representing that file as a machine-langauge program
        as it would be saved on `platform`. `loadaddr` is the default load
        address for the file; this may be ignored if load addresses are not
        supported.

        If `filename` is `None`, a default (perhaps empty) filename
        will be generated. Otherwise `filename` will be processed with
        `native_filename()`.
    '''
    #   XXX This is probably very JR-200-specific with things like a per-block
    #   address. We need to work out if and how to make it more generic.

    bm = get_block_module(platform)
    FH = bm.FileHeader
    B  = bm.Block

    blocks = []
    blocks.append(FH.make_block(native_filename(filename)))
    blockno = 1
    while True:
        filedata = stream.read(0x100)
        if len(filedata) > 0:
            blocks.append(B.make_block(blockno, loadaddr, filedata))
            blockno += 1; loadaddr += len(filedata)
        else:
            blocks.append(B.make_eof_block(loadaddr))
            break

    return blocks

####################################################################
#   blocks → bytestream

def get_file_bytestream(blocks):
    ''' Return a `bytes` containing the contents of the file represented
        by the list of blocks.
    '''
    return bytes(chain(*( b.filedata for b in blocks )))

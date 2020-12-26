''' Database of input and output formats.
'''

import  cmtconv.bytestream as bs
import  cmtconv.audio as au
from    cmtconv.logging import *
from    pathlib  import Path

#   Map of canonical format name to (input_func, output_func).
FORMATS = {
    'bin': ( bs.blocks_from_bin,        # (platform, stream, loadaddr, filename)
             bs.write_file_bytestream,  # (blocks, stream)
        ),
    'cas': ( bs.read_block_bytestream,  # (platform, stream)
            None,
        ),
    'wav': ( None, None, ),
}

#   Map of format alias to canonical format name.
FORMAT_ALIASES = {
    'cjr': 'cas',
}

def guess_format(format, path, open=open):
    ''' Suggest a format for the given file.

        `format`, if not `None`, will be returned, overriding the guess.
        Otherwise this will try to guess the format from the extension of
        the filename in `path`.

        XXX Eventually this should also try to open the file if it exists
        and determine the format by reading the first part of the contents.
        You may specify `open` as `None` to disable this behaviour, or as a
        mock open routine for testing.
    '''
    if format is not None:
        v1('user-specified format {!r} for file {!r}', format, path)
        return format

    if path is not None:    extension = Path(path).suffix[1:]
    else:                   extension = None
    if extension in FORMATS:
        format = extension
    else:
        format = FORMAT_ALIASES.get(extension)

    v1('guessed format {!r} from extension {!r} of {!r}',
        format, extension, path)
    return format

    #   XXX do not try to use `open` if path is `-`; that's stdin/stdout.

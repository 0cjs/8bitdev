''' testmc.asl - Support for Macro Assembler AS__ assembler output.

    .. _AS: http://john.ccac.rwth-aachen.de:8000/as/
'''

from    testmc.memimage import MemImage
from    testmc.symtab   import SymTab

from    collections   import namedtuple as ntup
from    struct   import unpack_from


####################################################################
#   Object file parsing.
#
#   The `.p` file format is documented in §5.1 "Code Files":
#     http://john.ccac.rwth-aachen.de:8000/as/as_EN.html#sect_5_

def parse_obj_fromfile(path):
    ' Given the path to a ``.p`` file, run `parse_obj` on it. '
    with open(path, 'rb') as stream:
        return parse_obj(stream)

def parse_obj(bytestream):
    ''' Parse the contents of an AS binary file, returning a `MemImage`.
    '''
    return PFile(bytestream)

class PFile(MemImage):
    ''' Parsed Macro Assembler AS code (``.p``) file.
    '''

    class Record(ntup('Record', 'header, segment, gran, addr, length data')):
        ''' A data record from a code file. This is used for both
            full/new ($81) and short/legacy ($01-$7F) records.
        '''

    #   Segement codes
    SEG_UNDEF   = 0x00
    SEG_CODE    = 0x01
    SEG_DATA    = 0x02
    SEG_IDATA   = 0x03
    SEG_XDATA   = 0x04
    SEG_YDATA   = 0x05
    SEG_BDATA   = 0x06
    SEG_IO      = 0x07
    SEG_REG     = 0x08
    SEG_ROMDATA = 0x09

    def __repr__(self):
        ''' We do not want the default representation from `list` because
            that can create confusion when debugging. This is just a
            quick hack, however; the format should not be relied upon.
        '''
        return 'PFfile(entrypoint={} creator={} records={})'.format(
            self.entrypoint, self.creator, super().__repr__())

    def __init__(self, istream):
        ' Parse the given input stream of bytes. '
        super().__init__()
        self.creator = None
        self.istream = istream
        if istream is None: return              # None allowed for testing
        self.parse_magic()
        while True:
            rectype = self.read8()
            if rectype == 0x00:
                self.parse_creator()
                break                       # creator is always last record
            elif rectype <= 0x7F:
                self.parse_oldrec(rectype)
            elif rectype == 0x80:
                self.parse_entrypoint()
            elif rectype == 0x81:
                self.parse_newrec()
            else:
                raise Exception('XXX write me for rectype={}'.format(rectype))

    def read8(self):
        ' Read a byte from the input stream. '
        return self.istream.read(1)[0]

    def read16(self):
        ' Read a little-endian 16-bit unsigned integer from the input stream. '
        return int.from_bytes(self.istream.read(2), 'little', signed=False)
        return 'XXX'

    def read32(self):
        ' Read a little-endian 32-bit unsigned integer from the input stream. '
        return int.from_bytes(self.istream.read(4), 'little', signed=False)

    def parse_magic(self):
        magic, = unpack_from('<H', self.istream.read(2))
        if magic == 0x1489:
            return None
        else:
            raise ValueError('Bad magic number: ${:04X}'.format(magic))

    def parse_creator(self):
        self.creator = self.istream.read()
        return None

    def parse_entrypoint(self):
        self.entrypoint = self.read32()
        return None

    def parse_newrec(self):
        header  = self.read8()
        segment = self.read8()
        gran    = self.read8()
        start   = self.read32()
        length  = self.read16()
        data    = self.istream.read(length)
        if length != len(data):
            raise ValueError('Bad data length: expected {} bytes but read {}' \
                .format(length, len(data)))
        self.append(self.Record(
            header, segment, gran, start, length, data))
        return None

    def parse_oldrec(self, rectype):
        ''' Parse an old-style data record where the header byte determining
            the record type also encodes the processor family.

            Despite the documentation claiming that these record types
            still generated, they appear not to be. So this is
            untested against actual output and we're not putting much
            work into it until we see a need.

            Because GRAN_LOOKUP is incomplete, this may throw a
            KeyError, meaning that you need to update the GRAN_LOOKUP
            table for your particular processor family (or perhaps
            just update your version of AS).
        '''
        header  = rectype
        segment = self.SEG_CODE
        gran    = self.GRAN_LOOKUP[rectype]
        start   = self.read32()
        length  = self.read16()
        data    = self.istream.read(length)
        self.append(self.Record(
            header, segment, gran, start, length, data))

    #   Old-style records do not include the granularity (which is
    #   perhaps why AS seems no longer to generate them, despite the
    #   documentation still saying it does), so we must know the
    #   correct values ourselves. Probably this should be generated
    #   from the AS source code.
    #   WARNING: In the meantime, ensure you carefully confirm new
    #   values before adding them here!
    GRAN_LOOKUP = {
        0x11: 1,    # 65xx/MELPS-740
        0x61: 1,    # 6800, 6301, 6811 (not confirmed from actual AS output)
    }

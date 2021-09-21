''' testmc.asl - Support for Macro Assembler AS__ assembler output.

    .. _AS: http://john.ccac.rwth-aachen.de:8000/as/

    A word of warning here: a testmc "section" is referred to as a
    "segment" in AS documentation, and AS documentation uses "section"
    to refer to local scopes for symbols, which we refer to as
    "scopes." There's no easy fix for this terminology problem; we
    prefer terminology that gives us consistency across toolchains
    rather than using terminology specific to a particular toolchain
    that would then be inconsistent with other toolchains.
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

        Our "sections" are what the AS documentation calls "segments."
        These should not be confused with AS "sections" which are
        actually symbol scopes. (Scoping in AS is dealt with in the
        asl SymTab code and does not apply to `.p` files, which are
        already "linked.")
    '''

    class Record(ntup('Record', 'header, section, gran, addr, length data')):
        ''' A data record from a code file. This is used for both
            full/new ($81) and short/legacy ($01-$7F) records.
        '''

    #   Section (generic term) / segment (AS term) codes
    SE_UNDEF    = 0x00
    SE_CODE     = 0x01
    SE_DATA     = 0x02
    SE_IDATA    = 0x03
    SE_XDATA    = 0x04
    SE_YDATA    = 0x05
    SE_BDATA    = 0x06
    SE_IO       = 0x07
    SE_REG      = 0x08
    SE_ROMDATA  = 0x09

    def __repr__(self):
        ''' We do not want the default representation from `list` because
            that can create confusion when debugging. This is just a
            quick hack, however; the format should not be relied upon.
        '''
        return 'PFile(entrypoint={} creator={} records={})'.format(
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
        section = self.read8()
        gran    = self.read8()
        start   = self.read32()
        length  = self.read16()
        data    = self.istream.read(length)
        if length != len(data):
            raise ValueError('Bad data length: expected {} bytes but read {}' \
                .format(length, len(data)))
        self.append(self.Record(
            header, section, gran, start, length, data))
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
        section = self.SE_CODE
        gran    = self.GRAN_LOOKUP[rectype]
        start   = self.read32()
        length  = self.read16()
        data    = self.istream.read(length)
        self.append(self.Record(
            header, section, gran, start, length, data))

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

####################################################################
#   Symbol table (map file) parsing.
#
#   The `.map` file format is documented in §5.2 "Debug Files":
#     http://john.ccac.rwth-aachen.de:8000/as/as_EN.html#sect_5_2_
#   However, this documentation is not actually correct; see below.

def parse_symtab_fromfile(path):
    ''' Given the path to a ``.map`` file, run `parse_symtab` on it.

        The .p files use the same encoding as the input files.

        This assumes that the assembler is configured to use UTF-8
        encoding. This is preferably done explicitly with the
        ``-codepage utf-8`` option rather than relying on the
        environment's locale.
    '''
    with open(path, 'r', encoding='utf-8') as stream:
        return parse_symtab(stream)

class ParseError(RuntimeError):
    pass

def parse_symtab(stream):
    ''' Parse the contents of an AS .map file, returning a `SymTab`.

        The map file is always ASCII-encoded (chars with the high bit set
        are not allowed in symbol names); we expect that the caller opened
        the file in text mode with that encoding specified. Newline format
        is less criticial; the caller must ensure that it's opened such
        that `readline()` works but we ignore all whitespace (\r, \n) at
        line ends.
    '''
    symbols = []
    while True:
        line = stream.readline()
        if line == '': break    # EOF

        if line.strip() == '':
            pass # skip blank lines
        elif line.startswith('Segment '):
            #   Source code line number to machine code address mapping
            #   information. We (currently) don't use this.
            ps_skip_block(stream)
        elif line.startswith('Symbols in Segment '):
            #   List of all symbols in a section. Symbol names include
            #   scope numbers for symbols in a local scope, but we do not
            #   yet know the name of that scope so we deal with that later.
            l = len('Symbols in Segment ')
            section_name = line[l:].strip()
            symbols += ps_parse_section(section_name, stream)
        elif line.startswith('Info for Section '):
            #   Number to name mapping for local variable scopes.
            #   We currently don't handle this, but we need to because a
            #   given scope can have a different number from run to run.
            ps_skip_block(stream)
        else:
            raise ParseError(line.rstrip())
    #   Here is where we should be renaming locally scoped symbols to
    #   have the scope name, rather than number, involved in it in
    #   some way. Potentially we might also use a Symbol subclass that
    #   allows us to note how things are scoped.
    return SymTab(symbols)

def ps_skip_block(stream):
    ' Read up to and including the next empty line. '
    while True:
        if '' == stream.readline().strip():
            return None

def ps_parse_section(secname, stream):
    ''' Read the symbols in a section, discarding the ending blank line.
        Returns a list of `Symbol` objects.

        This assumes that all ``Int`` values are in hexadecimal. This
        is not specified in the documentation but experimentally seems
        to be the case.

        ASL ≥ cur-142-bld172 has 6 fields, earlier versions have 5.
        However, from about 2008 through asl-current-142-bld151 there was a
        bug in .map file output where spaces in symbol values were not
        translated to `\032` as documented__ in §5.2. This does not work
        with those buggy versions, but we du a heuristic check for some
        cases of wrong output: if the number of fields is other than 5 or
        6, we raise a ParseError.

        .. _documented: http://john.ccac.rwth-aachen.de:8000/as/

    '''
    syms = []
    while True:
        line = stream.readline().strip()
        if '' == line:                      # blank line or EOF
            return syms

        fields = line.split()
        if len(fields) not in (5, 6):
            #   See docstring above.
            raise ParseError('Bad map file fields (see code):'
                ' {} fields in line {}'
                .format(len(fields), repr(line)))

        name, type, value = fields[0], fields[1], fields[2]
        # size = fields[3]
        # used = fields[4]
        # isvar = fields[5]  # ASL ≥ cur-142-bld172: '0'=const, '1'=var


        if type == 'Int':
            value = int(value, base=16)
        elif type == 'Float':
            value = float(value)
        elif type == 'String':
            value = aslunescape(value)
        else:
            raise ParseError("Unknown type '{}': {}".format(type, line))
        sym = SymTab.Symbol(name, value, secname)
        syms.append(sym)

def aslunescape(s):
    ''' Unescape a string with AS `\nnn` decimal escapes.
        This does very little error checking because we don't expect
        to see badly formed strings.
    '''
    if len(s) == 0:
        return s
    elif s[0] != '\\':
        return s[0] + aslunescape(s[1:])
    else:
        return chr(int(s[1:4])) + aslunescape(s[4:])

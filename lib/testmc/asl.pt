from    testmc.asl   import *

from    io   import BytesIO, StringIO
from    pathlib import Path
import  pytest
import  re

####################################################################
#   Test support

#   XXX This works only from repo top level dir.
TESTDATA_DIR = 'lib/testmc/testfiles'

def tdatafile(filename):
    ''' Return a ByteStream reading from the given test file.
        This returns a context manager and so can be used with ``with``.
    '''
    path = Path(TESTDATA_DIR, filename)
    return open(str(path), 'rb')

####################################################################
#   Object file parsing.
#
#   The `.p` file format is documented in §5.1 "Code Files":
#     http://john.ccac.rwth-aachen.de:8000/as/as_EN.html#sect_5_

#
#   Test support

bfh = bytes.fromhex

def PF(bs):
    ' Build a PFile with the given bytes as its input and parse not yet run. '
    pf = PFile(None)
    pf.istream = BytesIO(bs)
    return pf

def recnodata(rec):
    ' Return metadata for `PFile.Record` for easy asserting. '
    return rec.header, rec.section, rec.gran, rec.addr, rec.length

SE_CODE = PFile.SE_CODE
SE_DATA = PFile.SE_DATA

#
#   Tests for individual record parsters

pmagic  = bfh('89 14')              # Magic number, always at start
def test_PFile_parse_magic():
    assert None is PF(pmagic).parse_magic()

    with pytest.raises(ValueError) as ex:
        PF(bfh('14 89')).parse_magic()
    assert ex.match('Bad magic number: \$8914')

p00     = b'\x00Mr. Pufinpuff'      # Creator record; always at end
def test_PFile_parse_creator():
    pf = PF(p00[1:])
    assert     None is pf.creator

    creator = b'Mr. Pufinpuff'
    assert     None is pf.parse_creator()
    assert  creator == pf.creator
    assert      b'' == pf.istream.read()  # consumed all remaining input

p80     = b'\x80\x78\x56\x34\x12'   # Entrypoint record
def test_PFile_parse_entrypoint():
    pf = PF(p80[1:])
    assert None is pf.entrypoint
    pf.parse_entrypoint()
    assert 0x12345678 == pf.entrypoint
    assert b'' == pf.istream.read() # consumed all remaining input

p61  = b'\x61' \
        + b'\x76\x54\x32\x10' \
        + b'\x0B\x00' \
        + b'6800 record'
def test_PFFile_parse_61():
    pf = PF(p61[1:])
    assert None is pf.parse_oldrec(p61[0])
    assert (
        0x61,       # record header, 65816/MELPS-7700
        0x01,       # CODE section
        0x01,       # granularity = 1 byte
        0x10325476, # start address
        0x000B,     # length of data
        ) == recnodata(pf[0])
    assert 0x0B == len(pf[0].data)
    assert b'6800 record' == pf[0].data
    assert b'' == pf.istream.read() # consumed all remaining input

p81     = b'\x81' \
        + b'\x61\x02\x01' \
        + b'\x89\xAB\xCD\xEF' \
        + b'\x10\x00' \
        + b'6800, 6301, 6811'
def test_PFFile_parse_81():
    pf = PF(p81[1:])
    assert None is pf.parse_newrec()
    assert (
                    0x61,       # record header, 65816/MELPS-7700
                    SE_DATA,
                    0x01,       # granularity = 1 byte
                    0xEFCDAB89, # start address
                    0x0010,     # length of data
                    )           == recnodata(pf[0])
    assert  b'6800, 6301, 6811' == pf[0].data
    assert                 0x10 == len(pf[0].data)
    assert                  b'' == pf.istream.read() # consumed all input

def test_PFFile_parse_newrec_badlen():
    len_idx = 8
    assert 0x10 == p81[len_idx]     # Confirm we have length offset correct.

    shortrec = list(p81)
    shortrec[len_idx] = 0x11
    #assert list(p81) == shortrec   # for manual check
    pf = PF(bytes(shortrec[1:]))
    with pytest.raises(ValueError) as ex:
        pf.parse_newrec()
    assert ex.match('Bad data length: expected 17 bytes but read 16')

#
#   Tests for full-file parsing

def test_PFFile_parse_obj_constructed():
    input = pmagic + p61 + p81 + p80 + p00
    pf = PFile(BytesIO(input))
    assert 0x12345678 == pf.entrypoint
    assert b'Mr. Pufinpuff' == pf.creator
    def recsummary(pf):
        return  (pf.header, pf.section, pf.length, len(pf.data))
    assert (0x61, SE_CODE, 0x0B, 0x0B) == recsummary(pf[0])
    assert (0x61, SE_DATA, 0x10, 0x10) == recsummary(pf[1])
    assert 2 == len(pf)

def test_PFFile_parse_obj_real_file():
    with tdatafile('asl/program.p') as f:
        pf = parse_obj(f)
        assert b'' == pf.istream.read() # consumed all input

    assert re.match(b'AS 1\.', pf.creator) #   AS 2.x may require changes
    assert           0x0366 == pf.entrypoint

    assert (
        0x11,       # record header, 65xx/MELPS-740
        0x01,       # CODE section
        0x01,       # granularity = 1 byte
        0x280,      # start address
        0x00F2,     # length of data
        )                   == recnodata(pf[0])
    assert             0xF2 == len(pf[0].data)

    assert (
        0x11,       # record header, 65xx/MELPS-740
        0x01,       # CODE section
        0x01,       # granularity = 1 byte
        0xF480,     # start address
        0x0010,     # length of data
        )                   == recnodata(pf[1])
    assert             0x10 == len(pf[1].data)
    assert    b'Hello.\x00' == pf[1].data[0:7]

    assert 2 == len(pf)

####################################################################
#   Symbol table (map file) parsing.
#
#   The `.map` file format is documented in §5.2 "Debug Files":
#     http://john.ccac.rwth-aachen.de:8000/as/as_EN.html#sect_5_2_

@pytest.mark.parametrize('nl', ('\n', '\r\n', '\r'))
def test_ps_skip_block(nl):
    lines = nl.join(['line1', 'line2', '', 'line3']) + nl
    stream = StringIO(lines, newline=None)
    ps_skip_block(stream)
    assert 'line3\n' == stream.read()

def test_ps_skip_block_eof():
    stream = StringIO('ab\ncd\n')
    ps_skip_block(stream)
    assert '' == stream.read()

def test_ps_parse_section_eof():
    assert [] == ps_parse_section('', StringIO(''))

def test_aslmapstring():
    assert ''               == aslunescape('')
    assert 'abc'            == aslunescape('abc')
    assert '\x10'           == aslunescape('\\016')
    assert '\x00\x01\x7f'   == aslunescape('\\000\\001\\127')
    assert ' \x7b4\x0c '    == aslunescape(' \\1234\\012 ')

def test_ps_parse_section():
    input = '''\
stringvalue                           String ordinary                  -1  0
this_is_a_symbol_name_longer_than_33_chars String this-is-a-value-longer-than-27-characters -1 0
intvalue                              Int    CAFEBABE                  -1  0
CONSTPI                               Float  3.141592653589793         -1  0
sized                                 Int    0                         123 0
used                                  Int    0                         -1  1
nonprinting                           String \\032_\\000_\\127_\\032   -1  0

ignored
'''
    sn = 'SEname'
    stream = StringIO(input)
    syms = ps_parse_section(sn, stream)
    assert 'ignored\n' == stream.read()

    assert ('stringvalue', 'ordinary', sn)              == syms[0]
    assert 'this_is_a_symbol_name_longer_than_33_chars' == syms[1].name
    assert 'this-is-a-value-longer-than-27-characters'  == syms[1].value
    assert ('intvalue', 3405691582, sn)                 == syms[2]
    assert ('CONSTPI', 3.141592653589793, sn)           == syms[3]
    assert ('sized', 0, sn)                             == syms[4]
    assert ('used', 0, sn)                              == syms[5]
    assert 'nonprinting'                                == syms[6].name
    assert ' _\x00_\x7f_ '                              == syms[6].value
    assert 7 == len(syms)

def test_ps_parse_section_space_in_string():
    ''' If we find an actual space in a string we are using a buggy
        version of AS that did not properly substitute ``\032``.
    '''
    stream = StringIO('name String a value -1 0')
    with pytest.raises(ParseError) as ex:
        ps_parse_section('', stream)
    assert ex.match('Bad asl version?')

def test_parse_symtab_empty():
    ' Blank lines are ignored '
    stream = StringIO('\n\r\n\n')
    symtab = parse_symtab(stream)
    assert '' == stream.read()   # consumed all input
    assert 0 == len(symtab)

def test_parse_symtab_ParseError():
    s = StringIO(' one\n two\n')
    with pytest.raises(ParseError) as ex:
        parse_symtab(s)
    assert ex.match(re.compile('^ one$'))
    assert ' two\n' == s.read()

#
#   Tests for full-file parsing

def test_parse_symtab_fromfile():
    path = Path(TESTDATA_DIR, 'asl/program.map')
    with open(str(path), 'rt', encoding='ascii') as f:
        stab = parse_symtab(f)
        assert '' == f.read()   # consumed all input

    assert 0xBC614E                 == stab.eq0int
    assert 1.2345                   == stab.eq1float
    assert 6.78E-90                 == stab.eq2floatE
    assert 'nospace'                == stab.eq3strN
    assert ' lead/trail space '     == stab.eq4strT
    assert '\0\t\n\r"\'\\\x7F'      == stab.eq5strW
    assert 'This is a very long string, with a trailing space: ' \
                                    == stab.eq6strL

    assert 0x280 == stab.global0
    assert 0x288 == stab.globalinc

    assert 'NOTHING'    == stab.sym('eq0int').section
    assert 'CODE'       == stab.sym('global0').section

    assert 59 == len(stab)

def test_parse_symtab_fromfile_notfound():
    path = '/this/file/should/not/exist/for/this/test'
    with pytest.raises(FileNotFoundError) as ex:
        parse_symtab_fromfile(path)
    assert ex.match(path)

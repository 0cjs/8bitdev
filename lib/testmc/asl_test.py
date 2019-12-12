from    testmc.asl   import *

from    io   import BytesIO
from    pathlib import Path
import  pytest
import  re

####################################################################
#   Test support

def tdatafile(filename):
    ''' Return a ByteStream reading from the given test file.
        This returns a context manager and so can be used with ``with``.
    '''
    dir = 'lib/testmc/testfiles'    # XXX works only from repo top level dir
    path = Path(dir, filename)
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
    return rec.header, rec.segment, rec.gran, rec.addr, rec.length

SEG_CODE = PFile.SEG_CODE
SEG_DATA = PFile.SEG_DATA

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
        0x01,       # CODE segment
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
                    SEG_DATA,
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
        return  (pf.header, pf.segment, pf.length, len(pf.data))
    assert (0x61, SEG_CODE, 0x0B, 0x0B) == recsummary(pf[0])
    assert (0x61, SEG_DATA, 0x10, 0x10) == recsummary(pf[1])
    assert 2 == len(pf)

def test_PFFile_parse_obj_real_file():
    with tdatafile('asl/program.p') as f:
        pf = parse_obj(f)
        assert b'' == pf.istream.read() # consumed all input

    assert re.match(b'AS 1\.', pf.creator) #   AS 2.x may require changes
    assert           0x0366 == pf.entrypoint

    assert (
        0x11,       # record header, 65xx/MELPS-740
        0x01,       # CODE segment
        0x01,       # granularity = 1 byte
        0x280,      # start address
        0x00F2,     # length of data
        )                   == recnodata(pf[0])
    assert             0xF2 == len(pf[0].data)

    assert (
        0x11,       # record header, 65xx/MELPS-740
        0x01,       # CODE segment
        0x01,       # granularity = 1 byte
        0xF480,     # start address
        0x0010,     # length of data
        )                   == recnodata(pf[1])
    assert             0x10 == len(pf[1].data)
    assert    b'Hello.\x00' == pf[1].data[0:7]

    assert 2 == len(pf)

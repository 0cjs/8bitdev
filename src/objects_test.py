from    testmc.m6502 import  Machine, Registers as R
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/objects.p')
    return M

####################################################################
#   Tests

@pytest.mark.parametrize('obj, expected', (
    #   obj     (obfmtid, oblen, unused, smallint)
    # Least significant bits of obj determine type:
    #   %00   pointer to object
    (0x0000,    (0xFF, 0xFF, 0xFF,     -1)),
    (0xFFFC,    (0xFF, 0xFF, 0xFF,     -1)),
    #   %10   number: smallint
    (0x0002,    (0xFF, 0xFF, 0xFF,      0)),
    (0x0006,    (0xFF, 0xFF, 0xFF,    256)),
    (0x000A,    (0xFF, 0xFF, 0xFF,    512)),
    (0x000E,    (0xFF, 0xFF, 0xFF,    768)),
    (0x0402,    (0xFF, 0xFF, 0xFF,      4)),
    (0xC03E,    (0xFF, 0xFF, 0xFF,   4032)),    # non-zero MSB positive number
    (0xFF7E,    (0xFF, 0xFF, 0xFF,   8191)),    # smallint max
    (0x0082,    (0xFF, 0xFF, 0xFF,  -8192)),    # smallint min
    (0xFDFE,    (0xFF, 0xFF, 0xFF,     -3)),
    (0x2492,    (0xFF, 0xFF, 0xFF,  -7132)),    # non-zero MSB negative number
    #   %11   obdata: format number is LSB[7‥2], length is MSB
    (0x00FF,    (0xFF, 0x00, 0xFF,     -1)),
    (0x21EF,    (0xEF, 0x21, 0xFF,     -1)),
    (0xFE07,    (0x07, 0xFE, 0xFF,     -1)),
    #   %01   unused/invalid
    (0x0001,    (0xFF, 0xFF, 0x00,     -1)),
    (0xFF01,    (0xFF, 0xFF, 0xFF,     -1)),
    (0x3401,    (0xFF, 0xFF, 0x34,     -1)),
))
def test_typedisp(M, obj, expected):
    S = M.symtab
    M.deposit(S.obfmtid,    0xFF)   # set outputs to sentinel values
    M.deposit(S.oblen,      0xFF)
    M.deposit(S.unused,     0xFF)
    M.depword(S.smallint,   0xFFFF) # -1

    M.depword(S.obj, obj)
    M.call(S.typedisp)
    obfmtid, oblen, unused \
        = M.byte(S.obfmtid), M.byte(S.oblen), M.byte(S.unused)
    smallint =int.from_bytes(
        M.bytes(S.smallint, 2), byteorder='little', signed=True)

    print('obj ${:04X}, obfmtid ${:02X}, oblen ${:02X} unused ${:02X}, ' \
          'smallint: ${:04X} {}' \
          .format(obj, obfmtid, oblen, unused, smallint, smallint))

    assert expected == (obfmtid, oblen, unused, smallint)
    assert obj == M.word(S.obj), 'original obj should never be modified'

    #   XXX It might be useful to set some flags based on type.
    #   Depending on the next processing step may want to know
    #   heapdata vs. tagged pointer and pointer vs. value.

    cycles = M.mpu.processorCycles
    #   Uncomment to see cycle count for each test.
    #assert 'cycles' ==  cycles

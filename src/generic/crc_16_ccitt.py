''' CRC-16-CCITT checksum test

    This tests an `S.cksum_crc_16_ccitt` routine taking the data address
    and length to checksum, assuming the standard initialisation vector,
    and returning the CRC and next address after the checksummed range.

    The module importing this must supply the following functions:
    - `setup(m, data, length)`: set up the params for the routine
    - `result(m)`: return the CRC and addr of end of range
'''

from    binascii  import crc_hqx
from    testmc  import tmc_tid
import  pytest

@pytest.mark.parametrize('expected_crc, input', [
    #   These from answers to: https://stackoverflow.com/q/1918090/107294
    (0xB1E4, [0x12, 0x34, 0x56, 0x70]),
    (0x1AAD, [0x5A, 0x26, 0x19, 0x77]),
    (0x29B1, b'123456789'),
    (  None, [0]),
    (  None, [0, 0]),
    (  None, [0, 0, 0, 0]),
    (  None, [0xED] * 0xFF),
    (  None, [0xED] * 0x100),
    (  None, [0xED] * 0x101),
    (  None, [0xED] * 0x201),
   #(  None, [0xED] * 0x1001),      # ~0.5s
    #   The following require maxsteps=1e7
   #(  None, [0xED] * 0xDE00),
   #(  None, [0xED] * 0xDF00),      # XXX bad CRC; why?
], ids=tmc_tid)
def test_cksum_crc_16_ccitt(request, m, S, R, expected_crc, input):
    setup = getattr(request.module, 'setup')
    result = getattr(request.module, 'result')

    if expected_crc is None:
        expected_crc = crc_hqx(bytes(input), 0xFFFF)
    DATA = 0x180
    m.deposit(DATA, input)
    setup(m, DATA, len(input))
    print(f'data {m.hexdump(DATA, 12)} …')
    print(f' expected: crc=${expected_crc:04X} nextstart:${DATA+len(input)}')

    m.call(S.cksum_crc_16_ccitt, maxsteps=1e7)
    crc, nextstart = result(m)

    print(f'   actual: crc=${crc:04X} nextstart:${nextstart}')
    assert (expected_crc, DATA+len(input)) \
        == (crc,          nextstart      )

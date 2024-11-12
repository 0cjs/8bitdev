import  pytest

@pytest.mark.parametrize('sym, val', [
    ('T_LB_8',      0x08),
    ('T_MB_8',      0x00),
    ('T_LB_FEDC',   0xDC),
    ('T_MB_FEDC',   0xFE),
    ('T_LB_12340',  0x40),
    ('T_MB_12340',  0x23),
])
def test_LB_MB(S, sym, val):
    ''' The LB and MB macros work on assembler symbol values and so should
        work the same on every architecture.
    '''
    assert S[sym] == val

def test_ds_db_dw(m, S):
    start = S.defalloctest
    assert S.dstest0                    == start
    assert S.dstest1                    == start+3
    assert S.dbtest                     == start+4
    assert b'\x00abc\xFF\xFF\xFF\x00'   == bytes(m.bytes(S.dbtest, 8))
    assert S.dwtest                     == start+12
    assert 0xABCD                       == m.word(S.dwtest)

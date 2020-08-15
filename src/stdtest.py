def test_ds_db_dw(m, S):
    start = S.defalloctest
    assert S.dstest0            == start
    assert S.dstest1            == start+3
    assert S.dbtest             == start+4
    assert b'\x00abc\xFF\xFF'   == bytes(m.bytes(S.dbtest, 6))
    assert S.dwtest             == start+10
    assert 0xABCD               == m.word(S.dwtest)
    assert (0xCD, 0xAB)         == (m.byte(S.dwtest), m.byte(S.dwtest+1))

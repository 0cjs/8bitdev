from testmc.midump import *
from testmc.asxxxx import MemImage

MR = MemImage.MemRecord

def test_hexfield():
    assert '00 ' == hexfield(0)
    assert 'ff ' == hexfield(255)
    assert '   ' == hexfield(None)

def test_charfield():
    assert '.' == charfield(0x00)
    assert '.' == charfield(0x19)
    assert ' ' == charfield(0x20)
    assert '~' == charfield(0x7e)
    assert '.' == charfield(0x7f)
    assert '.' == charfield(0xff)

def test_alignmentshift():
    assert (  0, 0x400) == alignmentshift(0x400)
    assert ( -1, 0x400) == alignmentshift(0x401)
    assert (-15, 0x400) == alignmentshift(0x40f)
    assert (  0, 0x410) == alignmentshift(0x410)

def test_format_memline_full():
    #   Note we add additional data on the right that should not be displayed.
    addr        = 0x400
    data        = [0xff, 0x00, 0x30, 0x40] * 4 + [0xEE, 0xEE]
    hexfields   = 'ff 00 30 40 ff 00 30 40 - ff 00 30 40 ff 00 30 40'
    charfields  = '..0@..0@ ..0@..0@'

    expected    = '0400: {}  {}'.format(hexfields, charfields)
    assert expected == format_memline(addr, data)

def test_format_memline_empty_right():
    addr        = 0x400
    #             Extension uses tuples internally, so ensure list input works.
    data        = [0x41, 0x42, 0x43, 0x44]
    hexfields   = '41 42 43 44             -                        '
    charfields  = 'ABCD             '

    expected    = '0400: {}  {}'.format(hexfields, charfields)
    assert expected == format_memline(addr, data)

def test_format_memline_empty_left():
    addr        = 0x404
    #             Extension uses tuples internally, so ensure list input works.
    data        = [0x40, 0x41, 0x42, 0x43, 0x44]
    hexfields   = '            40 41 42 43 - 44                     '
    charfields  = '    @ABC D       '

    expected    = '0400: {}  {}'.format(hexfields, charfields)
    assert expected == format_memline(addr, data)

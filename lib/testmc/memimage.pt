from    collections   import namedtuple as ntup
from    struct   import unpack_from
from    testmc.memimage   import MemImage

def test_memimage_entrypoint():
    mi = MemImage()
    assert None is mi.entrypoint
    mi.entrypoint = 0x1234          # currently no accessors; set it directly

def test_memimage_memrec():
    mi = MemImage()
    assert  0 == len(mi)
    assert [] == mi

    testdata =  b'\x00\x01\x02\x03\0x04'
    mi.addrec(0x1234, testdata)
    assert (0x1234, testdata) == mi[0]
    assert 1 == len(mi)

    for addr, data in mi:           # make sure we're iterable
        assert 0x1234 == addr
        assert testdata == data
    for rec in mi:                  # and our tuple has accessors
        assert 0x1234 == rec.addr
        assert testdata == rec.data

def test_memimage_memrec_alternate():
    ''' When MemRec is a different type with additional attributes,
        `for` should still return (addr,data) tuples.
    '''
    MR = ntup('MR', 'x, addr, y, data, z')
    testaddr = 0x2345
    testdata = b'\x67\x89\xAB\xCD\xEF'

    mi = MemImage()
    mi.append(MR('x', testaddr, 'y', testdata, 'z'))
    for addr, data in mi:
        assert testaddr == addr
        assert testdata == data

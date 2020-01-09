from    testmc.m6502 import  Machine, Registers as R

from    collections.abc  import Iterable
import  pytest


@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/src/heap.p')
    return M

####################################################################
#   Heapdata types

def hdtype(n):
    return (n << 2) | 1

HDT_FREE        = hdtype(0)     # free block object
HDT_ENVHEADER   = hdtype(2)     # environment object header
HDT_ENVENTRY    = hdtype(3)     # environment object binding entry
HDT_SYMBOL      = hdtype(8)     # symbol

TT              = hdtype(63)    # used only by tests

TT              = hdtype(63)    # used only by tests

def test_HDT_values(M):
    ''' Ensure this test code has defined with the same values all of
        the HDT_* constants defined in the assembly source.
    '''
    for name, value in M.symtab:
        if not name.startswith('HDT_'): continue
        assert globals()[name] == value, name

    #   Confirm value of our test heapdata type
    assert 0xFD == TT

####################################################################
#   Test support: heap setup

def setheap(M, start, *, end=None, len=None, heaplowat=None, init=False):
    ''' Set up data structures for a heap starting at `start`. One of
        `end` (the first address after the heap) or `len` (the length
        of the heap from which the end address will be calculated)
        must be provided. If `init` is `True` the native heap
        initialization routine will be called, otherwise the caller is
        responsible for initializing data objects and free space in
        the heap.
    '''
    if end is not None and len is not None:
        raise ValueError('Only one of `end` and `len` may be specified.')
    if end is not None:     endaddr = end
    elif len is not None:   endaddr = start + len
    else:                   raise ValueError(
                                'One of `end` or `len` must be specified.')

    S = M.symtab
    M.depword(S.heapstart, start)
    M.depword(S.heaplowat, start if heaplowat is None else heaplowat)
    M.depword(S.heapend, endaddr)
    if init:
        M.call(S.heapinit)
    return start

def heapobjs(M, *, data=False, free=False, limit=None):
    ''' Return a list of the objects on the heap. Each object is
        returned as a tuple of ``(type, datalen)``, or
        ``(type, datalen, data)``, if `data` is `True`.

        For a cons cell, where the least significant bits of the type
        are %00, ``type`` and ``datalen`` are -1 and ``data`` is a
        pair of the two words in the cell.

        For a heapdata object, where the least significant bits of the
        type are %01, ``type`` is the type byte (as defined in the
        ``HD_*`` constants in this module), ``datalen`` is the length
        byte from the object header, and ``data`` a sequence of
        ``datalen`` bytes following the header.

        If any other "type" of object is encountered (least
        significant bits are %10 or %11), an exception will be raised
        as these are tagged pointers that should never appear as
        actual objects in the heap.

        "Free space block" objects of type `HDT_FREE` are skipped,
        not returned, unless `free` is `True`.

        Setting `limit` will return only the first *limit* objects,
        not including free space block objects unless `free` is `True`.
    '''
    S = M.symtab
    objs = []
    pos = M.word(S.heapstart)
    end = M.word(S.heapend)
    while pos < end:
        type = M.byte(pos)
        if type & 0b11 == 0b00:
            #   Cons cell
            if not data:
                objs.append((-1, -1))
            else:
                objs.append((-1, -1, M.words(pos, 2)))
            pos += 4
        elif type & 0b11 == 0b01:
            #   Heapdata object
            datalen  = M.byte(pos+1)
            if free or type != HDT_FREE:
                if not data:
                    objs.append((type, datalen))
                else:
                    databytes = M.bytes(pos+2, datalen)
                    objs.append((type, datalen, databytes))
            #   Header length + data length aligned up to next dword.
            pos += ((2 + datalen + 3) & 0xFFC)
        else:
            raise ValueError('Invalid object type ${:02X} in heap at ${:04X}' \
                .format(type, pos))
        if limit is not None and len(objs) >= limit:
            return objs
    return objs

def buildheap(M, addr, objs=None, heaplowat=None):
    ''' Build a test heap at `addr` containing the given `objs`.
        This is done entirely "by hand" and does not depend on any of
        the code under test. No error checking is done; if invalid
        data are given, an invalid heap will be produced.

        `objs` is a sequence of 3-tuples of ``(typebyte, lengthbyte,
        fill)``. The type and length byte values are placed in the
        first and second bytes of the current position in the heap;
        these may be an actual heapdata type and length to place a
        heapdata object or any other arbitrary values which will be
        the car of a cons cell. The fill is either an integer number
        of bytes to skip or a sequence of bytes to fill in after the
        type and length bytes.

        The `heapstart` and `heaplowat` memory locations will be
        filled with the given parameters. (`heaplowat` defaults to
        `addr`. It must be explicitly specified if the heap does not
        start with a free block; this will not calculate the actual
        position of the first free block.) `heapend` will be
        calculated from the data and filled in.

        The length of the built heap will be returned.
    '''
    #   Making objs a keyword param with a default value allows us to
    #   specify the optional heaplowat before it.
    if objs is None:        raise ValueError('objs must be specified')
    if heaplowat is None:   heaplowat=addr

    S = M.symtab
    pos = addr
    for typebyte, sizebyte, fill in objs:
        M.deposit(pos, [typebyte, sizebyte])
        pos += 2
        if not isinstance(fill, Iterable):
            pos += fill
        else:
            M.deposit(pos, fill)
            pos += len(fill)

    setheap(M, addr, end=pos, heaplowat=heaplowat)
    return pos - addr   # length

####################################################################
#   Tests for test support

def test_heapobjs(M):
    S = M.symtab
    start = 0x0FFC
    heapimage = [
        HDT_FREE,   2, 0xA0, 0xA1,              # min-size free block object
        0x00, 0x00, 0x00, 0x00,                 # cons cell
        TT,         2, 0xB0, 0xB1,              # min-size other object
        HDT_FREE, 254, ] + [0x99]*254 + [       # max-size free block object
        0xFC, 0xFF, 0xFC, 0xFF,
        TT,         3, 0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5,
        0x80, 0x81, 0x84, 0x85,                 # cons cell
    ]
    setheap(M, start, len=len(heapimage))
    M.deposit(start, heapimage)

    assert [    (HDT_FREE,    2),
                (-1,         -1),
                (TT,          2),
                (HDT_FREE,  254),
                (-1,         -1),
                (TT,          3),
                (-1,         -1),
        ] == heapobjs(M, free=True)
    assert [    (-1,         -1),
                (TT,          2),
                (-1,         -1),
                (TT,          3),
        ] == heapobjs(M, limit=4)

def test_heapobjs_alignment(M):
    S = M.symtab
    start = 0x0FF0
    heapimage = [
        TT, 0, 0x10, 0x11,
        TT, 1, 0x10, 0x11,
        TT, 2, 0x10, 0x11,
        TT, 3, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25,
        TT, 4, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25,
        TT, 5, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25,
        TT, 6, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25,
        TT, 7, 0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,
    ]
    setheap(M, start, len=len(heapimage))
    M.deposit(start, heapimage)
    objs = heapobjs(M, data=True)
    assert [
        (TT, 0, []),
        (TT, 1, [0x10, ]),
        (TT, 2, [0x10, 0x11, ]),
        (TT, 3, [0x20, 0x21, 0x22, ]),
        (TT, 4, [0x20, 0x21, 0x22, 0x23, ]),
        (TT, 5, [0x20, 0x21, 0x22, 0x23, 0x24, ]),
        (TT, 6, [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, ]),
        (TT, 7, [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, ]),
        ] == objs

@pytest.mark.parametrize('type', (2, 3, 6, 7))
def test_heapobjs_badtype(M, type):
    S = M.symtab
    start = 0x0080
    heapimage = [ type, 0, 0, 0 ]
    setheap(M, start, len=len(heapimage))
    M.deposit(start, heapimage)
    with pytest.raises(ValueError) as ex:
        heapobjs(M, data=True)
    assert ex.match(r'Invalid object type \$0[2367] in heap at \$0080')

def test_buildheap(M):
    heapdata = [
        (0x00,    0x00,  2),
        (0xA0,    0xB1,  (0xC4, 0xD5)),
        (HDT_SYMBOL, 3,  b'abc\1\2\3'),
        (TT,        11,  14),
        (0x34,    0x12,  (0x78, 0x56))
        ]
    expected = [
        0x00, 0x00, 0x00, 0x00,
        0xA0, 0xB1, 0xC4, 0xD5,
        HDT_SYMBOL, 3, ord('a'), ord('b'), ord('c'), 1, 2, 3,
        TT,        11, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x34, 0x12, 0x78, 0x56,
    ]
    addr  = 0x1004;
    length = len(expected)
    M.deposit(addr-1, 0xEE); M.deposit(addr+length, 0xEF) # guard bytes
    buildlen = buildheap(M, addr, heapdata)
    assert [0xEE] + expected + [0xEF] == M.bytes(addr-1, length+2)
    assert length == buildlen

####################################################################
#   utility routine tests

@pytest.mark.parametrize('p0, a, expected', (
    (0x12FF, 0x04, 0x1303),
))
def test_p0add(M, p0, a, expected):
    S = M.symtab
    M.depword(S.P0, p0)
    M.call(S.p0add, R(a=a, x=34, y=56))
    assert expected == M.word(S.P0)
    assert R(x=34, y=56) == M.regs

@pytest.mark.parametrize('heapend, pN, x, carry', (
    (0x4280, 0x0000, 0, False),
    (0x4280, 0x4100, 0, False),
    (0x4280, 0x41FF, 0, False),
    (0x4280, 0x4200, 0, False),
    (0x4280, 0x427F, 0, False),
    (0x4280, 0x4280, 0, True),
    (0x4280, 0x42FF, 0, True),
    (0x4280, 0x4300, 0, True),
    (0x4280, 0xFFFF, 0, True),
    #   Other locations for the zero-page pointer
    (0x1000, 0x0FFF, 3, False),
    (0x1000, 0x1000, 6, True),
))
def test_pXpastheap(M, heapend, pN, x, carry):
    S = M.symtab
    M.depword(S.heapend, heapend)
    M.depword(S.P0+x, pN)
    M.call(S.pXpastheap, R(x=x, y=0xAE, C=not carry))
    assert R(y=0xAE, C=carry) == M.regs

####################################################################
#   heapinit tests

@pytest.mark.parametrize('size', (
    0x004, # minimum heap size
    0x008, 0x010,
    0x0F8, 0x0FC, 0x100, 0x104, 0x108,
    0x4F8, 0x4FC, 0x500, 0x504, 0x508,
    0xEF00, # massive heap, most of memory
))
def test_heapinit(M, size):
    S = M.symtab
    start = 0x0FFC              # Ensure heap crosses a page
    setheap(M, start, len=size)
    M.call(S.heapinit)

    pos = 0; remain = size

    #   Max-size empty blocks on heap
    while remain >= 0x100:
        assert [HDT_FREE, 0xFE] == M.bytes(start+pos, 2), \
            'pos: {:04x}'.format(pos)
        pos    += 0x100
        remain -= 0x100

    #   Final remaining-size block on heap
    if remain > 0:
        assert [HDT_FREE, remain - 2] == M.bytes(start+pos, 2), \
            'pos: {:04x}'.format(pos)

    #   First free block object is at the start of the heap.
    assert start == M.word(S.heaplowat)

    #   Nothing other than free space on the heap.
    assert 0 == len(heapobjs(M, free=False))

@pytest.mark.parametrize('start, end', (
    (0x0FFF, 0x2000),
    (0x1001, 0x2000), (0x1002, 0x2000), (0x1003, 0x2000), (0x1005, 0x2000),
    (0x1000, 0x10FB),
    (0x1000, 0x10FD), (0x1000, 0x10FE), (0x1000, 0x10FF), (0x1000, 0x2001)
))
def test_heapinit_misaligned(M, start, end):
    ' Ensure that we BRK if a misaligned start or end value is given. '
    with pytest.raises(M.Abort):
        setheap(M, start, end=end, init=True)

####################################################################
#   splitfree tests

@pytest.mark.parametrize('allocsize, availsize, success_expected', (
    #   Sizes are a dword-aligned allocation size, including object header.
    (  4,   4, True),   # exact size block is unchanged
    ( 12,  12, True),
    (  4,  12, True),   # larger blocks are split
    ( 16, 252, True),
    ( 12,   4, False),  # fail if block is too small
    ( 16,  12, False),
    (252, 248, False),
))
def test_splitfree(M, allocsize, availsize, success_expected):
    S = M.symtab
    #   Make the initial block cross a page boundry if it's more than 4 bytes.
    start = 0x3FFC
    setheap(M, start, len=availsize)            # needed by heapobjs()

    M.deposit(start, [HDT_FREE, availsize-2])  # free block to (attempt to) split
    M.depword(S.P0, start)
    M.deposit(S.P0size, allocsize)

    print('before', heapobjs(M, free=True))
    M.call(S.splitfree, R(C=0 if success_expected else 1))
    print(' after', heapobjs(M, free=True))

    assert allocsize == M.byte(S.P0size)    # input params unchanged
    assert     start == M.word(S.P0)

    if not success_expected:
        assert [HDT_FREE, availsize-2] == M.bytes(start, 2)  # block unchanged
        assert R(C=0) == M.regs
    else:
        #   First block is now size requested
        assert [HDT_FREE, allocsize-2] == M.bytes(start, 2)
        if availsize > allocsize:
            #   Second block contains remaining free space
            assert [HDT_FREE, availsize-allocsize-2] \
                == M.bytes(start+allocsize, 2)
        assert R(C=1) == M.regs

####################################################################
#   mergefree tests

@pytest.mark.parametrize('endobj', (False, True))
@pytest.mark.parametrize('allocsize, availsizes, finalsizes, success_expected', (
    #   Sizes are a dword-aligned allocation size, including object header.
    #   Success via initial splitfree call.
    (  4, [4, 4],           [4, 4],                 True),
    (  8, [12, 4],          [8, 4, 4],              True),
    #   Success via merge.
    ( 12, [8, 4],           [12],                   True),
    ( 16, [12, 4, 4],       [16, 4],                True),
    ( 20, [8, 8, 4],        [20],                   True),
    ( 24, [8, 8, 16, 4],    [24, 8, 4],             True),
    #   Sum of two FBO dsizes > 256 should not cause problems.
    ( 28, [16, 0xFC],       [28, 0xF0],             True),
    #   Failure
    ( 32, [28],             [28],                   False),
    ( 36, [20, 4, 4, 4],    [32],                   False),
    #   XXX needs to test with full-size (hdsize=$FE) heapdata object?
    #   maybe not, since that has to be big enough for any allocation we
    #   want
))
def test_mergefree(M, allocsize, availsizes, finalsizes, endobj, success_expected):
    assert sum(availsizes) == sum(finalsizes)

    initobjs = [ (HDT_FREE, asize-2, asize-2) for asize in availsizes ]
    finalsizes2 = finalsizes.copy()     # pytest gets weird if you modify args
    if endobj:
        #   We end with an allocated object, rather than end of heap.
        initobjs.append((0x04, 0xAA, [0x08, 0xAB]))     # cons cell
        finalsizes2.append(4)                           # cons cell size

    start = 0x3FFC
    heapsize = buildheap(M, start, initobjs)
    #   An FBO after the heap to show that we're checking for end of heap.
    M.deposit(start+heapsize, [HDT_FREE, 0xFA])
    print('start+heapsize {:04X}'.format(start+heapsize))
    M.depword(M.symtab.P0, start)
    M.deposit(M.symtab.P0size, allocsize)

    print('before', heapobjs(M, free=True))
    M.call(M.symtab.mergefree, R(C=0 if success_expected else 1))
    objs = heapobjs(M, free=True)
    print(' after', objs)
    print('    P0 {:04X}'.format(M.word(M.symtab.P0)))
    print('    P3 {:04X}'.format(M.word(M.symtab.P3)))
    print('  [P3] ', M.bytes(M.word(M.symtab.P3), 4))

    expectedC = 1 if success_expected else 0
    actualC = M.regs.C
    assert (expectedC, finalsizes2) \
        == (actualC,   [ 4 if type == -1 else hdlen+2 for type, hdlen in objs ])

    #   XXX check again that removing end-of-heap-test in CUT fails test

####################################################################
#   allocn tests

@pytest.mark.parametrize('type', (
    0x02, 0x03, 0x04, 0x06, 0x07, 0x08, 0x0A,
    0xFC, 0xFE, 0xFF,
))
def test_allocn_badtype(M, type):
    setheap(M, 0x1000, end=0x2000, init=True)
    with pytest.raises(M.Abort):
        M.call(M.symtab.allocn, R(a=type, x=0))

@pytest.mark.parametrize('addr, objs', (
    #   see heaplen() for the object specification
    (0x10FC, [ ]),
    (0x20FC, [(0,0,2)]),
    (0x21FC, [(0,0,2)]*3),
    (0x30FC, [(TT,0,2), (TT,1,2), (TT,2,2),
        (TT,3,6), (TT,4,6), (TT,4,6), (TT,5,6), (TT,6,6), (TT,7,10)]),
    (0x33FC, [(TT,6,6), (TT,7,10), (TT,8,10), (TT,9,10), (TT,10,10)]),
    (0x34FC, [(TT,7,10), (0,0,2), (TT,9,10), (0xFF,0xFF,2), (TT,10,10), (0,0,2)]),
    (0x35FC, [(0,0,2), (TT,9,10), (0xFF,0xFF,2), (TT,10,10), (0,0,2), (TT,7,10)]),
    (0x40FC, [(TT,6,6), (0,0,2), (TT,0,2), (2,1,2)]),
))
def test_allocn_heapfull(M, addr, objs):
    S = M.symtab
    heaplen = buildheap(M, addr, objs)
    heapdata = M.bytes(addr, heaplen)
    M.call(S.allocn, R(a=0, x=0, C=0), trace=0)

    #   This is not required by the API, but if the internal counter does
    #   not equal the heap end at exit that shows where it failed.
    assert M.word(S.heapend) == M.word(S.P0)

    assert   R(C=1) == M.regs
    assert        0 == M.word(S.P1)
    assert heapdata == M.bytes(addr, heaplen)   # heap not changed

def test_allocn(M):
    S = M.symtab
    setheap(M, 0x1000, end=0x2000, init=True)
    assert     16 == len(heapobjs(M, free=True))
    assert 0x1000 == M.word(S.heaplowat)
    expected = []
    assert expected == heapobjs(M)

    #   Alloc a cons cell (4 bytes). The "type" byte is the LSB of the
    #   car, so not a valid heapdata type; it is initialized to 0 but
    #   expected to be filled in by the caller.
    M.call(S.allocn, R(a=0, x=0, C=1));  expected.append((0,4))
    assert R(C=0) == M.regs                 # returned success
    heaplowat = M.word(S.heaplowat)
    assert 0x1004 == heaplowat              # new free start is after cons cell
    assert HDT_FREE == M.byte(heaplowat)    # and is start of a free block
    assert expected == heapobjs(M)          # heap contains new cons cell

from    testmc.m6502 import  Machine, Registers as R
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

TT              = hdtype(63)    # used only by tests

def test_HDT_values(M):
    ''' Ensure this test code has defined with the same values all of
        the HDT_* constants defined in the assembly source.
    '''
    for name, value in M.symtab:
        if not name.startswith('HDT_'): continue
        assert globals()[name] == value, name

####################################################################
#   Test support

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
    M.depword(S.heapstart, start)
    M.depword(S.heapend, start + len(heapimage))
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
    M.depword(S.heapstart, start)
    M.depword(S.heapend, start + len(heapimage))
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
    M.depword(S.heapstart, start)
    M.depword(S.heapend, start + len(heapimage))
    M.deposit(start, heapimage)
    with pytest.raises(ValueError) as ex:
        heapobjs(M, data=True)
    assert ex.match(r'Invalid object type \$0[2367] in heap at \$0080')


####################################################################
#   Tests

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

    M.depword(S.heapstart, start)
    M.depword(S.heapend, start+size)
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
    assert start == M.word(S.heapff)

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
    S = M.symtab
    M.depword(S.heapstart, start)
    M.depword(S.heapend, end)
    with pytest.raises(M.Abort):
        M.call(S.heapinit)

''' Object Reference generator and decoder for clic.

    The constants and functions generate and consume 16-bit words as
    `int`s, usually to be deposited with `Machine.depword()` and read with
    `Machine.word()` which will handle converting the word to the correct
    endianness.

    Generally we order things in numerical order of tag:
    %00 pointer, const; %01 smallint; %10 sym12, sym1, sym2; %11 obdata
'''

__all__ = [
    'asbytes',                              #   Utility
    'isptr', 'isconst',                     #   Predicates
    'ptr', 'const', 'NIL', 'TRUE', 'FREE',  #   Construction
    'smallint', 'sym12', 'sym1', 'sym2',
    'hconslist',                            #   Inspection/Printing.
    'refstr', 'hconsdump', 'hconsprint',
]

#   We don't need all of testmc.generic.GenericMachine; any memory will do.
#   XXX MemoryAccess should be exported by testmc.generic.
#       That would fix this and mos65/machine.py:28.
from    testmc.generic.memory import MemoryAccess

####################################################################
#   Utility routines also for public consumption

def asbytes(seq):
    ' Whatever it is, make it into a `bytes` if we can. '
    try:
        return seq.encode('ASCII')
    except (AttributeError, TypeError):
        try:
            return bytes(seq)
        except TypeError:
            return bytes(list(seq))

####################################################################
#   Predicates.

def isptr(ref):     return ref & 0b11 == 0x00 and (ref>>8)  > 0x00
def isconst(ref):   return ref & 0b11 == 0x00 and (ref>>8) == 0x00

####################################################################
#   Construction.

def ptr(addr):  # tag %00
    ''' Construct reference: pointer to `addr`. This may not be used to
        create (intrinsic) const refs; use `const()` for that.

        If the tag (LSbits) is not %00 or the pointer is not in the
        range $0100 through $FFFC, a `ValueError` is raised.

        XXX This assumes a 16-bit address space. It's also not clear
        if not allowing creation of const pointers with this is good or
        inconvenient.
    '''
    if (addr < 0x0100) or (addr > 0xFFFF):  raise ValueError(
        f'pointer out of range: ${addr:04X}')
    tag = addr & 0x03
    if tag != 0:  raise ValueError(
        f'bad tag bits %{tag:02b} for pointer: ${addr:04X}')
    return addr


def const(n):   # tag %00
    ''' Construct reference: (intrinsic) const `n`.

        `n` includes the %00 tag bits. If the tag is not %00 or the
        constant is not in range, a `ValueError` is raised. The
        constants below should be used in preference to this.
    '''
    if (n < 0) or (n > 0xFF):  raise ValueError(
        f'Instrinsic const out of range: ${n:02X}')
    tag = n & 0x03
    if tag != 0:  raise ValueError(
        f'bad tag bits %{tag:02b} for const: ${n:02X}')
    return n

NIL     = const(0);     ' Const NIL or ().'
TRUE    = const(4);     ' Const TRUE.'
FREE    = const(0xCC);  ' Const for free heap cell.'

def smallint(i):    # tag %01
    ''' Given an integer between -8192 and 8191, convert it to a smallint
        object reference.
    '''
    if i > 8191 or i < -8192:
        raise ValueError(f'smallint out of range: {i}')
    if i < 0: i += 0x4000       # negative numbers → 2s complement
    return ((i << 2) | 0b01)

def sym12(sym):     # tag %10
    ''' Given a sequence of one or two characters, (anything that can be
        converted to `bytes`, using encoding ``ASCII`` if necessary),
        return a sym1 or sym2.
    '''
    sym =  _checksym(sym, [1,2])
    if   len(sym) == 1:     return sym1(sym)
    elif len(sym) == 2:     return sym2(sym)

def sym1(chars):        # tag %10
    ''' Given a sequence of one character (anything that can be converted
        to `bytes`, using encoding ``ASCII`` if necessary), return a sym1
        object reference.
    '''
    chars = _checksym(chars, [1])
    return ((chars[0] << 8) | 0b10000010)

def sym2(sym):      # tag %10
    ''' Given a sequence of two characters (anything that can be converted
        to `bytes`, using encoding ``ASCII`` if necessary), return a sym2
        object reference.
    '''
    sym = _checksym(sym, [2])
    if chr(sym[1]) in (' ', '`'):
        raise ValueError(f'sym2 2nd char cannot be space/backtick: {sym}')
    if sym[0] > 0x7F or sym[1] > 0x7F:
        raise ValueError(f'sym2 chars must be ≤ $7F: {sym}')
    msb = sym[0]
    if sym[1] & 0x40: msb |= 0x80    # copy sym0 bit 6 to MSB bit 7
    lsb = ((sym[1] & 0b00111111) << 2) | 0b10
    return ((msb << 8) | lsb)

def _checksym(seq, goodlen):
    if len(seq) not in goodlen:
        sgoodlen = ''.join(map(str, goodlen))
        raise ValueError(f'Bad sym{sgoodlen} length {len(seq)}: {seq}')
    return asbytes(seq)

####################################################################
#   Inspection/Printing.

def hconslist(m:MemoryAccess, ref, mapper=None):
    ''' Return an object representing the heap object at addr but using
        Python lists nested as necessary. `NIL` is returned as ``[]``.

        If `mapper` is given, non-pointer and non-NIL refs are mapped
        through that function. A typical use is ``mapper=refstr`` to get a
        debug display.
    '''
    if mapper is None:  mapper = lambda x: x
    if ref == NIL:      return []
    if not isptr(ref):  return mapper(ref)
    retval = []
    while True:
        car, cdr = m.words(ref, 2)
        retval.append(hconslist(m, car, mapper))
        if cdr == NIL:  break
        ref = cdr
    return retval

def refstr(word):
    ''' Return a printable string representing the ref: a pointer,
        smallint, sym1, sym2 or obdata header.

        For ease of columnar display this always returns an 8 character
        string padded with at least one space at the right. If you need to
        trim it down use `rstrip()`. (The minimum length is 3 for ``i:0``.)

        XXX See the test for documentation of the format.
    '''
    #   The longest representations are 7 chars: `o:00,FF` and `i:-8192`,
    #   which is where we get the 8-character length from.
    tag = word & 0x0003

    if   tag == 0b00:
        if word >= 0x100:  return f'p:{word:04X}  '         # pointer
        else:              return f'c:{_conststr(word)}    ' # const

    elif tag == 0b01:                                       # smallint
        value = word >> 2
        if value > 8191:  value -= 16384
        return f'i:{value:<5} '

    elif tag == 0b10:                                       # sym1/2
        msb = word >> 8; lsb = word & 0xFF
        if lsb == 0x82:     # sym1
            return f's:{_symcharstr(msb, 0)}    '
        else:               # sym2
            char2 = (lsb >> 2)
            if msb & 0x80:  char2 |= 0x40   # msb b7 is char2 b6
            return f's:{_symcharstr(msb & 0x7F, 0)}{_symcharstr(char2, 1)}  '

    elif tag == 0b11:                                       # obdata
        formatID = word & 0xFF
        odsize = word >> 8
        return f'o:{formatID:02X},{odsize:02X} '

    raise RuntimeError('INTERNAL ERROR')

_CONSTSTR_MAP = {
    0x00: '#n',
    0x04: '#t',
    0xCC: '--',
}
def _conststr(word):
    ''' Return a two-character string with a human-readable representation of
        the const represented by `word`. Throws a `RuntimeError` for
        invalid constants.
    '''
    s = _CONSTSTR_MAP.get(word)
    if s is not None:  return s
    if (word >= 0x100) or ((word & 0x03) != 0x00):
        raise RuntimeError(f'INTERNAL ERROR: bad value ${word:02X}')
    return f'{word:02X}'

def _symcharstr(char:int, pos:int) -> str:
    ''' Given an 8-bit `char` return a two-character string in a printable
        form. Non-printing chars print as a two-digit hex number; printing
        chars print as the char itself in the left-hand (`pos`=0) or
        right-hand (`pos`=1) position in the field, with the other position
        filled with an underscore ``_``.
    '''
    if char < ord('!') or char > ord('~'):
        return f'{char:02X}'
    if pos == 0:  return f'_{chr(char)}'
    else:         return f'{chr(char)}_'

def hconsdump(m:MemoryAccess, htop, ncells=None):
    ''' Given a cons heap starting below address `htop`, print in descending
        order one line per cons cell on the heap giving address, a hexdump
        of the four bytes (in native order) and `refstr()` output of the
        car and cdr cells.  If `ncells` is specified, print that many cells
        plus two more, otherwise print until two consecutive free cells
        (car and cdr are both the `FREE` constant) are printed.
    '''
    contig_free = 0
    addr = htop
    while True:
        addr -= 4
        if addr < 0:  raise RuntimeError('hconsdump() reached addr < 0')

        hex = m.hexdump(addr, 4)
        car, cdr = m.words(addr, 2)
        print(f'{hex}   {refstr(car)} {refstr(cdr)}'.rstrip())

        if ncells is not None:
            ncells -= 1
            if ncells <= -2:  return
        else:
            if (car, cdr) == (FREE, FREE):  contig_free += 1
            else:                           contig_free = 0
            if contig_free >= 2:            return

def _prin(*args):
    print(*args, sep='', end='')

def hconsprint(m:MemoryAccess, addr, depth=1):
    ''' Print the spine of the cons list starting at `addr`. If `depth` is
        greater than the default of ``1``, print on additional lines the
        spines of the sub-lists, recursing down to the given depth.

        If `addr` is not a pointer this will print, "----:" followed by the
        value.

        XXX Doesn't handle improper lists: dotted lists explode and
        circular lists loop forever.
    '''
    sublists = []

    if not isptr(addr):
        print(f'----: {refstr(addr).rstrip()}')
    else:
        _prin(f'{addr:04X}: [')
        while True:
            car, cdr = m.words(addr, 2)
            _prin(refstr(car).rstrip())
           #_prin(f'.{refstr(cdr).rstrip()}')
            if isptr(car):  sublists.append(car)
            if cdr != NIL:
                _prin(', ')
                addr = cdr
            else:
                print(']')
                break
        if depth > 1:
            for p in sublists:
                hconsprint(m, p, depth-1)

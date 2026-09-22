''' Object Reference generator and decoder for clic.

    The constants and functions generate and consume 16-bit words as
    `int`s, usually to be deposited with `Machine.depword()` and read with
    `Machine.word()` which will handle converting the word to the correct
    endianness.
'''

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
#   Constructing

####################################################################
#   Intrinsic constants

def const(n):
    ''' Return the object reference for intrinsic constant `n`.

        This takes the value _including_ the %00 tag in the LSbits.
        If the tag is not %00 or the constant is not in range, a
        `ValueError` is raised.
    '''
    if (n < 0) or (n > 0xFF):  raise ValueError(
        f'Instrinsic const out of range: ${n:02X}')
    tag = n & 0x03
    if tag != 0:  raise ValueError(
        f'bad tag bits %{tag:02b} for intrinsic const: ${n:02X}')
    return n

NIL     = const(0);     ' Intrinsic constant NIL.'
T       = const(4);     ' Intrinsic constant TRUE.'

####################################################################
#   Pointers

def ptr(addr):
    ''' Return pointer to `addr`. This may not be used to create
        "intrinsic constant" pointers.

        If the tag (LSbits) is not %00 or the pointer is not in the
        range $0100 through $FFFC, a `ValueError` is raised.

        XXX This assumes a 16-bit address space. It's also not clear
        if not allowing creation of intrinsic constant pointers with
        this is good or inconvenient.
    '''
    if (addr < 0x0100) or (addr > 0xFFFF):  raise ValueError(
        f'pointer out of range: ${addr:04X}')
    tag = addr & 0x03
    if tag != 0:  raise ValueError(
        f'bad tag bits %{tag:02b} for pointer: ${addr:04X}')
    return addr

####################################################################
#   Short symbols

def _checksym(seq, goodlen):
    if len(seq) not in goodlen:
        sgoodlen = ''.join(map(str, goodlen))
        raise ValueError(f'Bad sym{sgoodlen} length {len(seq)}: {seq}')
    return asbytes(seq)

def sym1(chars):
    ''' Given a sequence of one character (anything that can be converted
        to `bytes`, using encoding ``ASCII`` if necessary), return a sym1
        object reference.
    '''
    chars = _checksym(chars, [1])
    return ((chars[0] << 8) | 0b10000010)

def sym2(sym):
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

def sym12(sym):
    ''' Given a sequence of one or two characters, (anything that can be
        converted to `bytes`, using encoding ``ASCII`` if necessary),
        return a sym1 or sym2.
    '''
    sym =  _checksym(sym, [1,2])
    if   len(sym) == 1:     return sym1(sym)
    elif len(sym) == 2:     return sym2(sym)

####################################################################
#   Smallints

def smallint(i):
    ''' Given an integer between -8192 and 8191, convert it to a smallint
        object reference.
    '''
    if i > 8191 or i < -8192:
        raise ValueError(f'smallint out of range: {i}')
    if i < 0: i += 0x4000       # negative numbers → 2s complement
    return ((i << 2) | 0b01)

####################################################################
#   Inspecting/Printing

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
        else:              return f'c:{conststr(word)}    ' # intrinsic const

    elif tag == 0b01:                                       # smallint
        value = word >> 2
        if value > 8191:  value -= 16384
        return f'i:{value:<5} '

    elif tag == 0b10:                                       # sym1/2
        msb = word >> 8; lsb = word & 0xFF
        if lsb == 0x82:     # sym1
            return f's:{symcharstr(msb, 0)}    '
        else:               # sym2
            char2 = (lsb >> 2)
            if msb & 0x80:  char2 |= 0x40   # msb b7 is char2 b6
            return f's:{symcharstr(msb & 0x7F, 0)}{symcharstr(char2, 1)}  '

    elif tag == 0b11:                                       # obdata
        formatID = word & 0xFF
        odsize = word >> 8
        return f'o:{formatID:02X},{odsize:02X} '

    raise RuntimeError('INTERNAL ERROR')

CONSTSTR_MAP = {
    0x00: '#n',
    0x04: '#t',
    0xCC: '--',
}
def conststr(word):
    ''' Return a two-character string with a human-readable representation of
        the intrinsic constant represented by `word`. Throws a `RuntimeError`
        for invalid constants.
    '''
    s = CONSTSTR_MAP.get(word)
    if s is not None:  return s
    if (word >= 0x100) or ((word & 0x03) != 0x00):
        raise RuntimeError(f'INTERNAL ERROR: bad value ${word:02X}')
    return f'{word:02X}'

def symcharstr(char:int, pos:int) -> str:
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

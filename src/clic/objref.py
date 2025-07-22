''' Object Reference generator for clic.

    These constants and functions generate 16-bit words as `int`s, usually
    to be deposited with `Machine.depword()` which will handle converting
    the word to the correct endianness.
'''

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
    try:
        return seq.encode('ASCII')
    except (AttributeError, TypeError):
        try:
            return bytes(seq)
        except TypeError:
            return bytes(list(seq))

def sym1(chars):
    ''' Given a sequence of one character (anything that can be converted
        to `bytes`, using encoding ``ASCII`` if necessary), return a sym1
        object reference.
    '''
    chars = _checksym(chars, [1])
    return ((chars[0] << 8) | 0b00000010)

def sym2(sym):
    ''' Given a sequence of two characters (anything that can be converted
        to `bytes`, using encoding ``ASCII`` if necessary), return a sym2
        object reference.

        Note that with a sym2 the MSB contains the second char, not the first.
    '''
    sym = _checksym(sym, [2])
    if sym[0] == 0x00:
        raise ValueError(f'sym2 1st char cannot be $00: {sym}')
    if sym[0] > 0x7F or sym[1] > 0x7F:
        raise ValueError(f'sym2 chars must be ≤ $7F: {sym}')
    msb = sym[1]
    if sym[0] & 0x40: msb |= 0x80    # copy sym0 bit 6 to MSB bit 7
    lsb = (sym[0] << 2) & 0xFC | 0b10
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



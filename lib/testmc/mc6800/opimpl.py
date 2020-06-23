''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing to its opcode. The function is responsible
    for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

from struct import unpack

####################################################################
#   Tests of values for setting flags (HINZVC)

def isnegative(b):
    return 0 != b & 0b10000000

def iszero(b):
    return b == 0

def incword(word, addend):
    ''' Return 16-bit `word` incremented by `addend` (which may be negative).
        This returns a 16-bit unsigned result, wrapping at $FFFF/$0000.
    '''
    return (word + addend) & 0xFFFF

def readbyte(m):
    ' Consume a byte at [PC] and return it. '
    val = m.byte(m.pc)
    m.pc = incword(m.pc, 1)
    return val

def readsignedbyte(m):
    ' Consume a byte at [PC] as a signed value and return it. '
    val = unpack('b', m.bytes(m.pc, 1))[0]
    m.pc = incword(m.pc, 1)
    return val

def readword(m):
    ' Consume a word at [PC] and return it. '
    # Careful! PC may wrap between bytes.
    return (readbyte(m) << 8) | readbyte(m)

def readindex(m):
    ''' Consume an unsigned offset byte at [PC], add it to the X register
        contents and return the result.
    '''
    return incword(m.x, readbyte(m))

def readreloff(m):
    ''' Consume a signed relative offset byte at [PC] and return the
        target address. '''
    offset = readsignedbyte(m)
    return incword(m.pc, offset)

def popword(m):
    ' Pop a word off the stack and return it. '
    m.sp = incword(m.sp, 1)
    msb = m.byte(m.sp)
    m.sp = incword(m.sp, 1)
    lsb = m.byte(m.sp)
    return (msb << 8) + lsb

def pushword(m, word):
    ' Push a word on to the stack, LSB followed by MSB. '
    m.deposit(m.sp, word & 0xFF)
    m.sp = incword(m.sp, -1)
    m.deposit(m.sp, word >> 8)
    m.sp = incword(m.sp, -1)

####################################################################
#   Opcode implementations

def nop(m):
    readbyte(m)

def bra(m):
    readbyte(m)
    m.pc = readreloff(m)

def rts(m):
    m.pc = popword(m)

def jmpx(m):
    readbyte(m)
    m.pc = readindex(m)

def jmp(m):
    readbyte(m)
    m.pc = readword(m)

def ldaa(m):
    readbyte(m)
    m.a = readbyte(m)
    m.N = isnegative(m.a)
    m.Z = iszero(m.a)
    m.V = False

def bsr(m):
    readbyte(m)
    target = readreloff(m)
    pushword(m, m.pc)
    m.pc = target

def jsrx(m):
    readbyte(m)
    target = readindex(m)
    pushword(m, m.pc)
    m.pc = target

def jsr(m):
    readbyte(m)
    target = readword(m)
    pushword(m, m.pc)
    m.pc = target

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
    ' Read the byte at the PC and increment the PC past it. '
    val = m.byte(m.pc)
    m.pc = incword(m.pc, 1)
    return val

def readsignedbyte(m):
    ' Read the byte at the PC as a signed value and increment the PC past it. '
    val = unpack('b', m.bytes(m.pc, 1))[0]
    m.pc = incword(m.pc, 1)
    return val

def readword(m):
    ' Read the word at the PC and increment the PC past it. '
    # Careful! PC may wrap between bytes.
    return (readbyte(m) << 8) | readbyte(m)

def readindex(m):
    ' Read a byte offset and return it added to the X register contents. '
    return incword(m.x, readbyte(m))

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
    relfrom = m.pc + 2
    readbyte(m)
    m.pc = incword(relfrom, readsignedbyte(m))

def rts(m):
    m.pc = popword(m)

def jmpx(m):
    readbyte(m)
    m.pc = readindex(m)

def jmp(m):
    readbyte(m)
    m.pc = readword(m)

def ldaa(m):
    m.a = m.byte(m.pc+1)
    m.N = isnegative(m.a)
    m.Z = iszero(m.a)
    m.V = False
    m.pc = incword(m.pc, 2)

def bsr(m):
    relfrom = m.pc + 2
    readbyte(m)
    target = incword(relfrom, readsignedbyte(m))
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

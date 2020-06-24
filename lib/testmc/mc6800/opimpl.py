''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing the byte after the opcode. The function is
    responsible for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

from struct import unpack

####################################################################
#   Values tests for setting flags (HINZVC)

def isnegative(b):
    return 0 != b & 0b10000000

def iszero(b):
    return b == 0

####################################################################
#   Address handling, reading data at the PC, reading/writing stack

def incbyte(byte, addend):
    ''' Return 8-bit `byte` incremented by `addend` (which may be negative).
        This returns an 8-bit unsigned result, wrapping at $FF/$00.
    '''
    return (byte + addend) & 0xFF

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
#   Flag handling

def logicNZV(m, val):
    ''' Set N, Z and V flags based on `val`, and return `val`.
        This is used for loads and logic operations.
    '''
    m.N = isnegative(val)
    m.Z = iszero(val)
    m.V = False
    return val

####################################################################
#   Opcode implementations

def nop(m):
    pass

def bra(m):
    m.pc = readreloff(m)

def rts(m):
    m.pc = popword(m)

def jmpx(m):
    m.pc = readindex(m)

def jmp(m):
    m.pc = readword(m)

def anda(m):
    m.a = logicNZV(m, m.a & readbyte(m))

def ldaa(m):
    m.a = logicNZV(m, readbyte(m))

def bsr(m):
    target = readreloff(m)
    pushword(m, m.pc)
    m.pc = target

def jsrx(m):
    target = readindex(m)
    pushword(m, m.pc)
    m.pc = target

def jsr(m):
    target = readword(m)
    pushword(m, m.pc)
    m.pc = target

####################################################################
#   Arithmetic opcodes

def addHNZVC(m, augend, addend):
    ''' Return the modular 8-bit sum of adding without carry `addend` (the
        operand) to `augend` (the contents of the register). Set H, N, Z, V
        and C flags based on the result, per pages A-4 (ADC) and A-5 (ADD)
        in the PRG.
    '''
    sum = incbyte(augend, addend)

    m.N = isnegative(sum)
    m.Z = iszero(sum)

    bit7 = 0b10000000;              bit3 = 0b1000
    x7 = bool(augend & bit7);       x3 = bool(augend & bit3)
    m7 = bool(addend & bit7);       m3 = bool(addend & bit3)
    r7 = bool(sum & bit7);          r3 = bool(sum & bit3)

    #   The following is copied directly from PRG pages A-4 and A-5.
    m.C = x7 and m7  or  m7 and not r7  or  not r7 and x7
    m.H = x3 and m3  or  m3 and not r3  or  not r3 and x3
    m.V = x7 and m7 and not r7  or  not x7 and not m7 and r7

    return sum

def adda(m):
    m.a = addHNZVC(m, m.a, readbyte(m))

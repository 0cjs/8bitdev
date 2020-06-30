''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing the byte after the opcode. The function is
    responsible for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

from struct import unpack

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

def readreloff(m):
    ''' Consume a signed relative offset byte at [PC] and return the
        target address. '''
    offset = readsignedbyte(m)
    return incword(m.pc, offset)

def readindex(m):
    ''' Consume an unsigned offset byte at [PC], add it to the X register
        contents and return the result.
    '''
    return incword(m.x, readbyte(m))

def popbyte(m):
    ' Pop a byte off the stack and return it. '
    m.sp = incword(m.sp, 1)
    return m.byte(m.sp)

def popword(m):
    ' Pop a word off the stack and return it. '
    msb = popbyte(m)
    lsb = popbyte(m)
    return (msb << 8) + lsb

def pushbyte(m, byte):
    ' Push a byte on to the stack. '
    m.deposit(m.sp, byte)
    m.sp = incword(m.sp, -1)

def pushword(m, word):
    ' Push a word on to the stack, LSB followed by MSB. '
    pushbyte(m, word & 0xFF)
    pushbyte(m, word >> 8)

####################################################################
#   Branches

def jmp(m):     m.pc = readword(m)
def jmpx(m):    m.pc = readindex(m)
def bra(m):     m.pc = readreloff(m)

def branchif(m, predicate):
    target = readreloff(m)
    if predicate:
        m.pc = target

def beq(m): branchif(m, m.Z)
def bmi(m): branchif(m, m.N)

def jsr(m):     t = readword(m);    pushword(m, m.pc); m.pc = t
def jsrx(m):    t = readindex(m);   pushword(m, m.pc); m.pc = t
def bsr(m):     t = readreloff(m);  pushword(m, m.pc); m.pc = t

def rts(m):     m.pc = popword(m)

####################################################################
#   Data movement

def pula(m):    m.a = popbyte(m)
def psha(m):    pushbyte(m, m.a)

def ldaa(m):    m.a = logicNZV(m, readbyte(m))
def ldaam(m):   m.a = logicNZV(m, m.mem[readword(m)])
def ldx(m):     m.x = logicNZV(m, readword(m), signbit=15)

def clrx(m):    m.mem[readindex(m)] = logicNZV(m, 0); m.C = 0
def staa_m(m):  m.mem[readword(m)] = logicNZV(m, m.a)
def staax(m):   m.mem[readindex(m)] = logicNZV(m, m.a)

####################################################################
#   Flag handling for data movement and logic

def isneg(b, signbit=7):
    sign = b & (1 << signbit)
    return 0 !=  sign

def iszero(b):
    return b == 0

def logicNZV(m, val, signbit=7):
    ''' Set N, Z and V flags based on `val`, and return `val`.
        This is used for data transfer and logic operations.
    '''
    m.N = isneg(val, signbit=signbit)
    m.Z = iszero(val)
    m.V = False
    return val

####################################################################
#   Logic operations

def anda(m):
    m.a = logicNZV(m, m.a & readbyte(m))

def lsra(m):
    m.C = m.a & 1
    m.a = m.a >> 1
    m.N = isneg(m.a)
    m.Z = iszero(m.a)
    #   V is actually N⊕C, which is meaningless for right shifts
    #   but with ASL means "the sign has changed."
    m.V = m.C

####################################################################
#   Arithmetic operations

def inx(m):     m.x = incword(m.x, 1); m.Z = iszero(m.x)

def addHNZVC(m, augend, addend):
    ''' Return the modular 8-bit sum of adding without carry `addend` (the
        operand) to `augend` (the contents of the register). Set H, N, Z, V
        and C flags based on the result, per pages A-4 (ADC) and A-5 (ADD)
        in the PRG.
    '''
    sum = incbyte(augend, addend)

    m.N = isneg(sum)
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

def subNZVC(m, minuend, subtrahend):
    difference = incbyte(minuend, -subtrahend)
    m.N = isneg(difference)
    m.Z = iszero(difference)

    bit7 = 0b10000000;              bit3 = 0b1000
    x7 = bool(minuend & bit7);      x3 = bool(minuend & bit3)
    m7 = bool(subtrahend & bit7);   m3 = bool(subtrahend & bit3)
    r7 = bool(difference & bit7);   r3 = bool(difference & bit3)
    #   The following is copied pretty much directly from the PRG,
    #   page A-31 (CMP).
    m.C = (not x7 and m7) or (m7 and r7) or (r7 and not x7)
    m.V = (x7 and not m7 and not r7) or (not x7 and m7 and r7)

    return difference

def suba(m):
    m.a = subNZVC(m, m.a, readbyte(m))

def cmpa(m):
    subNZVC(m, m.a, readbyte(m))

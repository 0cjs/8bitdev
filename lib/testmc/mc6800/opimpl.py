''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing the byte after the opcode. The function is
    responsible for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

from struct import unpack

class InvalidOpcode(RuntimeError):
    ''' Since it is designed for testing code, the simulator
        will not execute invalid opcodes, instead raising an exception.
    '''
    def __init__(self, opcode, pc):
        self.opcode = opcode
        self.pc = pc
        super().__init__('opcode=${:02X} pc=${:04X}'.format(opcode, pc))

def invalid(m):
    raise InvalidOpcode(m.mem[incword(m.pc, -1)], m.pc-1)

####################################################################
#   Address handling, reading data at the PC

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

def signedbyteat(m, addr):
    ' Return the byte at `addr` as a signed value. '
    return unpack('b', m.bytes(addr, 1))[0]

def readsignedbyte(m):
    ' Consume a byte at [PC] as a signed value and return it. '
    val = signedbyteat(m, m.pc)
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

####################################################################
#   Branches

def jmp(m):     m.pc = readword(m)
def jmpx(m):    m.pc = readindex(m)

def branchif(m, predicate):
    target = readreloff(m)
    if predicate:
        m.pc = target

def bra(m): branchif(m, True)
def bcc(m): branchif(m, not m.C)
def bcs(m): branchif(m, m.C)
def bvc(m): branchif(m, not m.V)
def bvs(m): branchif(m, m.V)
def beq(m): branchif(m, m.Z)
def bne(m): branchif(m, not m.Z)
def bmi(m): branchif(m, m.N)
def bpl(m): branchif(m, not m.N)

####################################################################
#   Instructions affecting the stack

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


def jsr(m):     t = readword(m);    pushword(m, m.pc); m.pc = t
def jsrx(m):    t = readindex(m);   pushword(m, m.pc); m.pc = t
def bsr(m):     t = readreloff(m);  pushword(m, m.pc); m.pc = t
def rts(m):     m.pc = popword(m)

def pula(m):    m.a = popbyte(m)
def pulb(m):    m.b = popbyte(m)
def psha(m):    pushbyte(m, m.a)
def pshb(m):    pushbyte(m, m.b)

####################################################################
#   Flag Changes

def clv(m): setattr(m, 'V', 0)
def sev(m): setattr(m, 'V', 1)
def clc(m): setattr(m, 'C', 0)
def sec(m): setattr(m, 'C', 1)
def cli(m): setattr(m, 'I', 0)
def sei(m): setattr(m, 'I', 1)

def tap(m):
    m.H = bool(m.a & 32)
    m.I = bool(m.a & 16)
    m.N = bool(m.a & 8)
    m.Z = bool(m.a & 4)
    m.V = bool(m.a & 2)
    m.C = bool(m.a & 1)

def tpa(m):
    m.a = 0b11000000 \
        | (m.H << 5) \
        | (m.I << 4) \
        | (m.N << 3) \
        | (m.Z << 2) \
        | (m.V << 1) \
        | (m.C << 0) \
        | 0

####################################################################
#   Data movement

def tab(m):     m.b = logicNZV(m, m.a)
def tba(m):     m.a = logicNZV(m, m.b)

def ldaa(m):    m.a = logicNZV(m, readbyte(m))
def ldab(m):    m.b = logicNZV(m, readbyte(m))
def ldaaz(m):   m.a = logicNZV(m, m.mem[readbyte(m)])
def ldabz(m):   m.b = logicNZV(m, m.mem[readbyte(m)])
def ldaam(m):   m.a = logicNZV(m, m.mem[readword(m)])
def ldabm(m):   m.b = logicNZV(m, m.mem[readword(m)])
def ldaax(m):   m.a = logicNZV(m, m.mem[readindex(m)])
def ldabx(m):   m.b = logicNZV(m, m.mem[readindex(m)])

def ldx(m):     m.x = logicNZV(m, readword(m), signbit=15)
def ldxtarget(m, loc0):
    loc1 = incword(loc0, 1)
    val  = (m.mem[loc0] << 8) | m.mem[loc1]
    m.x = logicNZV(m, val, signbit=15)
def ldxz(m):    ldxtarget(m, readbyte(m))
def ldxm(m):    ldxtarget(m, readword(m))
def ldxx(m):    ldxtarget(m, readindex(m))

def clra(m):    m.a                 = logicNZV(m, 0); m.C = 0
def clrb(m):    m.b                 = logicNZV(m, 0); m.C = 0
def clrm(m):    m.mem[readword(m)]  = logicNZV(m, 0); m.C = 0
def clrx(m):    m.mem[readindex(m)] = logicNZV(m, 0); m.C = 0

def staaz(m):   m.mem[readbyte(m)]  = logicNZV(m, m.a)
def staam(m):   m.mem[readword(m)]  = logicNZV(m, m.a)
def staax(m):   m.mem[readindex(m)] = logicNZV(m, m.a)

def stabz(m):   m.mem[readbyte(m)]  = logicNZV(m, m.b)
def stabm(m):   m.mem[readword(m)]  = logicNZV(m, m.b)
def stabx(m):   m.mem[readindex(m)] = logicNZV(m, m.b)

def stxtarget(m, target0):
    target1 = incword(target0, 1)
    m.mem[target0] = m.x >> 8
    m.mem[target1] = m.x & 0xFF
    m.N = isneg(m.x, signbit=15)
    m.Z = iszero(m.x)
    m.V = 0

def stxz(m):    stxtarget(m, readbyte(m))
def stxm(m):    stxtarget(m, readword(m))

def tsx(m):     m.x = m.sp
def txs(m):     m.sp = m.x

####################################################################
#   Flag handling for data movement and logic

def isneg(b, signbit=7):
    sign = b & (1 << signbit)
    return 0 !=  sign

def iszero(b):
    return b == 0

def updateNZ(m, val, signbit=7):
    ' Set N and Z flags based on `val`, and return `val`. '
    m.N = isneg(val, signbit=signbit)
    m.Z = iszero(val)
    return val

def logicNZV(m, val, signbit=7):
    ''' Clear V flag and return `updateNZ()` for `val`.
        This is used for data transfer and logic operations.
    '''
    m.V = False
    return updateNZ(m, val, signbit=signbit)

####################################################################
#   Logic operations

def com(m, val): m.V = 0; m.C = 1; return updateNZ(m, val ^ 0xFF)
def coma(m):                            m.a = com(m, m.a)
def comb(m):                            m.b = com(m, m.b)
def comm(m): loc = readword(m);  m.mem[loc] = com(m, m.mem[loc])
def comx(m): loc = readindex(m); m.mem[loc] = com(m, m.mem[loc])

def anda(m):    m.a = logicNZV(m, m.a & readbyte(m))
def andaz(m):   m.a = logicNZV(m, m.a & m.mem[readbyte(m)])
def andam(m):   m.a = logicNZV(m, m.a & m.mem[readword(m)])
def andax(m):   m.a = logicNZV(m, m.a & m.mem[readindex(m)])
def andb(m):    m.b = logicNZV(m, m.b & readbyte(m))
def andbz(m):   m.b = logicNZV(m, m.b & m.mem[readbyte(m)])
def andbm(m):   m.b = logicNZV(m, m.b & m.mem[readword(m)])
def andbx(m):   m.b = logicNZV(m, m.b & m.mem[readindex(m)])

def oraa(m):    m.a = logicNZV(m, m.a | readbyte(m))
def oraaz(m):   m.a = logicNZV(m, m.a | m.mem[readbyte(m)])
def oraam(m):   m.a = logicNZV(m, m.a | m.mem[readword(m)])
def oraax(m):   m.a = logicNZV(m, m.a | m.mem[readindex(m)])
def orab(m):    m.b = logicNZV(m, m.b | readbyte(m))
def orabz(m):   m.b = logicNZV(m, m.b | m.mem[readbyte(m)])
def orabm(m):   m.b = logicNZV(m, m.b | m.mem[readword(m)])
def orabx(m):   m.b = logicNZV(m, m.b | m.mem[readindex(m)])

def eora(m):    m.a = logicNZV(m, m.a ^ readbyte(m))
def eoraz(m):   m.a = logicNZV(m, m.a ^ m.mem[readbyte(m)])
def eoram(m):   m.a = logicNZV(m, m.a ^ m.mem[readword(m)])
def eorax(m):   m.a = logicNZV(m, m.a ^ m.mem[readindex(m)])
def eorb(m):    m.b = logicNZV(m, m.b ^ readbyte(m))
def eorbz(m):   m.b = logicNZV(m, m.b ^ m.mem[readbyte(m)])
def eorbm(m):   m.b = logicNZV(m, m.b ^ m.mem[readword(m)])
def eorbx(m):   m.b = logicNZV(m, m.b ^ m.mem[readindex(m)])

####################################################################
#   Shifts and Rotates

def shiftflags(m, newC, val):
    m.Z = iszero(val)
    m.N = isneg(val)
    m.C = bool(newC)
    m.V = m.N ^ m.C
    return val

#                                      new carry    shifted/rotated value
def asl(m, arg): return shiftflags(m,  arg & 0x80,  (arg << 1) & 0xFF         )
def rol(m, arg): return shiftflags(m,  arg & 0x80,  (arg << 1) & 0xFF | m.C   )
def lsr(m, arg): return shiftflags(m,  arg & 1,     (arg >> 1)                )
def asr(m, arg): return shiftflags(m,  arg & 1,     (arg >> 1) | (arg & 0x80) )
def ror(m, arg): return shiftflags(m,  arg & 1,     (arg >> 1) | (m.C << 7)   )

def asla(m):                            m.a = asl(m, m.a)
def aslb(m):                            m.b = asl(m, m.b)
def aslm(m): loc = readword(m);  m.mem[loc] = asl(m, m.mem[loc])
def aslx(m): loc = readindex(m); m.mem[loc] = asl(m, m.mem[loc])

def rola(m):                            m.a = rol(m, m.a)
def rolb(m):                            m.b = rol(m, m.b)
def rolm(m): loc = readword(m);  m.mem[loc] = rol(m, m.mem[loc])
def rolx(m): loc = readindex(m); m.mem[loc] = rol(m, m.mem[loc])

def lsra(m):                            m.a = lsr(m, m.a)
def lsrb(m):                            m.b = lsr(m, m.b)
def lsrm(m): loc = readword(m);  m.mem[loc] = lsr(m, m.mem[loc])
def lsrx(m): loc = readindex(m); m.mem[loc] = lsr(m, m.mem[loc])

def asra(m):                            m.a = asr(m, m.a)
def asrb(m):                            m.b = asr(m, m.b)
def asrm(m): loc = readword(m);  m.mem[loc] = asr(m, m.mem[loc])
def asrx(m): loc = readindex(m); m.mem[loc] = asr(m, m.mem[loc])

def rora(m):                            m.a = ror(m, m.a)
def rorb(m):                            m.b = ror(m, m.b)
def rorm(m): loc = readword(m);  m.mem[loc] = ror(m, m.mem[loc])
def rorx(m): loc = readindex(m); m.mem[loc] = ror(m, m.mem[loc])

####################################################################
#   Arithmetic operations

def neg(m, arg):
    m.V = arg == 0x80
    m.C = arg != 0x00
    return updateNZ(m, ((arg^0xFF) + 1) & 0xFF)
def nega(m):                            m.a = neg(m, m.a)
def negb(m):                            m.b = neg(m, m.b)
def negm(m): loc = readword(m);  m.mem[loc] = neg(m, m.mem[loc])
def negx(m): loc = readindex(m); m.mem[loc] = neg(m, m.mem[loc])

def inc(m, val):
    m.V = val == 0x7F
    return updateNZ(m, (val+1)&0xFF)
def inca(m):                            m.a = inc(m, m.a)
def incb(m):                            m.b = inc(m, m.b)
def incm(m): loc = readword(m);  m.mem[loc] = inc(m, m.mem[loc])
def incx(m): loc = readindex(m); m.mem[loc] = inc(m, m.mem[loc])

def dec(m, val):
    m.V = val == 0x80
    return updateNZ(m, (val-1)&0xFF)
def deca(m):                            m.a = dec(m, m.a)
def decb(m):                            m.b = dec(m, m.b)
def decm(m): loc = readword(m);  m.mem[loc] = dec(m, m.mem[loc])
def decx(m): loc = readindex(m); m.mem[loc] = dec(m, m.mem[loc])

def inx(m):     m.x = incword(m.x, 1);  m.Z = iszero(m.x)
def dex(m):     m.x = incword(m.x, -1); m.Z = iszero(m.x)

def ins(m):     m.sp = incword(m.sp, 1)
def des(m):     m.sp = incword(m.sp, -1)

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

def subNZVC(m, minuend, subtrahend, affectC=True):
    difference = incbyte(minuend, -subtrahend)
    m.N = isneg(difference)
    m.Z = iszero(difference)

    bit7 = 0b10000000;              bit3 = 0b1000
    x7 = bool(minuend & bit7);      x3 = bool(minuend & bit3)
    m7 = bool(subtrahend & bit7);   m3 = bool(subtrahend & bit3)
    r7 = bool(difference & bit7);   r3 = bool(difference & bit3)
    #   The following is copied pretty much directly from the PRG,
    #   page A-31 (CMP).
    if affectC:
        m.C = (not x7 and m7) or (m7 and r7) or (r7 and not x7)
    m.V = (x7 and not m7 and not r7) or (not x7 and m7 and r7)

    return difference

def suba(m):
    m.a = subNZVC(m, m.a, readbyte(m))

def cmpa(m):
    subNZVC(m, m.a, readbyte(m))

def cpxarg(m, argh, argl):
    xh,     xl =    m.x >> 8,  m.x & 0xFF
    subNZVC(m, xl, argl, affectC=False)
    Zl = m.Z
    subNZVC(m, xh, argh, affectC=False)
    m.Z = Zl and m.Z

def cpx(m):
    argh, argl = readbyte(m), readbyte(m)
    cpxarg(m, argh, argl)

def cpxz(m):
    target = readbyte(m)
    argh, argl = m.mem[target], m.mem[incword(target, 1)]
    cpxarg(m, argh, argl)

def cpxm(m):
    target = readword(m)
    argh, argl = m.mem[target], m.mem[incword(target, 1)]
    cpxarg(m, argh, argl)

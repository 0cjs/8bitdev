''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing the byte after the opcode. The function is
    responsible for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

from struct import unpack


####################################################################

class InvalidOpcode(RuntimeError):
    ''' Since it is designed for testing code, the simulator
        will not execute invalid opcodes, instead raising an exception.
    '''
    def __init__(self, opcode, regs):
        self.opcode = opcode; self.regs = regs
        super().__init__('op=${:02X}, {}'.format(opcode, regs))

def invalid(m):
    #   The PC PC has already been advanced past the opcode; undo this.
    pc = incword(m.pc, -1)
    regs = m.regs.clone(pc=pc)
    raise InvalidOpcode(m.mem[pc], regs)

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

#   Unsigned comparisons after CMP/SUB/CBA/SBA.
def bhi(m): branchif(m, not m.C and not m.Z)
def bls(m): branchif(m, m.C or m.Z)

#   Signed comparisons after CMP/SUB/CBA/SBA.
def blt(m): branchif(m, m.N ^ m.V)
def ble(m): branchif(m, m.Z or (m.N ^ m.V))
def bge(m): branchif(m, not (m.N ^ m.V))
def bgt(m): branchif(m, not m.Z and not (m.N ^ m.V))
#
#   Definitions from the MC6800 Programmer's Reference Manual:
#
#   blt(m): branchif(m, (m.N and not m.V) or (not m.N and m.V))
#   ble(m): branchif(m, m.Z or ((m.N and not m.V) or (not m.N and m.V)))
#   bge(m): branchif(m, (m.N and m.V) or (not m.N and not m.V))
#   bgt(m): branchif(m, not m.Z and ((m.N and m.V) or (not m.N and not m.V)))


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

def rti(m):
    flags = popbyte(m)
    #   This code is deliberately independent of the Registers object
    #   to help cross-test, as well as for clarity.
    m.H  = bool(flags & 0b00100000); m.I  = bool(flags & 0b00010000)
    m.N  = bool(flags & 0b00001000); m.Z  = bool(flags & 0b00000100)
    m.V  = bool(flags & 0b00000010); m.C  = bool(flags & 0b00000001)

    m.b  = popbyte(m)
    m.a  = popbyte(m)
    m.x  = popword(m)
    m.pc = popword(m)

def swi(m):
    ''' The definition of SWI is that it should set the PC to the address
        at (n-5), "where n is the address corresponding to a high state on
        all lines of the address bus." (PRM p.100) This should be kept in
        mind if we introduce emulation of CPUs with <16-bit address buses,
        though the implementation should still be fine so long as the high
        bits are ignored.
    '''
    #   In the PRM this instruction, unlike the others excepting JSR,
    #   explicitly shows the PC being incremented past the instruction: "PC
    #   ← (PC) + 0001". Presumably it shows it here but not elsewhere just
    #   to make clear which PC value is being pushed on the stack.
    pushword(m, m.pc)
    pushword(m, m.x)
    pushbyte(m, m.a)
    pushbyte(m, m.b)
    pushbyte(m, 1 << 7 | 1 << 6 \
                | m.H << 5 | m.I << 4 | m.N << 3 | m.Z << 2 | m.V << 1 | m.C)

    swivec = 0xFFFF - 5             # PRM definition for 16-bit address bus
    m.pc = m.word(swivec)
    m.I = True

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

def ld16target(m, loc0):
    loc1 = incword(loc0, 1)
    val  = (m.mem[loc0] << 8) | m.mem[loc1]
    return logicNZV(m, val, signbit=15)

def ldx(m):     m.x = logicNZV(m, readword(m), signbit=15)
def ldxz(m):    m.x = ld16target(m, readbyte(m))
def ldxm(m):    m.x = ld16target(m, readword(m))
def ldxx(m):    m.x = ld16target(m, readindex(m))

def lds(m):     m.sp = logicNZV(m, readword(m), signbit=15)
def ldsz(m):    m.sp = ld16target(m, readbyte(m))
def ldsm(m):    m.sp = ld16target(m, readword(m))
def ldsx(m):    m.sp = ld16target(m, readindex(m))

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

def st16target(m, val, target0):
    target1 = incword(target0, 1)
    m.mem[target0] = val >> 8
    m.mem[target1] = val & 0xFF
    m.N = isneg(val, signbit=15)
    m.Z = iszero(val)
    m.V = 0

def stxz(m):    st16target(m, m.x,  readbyte(m))
def stxm(m):    st16target(m, m.x,  readword(m))
def stxx(m):    st16target(m, m.x,  readindex(m))

def stsz(m):    st16target(m, m.sp, readbyte(m))
def stsm(m):    st16target(m, m.sp, readword(m))
def stsx(m):    st16target(m, m.sp, readindex(m))

def tsx(m):     m.x  = incword(m.sp, 1)
def txs(m):     m.sp = incword(m.x, -1)

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

def bita(m):          logicNZV(m, m.a & readbyte(m))
def bitaz(m):         logicNZV(m, m.a & m.mem[readbyte(m)])
def bitam(m):         logicNZV(m, m.a & m.mem[readword(m)])
def bitax(m):         logicNZV(m, m.a & m.mem[readindex(m)])
def bitb(m):          logicNZV(m, m.b & readbyte(m))
def bitbz(m):         logicNZV(m, m.b & m.mem[readbyte(m)])
def bitbm(m):         logicNZV(m, m.b & m.mem[readword(m)])
def bitbx(m):         logicNZV(m, m.b & m.mem[readindex(m)])

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

def tsta(m):    m.C = 0; logicNZV(m, m.a)
def tstb(m):    m.C = 0; logicNZV(m, m.b)
def tstm(m):    m.C = 0; logicNZV(m, m.mem[readword(m)])
def tstx(m):    m.C = 0; logicNZV(m, m.mem[readindex(m)])

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
#   Urnary Arithmetic operations

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

####################################################################
#   Binary Arithmetic operations

def add(m, augend, addend, carry=0):
    ''' Return the modular 8-bit sum of adding `addend` (the operand) and
        `carry` to `augend` (the contents of the register). Set H, N, Z, V
        and C flags based on the result, per pages A-4 (ADC) and A-5 (ADD)
        in the PRG.
    '''
    sum = incbyte(augend, addend)
    sum = incbyte(sum, carry)

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

def adda(m):    m.a = add(m, m.a, readbyte(m))
def addaz(m):   m.a = add(m, m.a, m.mem[readbyte(m)])
def addam(m):   m.a = add(m, m.a, m.mem[readword(m)])
def addax(m):   m.a = add(m, m.a, m.mem[readindex(m)])
def addb(m):    m.b = add(m, m.b, readbyte(m))
def addbz(m):   m.b = add(m, m.b, m.mem[readbyte(m)])
def addbm(m):   m.b = add(m, m.b, m.mem[readword(m)])
def addbx(m):   m.b = add(m, m.b, m.mem[readindex(m)])

def adca(m):    m.a = add(m, m.a, readbyte(m), m.C)
def adcaz(m):   m.a = add(m, m.a, m.mem[readbyte(m)], m.C)
def adcam(m):   m.a = add(m, m.a, m.mem[readword(m)], m.C)
def adcax(m):   m.a = add(m, m.a, m.mem[readindex(m)], m.C)
def adcb(m):    m.b = add(m, m.b, readbyte(m), m.C)
def adcbz(m):   m.b = add(m, m.b, m.mem[readbyte(m)], m.C)
def adcbm(m):   m.b = add(m, m.b, m.mem[readword(m)], m.C)
def adcbx(m):   m.b = add(m, m.b, m.mem[readindex(m)], m.C)

def aba(m):     m.a = add(m, m.a, m.b)

def sub(m, minuend, subtrahend, borrow=0, affectC=True):
    ''' On the 6800 the C condition code is a "carry-borrow" flag: when
        subtracting it is SET if the previous operation needed to borrow
        from the next. Thus, when set, that borrow 1 bit should be
        additionally subtracted from the SBC result.
    '''
    difference = incbyte(minuend, -subtrahend)
    difference = incbyte(difference, -borrow)
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

def suba(m):    m.a = sub(m, m.a, readbyte(m))
def subaz(m):   m.a = sub(m, m.a, m.mem[readbyte(m)])
def subam(m):   m.a = sub(m, m.a, m.mem[readword(m)])
def subax(m):   m.a = sub(m, m.a, m.mem[readindex(m)])
def subb(m):    m.b = sub(m, m.b, readbyte(m))
def subbz(m):   m.b = sub(m, m.b, m.mem[readbyte(m)])
def subbm(m):   m.b = sub(m, m.b, m.mem[readword(m)])
def subbx(m):   m.b = sub(m, m.b, m.mem[readindex(m)])

#   ACCX - M - C = ACCS - (M + C)   (PRM A-59)
def sbca(m):    m.a = sub(m, m.a, readbyte(m), borrow=m.C)
def sbcaz(m):   m.a = sub(m, m.a, m.mem[readbyte(m)], borrow=m.C)
def sbcam(m):   m.a = sub(m, m.a, m.mem[readword(m)], borrow=m.C)
def sbcax(m):   m.a = sub(m, m.a, m.mem[readindex(m)], borrow=m.C)
def sbcb(m):    m.b = sub(m, m.b, readbyte(m), borrow=m.C)
def sbcbz(m):   m.b = sub(m, m.b, m.mem[readbyte(m)], borrow=m.C)
def sbcbm(m):   m.b = sub(m, m.b, m.mem[readword(m)], borrow=m.C)
def sbcbx(m):   m.b = sub(m, m.b, m.mem[readindex(m)], borrow=m.C)

def cmpa(m):          sub(m, m.a, readbyte(m))
def cmpaz(m):         sub(m, m.a, m.mem[readbyte(m)])
def cmpam(m):         sub(m, m.a, m.mem[readword(m)])
def cmpax(m):         sub(m, m.a, m.mem[readindex(m)])
def cmpb(m):          sub(m, m.b, readbyte(m))
def cmpbz(m):         sub(m, m.b, m.mem[readbyte(m)])
def cmpbm(m):         sub(m, m.b, m.mem[readword(m)])
def cmpbx(m):         sub(m, m.b, m.mem[readindex(m)])

def sba(m):     m.a = sub(m, m.a, m.b)
def cba(m):           sub(m, m.a, m.b)

def cpxarg(m, argh, argl):
    xh,     xl =    m.x >> 8,  m.x & 0xFF
    sub(m, xl, argl, affectC=False)
    Zl = m.Z
    sub(m, xh, argh, affectC=False)
    m.Z = Zl and m.Z

def cpx(m):
    argh, argl = readbyte(m), readbyte(m)
    cpxarg(m, argh, argl)

def cpxtarget(m, target):
    argh, argl = m.mem[target], m.mem[incword(target, 1)]
    cpxarg(m, argh, argl)

def cpxz(m):    cpxtarget(m, readbyte(m))
def cpxm(m):    cpxtarget(m, readword(m))
def cpxx(m):    cpxtarget(m, readindex(m))

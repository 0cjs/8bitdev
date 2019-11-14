''' 6502 Arithmetic and Flags

    When doing arithmetic on the 6502, you use the following flags to
    determine what to do after an operation. (Here we ignore BCD
    operations using the D (decimal) flag.)

    - Z (zero): Set if result is $00.
    - N (negative): Bit 7 of result.
    - C (carry, "not borrow"): Set when an addition result is >$FF.
      Cleared when a subtraction result is <$00.
    - V (overflow): Set when an addition result >$7F or a subtraction
      result <$80.

    XXX or V flag set when sign changes? Which sign?

'''

from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    return Machine()

def add(M, a, b):
    M.deposit(0x200, [ I.LDA, a, I.CLC, I.ADC, b, I.RTS, ])
    M.call(0x200)

def sub(M, a, b):
    M.deposit(0x200, [ I.LDA, a, I.SEC, I.SBC, b, I.RTS, ])
    M.call(0x200)

####################################################################

def test_2s_complement(M):
    ''' In 2s complement, the positive integers (sign bit clear) are
        the same as in unsigned arithmetic, though of course the
        maximum number expressable is trucated (2^(n-1)-1) as compared
        to an unsigned integer of the same size (2^n-1).
    '''

    #   Negative numbers can be viewed as (0 - n) where n is the
    #   (positive) absolute value.
    sub(M, 0x00, 0x01); assert R(a=0xFF) == M.regs  # -01 == $FF
    sub(M, 0x00, 0x02); assert R(a=0xFE) == M.regs  # -02 == $FE
                                                    # ...
    sub(M, 0x00, 0x7F); assert R(a=0x81) == M.regs  # -7F == $81
    sub(M, 0xFF, 0x7F); assert R(a=0x80) == M.regs  # -80 == $80

    #   They can also be viewed as the inversion of the numeric
    #   bits (i.e., XOR with $7F then add 1) with the sign set. Thus, abs()
    #   for values of -1 to -(2^(n-1)-1) is the just the XOR with $FF.
    def absofneg(a):
        M.deposit(0x200, [
            I.LDA, a, I.EOR, 0xFF,  # XOR with $FF
            I.CLC, I.ADC, 0x01,     # Add 1
            I.RTS, ])
        M.call(0x200)
    absofneg(0xFF); assert R(a=0x01) == M.regs  # -$01 → $01
    absofneg(0xFE); assert R(a=0x02) == M.regs  # -$02 → $02
                                                # ...
    absofneg(0x81); assert R(a=0x7F) == M.regs  # -$7F → $7F

def test_2s_complement_abs(M):
    ''' We can calculate the absolute value using the inversion/XOR
        technique above, checking first to see that the number isn't
        already positive, and also checking for overflow because we
        can represent -$80 but not +$80.
    '''
    def abs(a):
        #   Returns the absolute value of the 8-bit signed input.
        #   N flag set indicates overflow, i.e., input was -$80
        #       and we can't represent $80 in a signed 8-bit value
        M.deposit(0x200, [
            I.LDA, a,
            I.BPL, 5,               # Not negative; we're done (jump to RTS)
            I.EOR, 0xFF,            # XOR with $FF
            I.CLC, I.ADC, 0x01,     # Add 1, setting N if we overflowed
            I.RTS, ])
        M.call(0x200)

    abs(0x00); assert R(a=0x00, N=0) == M.regs
    abs(0x01); assert R(a=0x01, N=0) == M.regs
    abs(0x7F); assert R(a=0x7F, N=0) == M.regs

    abs(0xFF); assert R(a=0x01, N=0) == M.regs
    abs(0xFE); assert R(a=0x02, N=0) == M.regs
    abs(0x81); assert R(a=0x7F, N=0) == M.regs

    abs(0x80); assert R(a=0x80, N=1) == M.regs  # overflow

####################################################################

def test_adc_unsigned(M):
    ''' Unsigned ADC (add with carry).
        We always ignore the N and V flags.
        C flag indicates overflow; extend with $01 MSB.
    '''
    add(M, 0x00, 0x00); assert R(a=0x00, C=0) == M.regs    # 00 + 00 = 000
    add(M, 0xFE, 0x01); assert R(a=0xFF, C=0) == M.regs    # FE + 01 = 0FF
    add(M, 0xFF, 0x01); assert R(a=0x00, C=1) == M.regs    # FF + 01 = 100
    add(M, 0xFF, 0xFF); assert R(a=0xFE, C=1) == M.regs    # FF + FF = 1FE

def test_adc_signed(M):
    ''' Signed ADC (add with carry).
        We always ignore the C flag.
        Overflow clear: extend with N.
        Overflow set: extend with inverted N.
    '''

    ##########################################################
    #   Overflow clear means that sign bit is valid.
    #   -128 <= result <= +127.
    #   Extend with byte filled with sign bit: $00 or $FF.

    #       +00 + +00            = +000
    add(M, 0x00, 0x00); assert R(a=0x00, N=0, V=0) == M.regs
    #       +7E + +01            = +07F
    add(M, 0x7E, 0x01); assert R(a=0x7F, N=0, V=0) == M.regs

    #       +00 + -01            = -001
    add(M, 0x00, 0xFF); assert R(a=0xFF, N=1, V=0)
    #       +00 + -7F            = -07F
    add(M, 0x00, 0x81); assert R(a=0x81, N=1, V=0)
    #       +01 + -7F            = -07E
    add(M, 0x01, 0x81); assert R(a=0x82, N=1, V=0)

    #       +00 + -80            = -080
    add(M, 0x00, 0x80); assert R(a=0x80, N=1, V=0)
    #       +01 + -80            = -07F
    add(M, 0x01, 0x80); assert R(a=0x81, N=1, V=0)

    ##########################################################
    #   Overflow set means that sign bit is inverted.
    #   N=1 → result > 127 → extend with $00.

    #       +7F + +01            = +080 = $0080.
    add(M, 0x7F, 0x01); assert R(a=0x80, N=1, V=1) == M.regs
    #       +7F + +7F            = +0FE = $00FE.
    add(M, 0x7F, 0x7F); assert R(a=0xFE, N=1, V=1) == M.regs

    ##########################################################
    #   Overflow set means that sign bit is inverted.
    #   N=0 → result < -128 → extend with $FF.

    #       -80 + -01            = -081 = $FF7F
    add(M, 0x80, 0xFF); assert R(a=0x7F, N=0, V=1) == M.regs
    #       -80 + -7F            = -0FF = $FF01
    add(M, 0x80, 0x81); assert R(a=0x01, N=0, V=1) == M.regs
    #       -80 + -80            = -100 = $FF00
    add(M, 0x80, 0x80); assert R(a=0x00, N=0, V=1) == M.regs

####################################################################

def test_sbc_unsigned(M):
    ''' Unsigned SBC (subtract with carry).
        We always ignore the N and V flags.
        C flag clear indicates underflow (borrow used).
    '''
    sub(M, 0x00, 0x00); assert R(a=0x00, C=1) == M.regs
    sub(M, 0xFF, 0x00); assert R(a=0xFF, C=1) == M.regs
    sub(M, 0xFF, 0xFD); assert R(a=0x02, C=1) == M.regs

    #   In these cases, C=0 (borrow used) → result < 0.
    #   We could generate a signed result by sign-extending with $FF.
    sub(M, 0x00, 0x01); assert R(a=0xFF, C=0) == M.regs     # $FFFF = -1
    sub(M, 0x00, 0xFF); assert R(a=0x01, C=0) == M.regs     # $FF01 = -255

def test_sbc_signed(M):
    ''' Signed SBC (subtract with carry).
    '''

    #   +minuend, +subtrahend, +difference.
    sub(M, 0x00, 0x00); assert R(a=0x00, N=0, V=0) == M.regs
    sub(M, 0x7F, 0x00); assert R(a=0x7F, N=0, V=0) == M.regs
    sub(M, 0x7F, 0x7F); assert R(a=0x00, N=0, V=0) == M.regs

    #   +minuend, +subtrahend, -difference.
    #       +00 - +01            = -001
    sub(M, 0x00, 0x01); assert R(a=0xFF, N=1, V=0) == M.regs
    #       +00 - +7F            = -07F
    sub(M, 0x00, 0x7F); assert R(a=0x81, N=1, V=0) == M.regs
    #       +7E - +7F            = -001
    sub(M, 0x7E, 0x7F); assert R(a=0xFF, N=1, V=0) == M.regs

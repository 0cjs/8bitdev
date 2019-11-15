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
    def sub(a, b): global sub; return sub(M, a, b)

    #   Negative numbers can be viewed as (0 - n) where n is the
    #   (positive) absolute value.
    sub(0x00, 0x01); assert R(a=0xFF) == M.regs  # -01 == $FF
    sub(0x00, 0x02); assert R(a=0xFE) == M.regs  # -02 == $FE
                                                 # ...
    sub(0x00, 0x7F); assert R(a=0x81) == M.regs  # -7F == $81
    sub(0xFF, 0x7F); assert R(a=0x80) == M.regs  # -80 == $80

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

        The C flag set indicates overflow; to have the full result we
        must extend the number by adding a new MSB of $01, increasing
        the representation size by 8 bits.

        We always ignore the N and V flags; an unsigned number can
        never be negative and V is used only with signed operations.
    '''
    def add(a, b): global add; return add(M, a, b)

    add(0x00, 0x00); assert R(a=0x00, C=0) == M.regs    # 00 + 00 = 000
    add(0xFE, 0x01); assert R(a=0xFF, C=0) == M.regs    # FE + 01 = 0FF
    add(0xFF, 0x01); assert R(a=0x00, C=1) == M.regs    # FF + 01 = 100
    add(0xFF, 0xFF); assert R(a=0xFE, C=1) == M.regs    # FF + FF = 1FE

def test_adc_signed(M):
    ''' Signed ADC (add with carry).

        The carry of a signed addition, if it exists, ends up changing
        the most significant bit, the sign bit. The V (overflow) flag
        detects this. It's calculated as follows.

        If the signs of the numbers are different, overflow can never
        occur. Thus V will be clear and the result sign bit will
        always be correct.

        If the signs of the numbers are the same, the sign of the
        result must be the same, too. If it is the same, V is clear
        and we have a correct result.

        If the sign of the result is not the same, that means we
        overflowed and so V is set. To have the full result we must
        extend the number (increasing the representation size by 8
        bits) by adding a new MSB. This will be a sign-extend using
        the _opposite_ of the N flag: if the (truncated) result has a
        positive sign bit, we extend with $FF because it's really a
        negative number where the sign bit "couldn't fit"; if it has a
        negative sign bit we extend with $00 because it's really a
        positive number.

        We always ignore the C flag.
    '''
    def add(a, b): global add; return add(M, a, b)

    ##########################################################
    #   Overflow clear means that sign bit is valid.
    #   -128 <= result <= +127.
    #   No need to extend, but if we did, we'd extend with byte
    #   filled with the sign bit: $00 or $FF.

    #    +00 + +00            = +000
    add(0x00, 0x00); assert R(a=0x00, N=0, V=0) == M.regs
    #    +7E + +01            = +07F
    add(0x7E, 0x01); assert R(a=0x7F, N=0, V=0) == M.regs

    #    +00 + -01            = -001
    add(0x00, 0xFF); assert R(a=0xFF, N=1, V=0)
    #    +00 + -7F            = -07F
    add(0x00, 0x81); assert R(a=0x81, N=1, V=0)
    #    +01 + -7F            = -07E
    add(0x01, 0x81); assert R(a=0x82, N=1, V=0)

    #    +00 + -80            = -080
    add(0x00, 0x80); assert R(a=0x80, N=1, V=0)
    #    +01 + -80            = -07F
    add(0x01, 0x80); assert R(a=0x81, N=1, V=0)

    ##########################################################
    #   Overflow set means that sign bit is inverted.
    #   N=1 → result > 127 → extend with $00.

    #    +7F + +01            = +080 = $0080.
    add(0x7F, 0x01); assert R(a=0x80, N=1, V=1) == M.regs
    #    +7F + +7F            = +0FE = $00FE.
    add(0x7F, 0x7F); assert R(a=0xFE, N=1, V=1) == M.regs

    ##########################################################
    #   Overflow set means that sign bit is inverted.
    #   N=0 → result < -128 → extend with $FF.

    #    -80 + -01            = -081 = $FF7F
    add(0x80, 0xFF); assert R(a=0x7F, N=0, V=1) == M.regs
    #    -80 + -7F            = -0FF = $FF01
    add(0x80, 0x81); assert R(a=0x01, N=0, V=1) == M.regs
    #    -80 + -80            = -100 = $FF00
    add(0x80, 0x80); assert R(a=0x00, N=0, V=1) == M.regs

####################################################################

def test_sbc_unsigned(M):
    ''' Unsigned SBC (subtract with carry).

        The C flag clear indicates underflow (i.e., the borrow was
        used) and so our result < 0. We could generate an error,
        or we could generate an unsigned number.

        We ignore the N flag unless we want to use it to generate
        a signed result without doing unnecessary sign-extension
        into a new byte, increasing the size of the integer.

        We always ignore the V flag.
    '''
    def sub(a, b): global sub; return sub(M, a, b)

    sub(0x00, 0x00); assert R(a=0x00, C=1) == M.regs
    sub(0xFF, 0x00); assert R(a=0xFF, C=1) == M.regs
    sub(0xFF, 0xFD); assert R(a=0x02, C=1) == M.regs

    #   In these cases, C=0 (borrow used) → result < 0.
    #   But because the result is ≥ -$80, as we can tell from the N
    #   flag being set, we could generate a signed result by setting
    #   bit 7 (`OR $80`).
    sub(0x00, 0x01); assert R(a=0xFF, C=0, N=1) == M.regs  # $FF = -$01
    sub(0x00, 0x80); assert R(a=0x80, C=0, N=1) == M.regs  # $80 = -$80

    #   In these cases, C=0 (borrow used) → result < 0.
    #   The result is also < $80 as we can tell by the N flag being
    #   clear, so if we want to generate a signed result we would need
    #   to sign-extend with an additional byte, a new MSB of $FF.
    sub(0x00, 0x81); assert R(a=0x7F, C=0, N=0) == M.regs  # $FF7F = -$81
    sub(0x00, 0xFF); assert R(a=0x01, C=0, N=0) == M.regs  # $FF01 = -$FF

def test_sbc_signed(M):
    ''' Signed SBC (subtract with carry).

        The V flag clear indicates no underflow or overflow (i.e., the
        result fit into 8 bits: -$80 ≤ result ≤ +$7F), and so the N
        flag is correct.

        The V flag set indicates underflow (result < -$80) or overflow
        (result > +$7F), and so the N flag is incorrect. To get the
        full result we need to sign-extend with an additional byte
        with all bits set to the _opposite_ of the N flag.

        We always ignore the C flag.
    '''
    def sub(a, b): global sub; return sub(M, a, b)

    #   Positive minuend and subtrahend.
    #   Result will always fit in a signed 8-bit value.
    #
    sub(0x00,  0x00); assert R(a=0x00, N=0, V=0) == M.regs
    sub(0x7F,  0x00); assert R(a=0x7F, N=0, V=0) == M.regs
    sub(0x7F,  0x7F); assert R(a=0x00, N=0, V=0) == M.regs
    #    +00  - +01            = -$01
    sub(0x00,  0x01); assert R(a=0xFF, N=1, V=0) == M.regs
    #   +$7E - +$7F            = -$01
    sub(0x7E,  0x7F); assert R(a=0xFF, N=1, V=0) == M.regs
    #   +$00 - +$7F            = -$7F
    sub(0x00,  0x7F); assert R(a=0x81, N=1, V=0) == M.regs

    #   Negative minuend and negative subtrahend.
    #   Result will always fit in a signed 8-bit value.
    #
    #   -$01 - -$01            = +$00
    sub(0xFF,  0xFF); assert R(a=0x00, N=0, V=0) == M.regs
    #   -$80 - -$80            = +$00
    sub(0x80,  0x80); assert R(a=0x00, N=0, V=0) == M.regs
    #   -$01 - -$80            = +$7F
    sub(0xFF,  0x80); assert R(a=0x7F, N=0, V=0) == M.regs
    #   -$80 - -$01            = -$7F
    sub(0x80,  0xFF); assert R(a=0x81, N=1, V=0) == M.regs
    #   -$80 - -$7F            = -$01
    sub(0x80,  0x81); assert R(a=0xFF, N=1, V=0) == M.regs
    #   -$7F - -$80            = +$01
    sub(0x81,  0x80); assert R(a=0x01, N=0, V=0) == M.regs

    #   Negative minuend and positive subtrahend.
    #   May overflow, result < -$80
    #   We show the extended version, extended with the inverse of N.
    #   `x` above the N flag indicates it's incorrect.
    #
    #   -$7F - +$01            = -$80         no overflow
    sub(0x81,  0x01); assert R(a=0x80, N=1, V=0) == M.regs
    #   -$7F - +$02     = -$81 ($FF7F)   x    overflow
    sub(0x81,  0x02); assert R(a=0x7F, N=0, V=1) == M.regs
    #   -$7F - +$7F     = -$FE ($FF02)   x    overflow
    sub(0x81,  0x7F); assert R(a=0x02, N=0, V=1) == M.regs
    #   -$80 - +$7F     = -$FF ($FF01)   x    overflow
    sub(0x80,  0x7F); assert R(a=0x01, N=0, V=1) == M.regs

    #   Positive minuend and negative subtrahend.
    #   May overflow, result > +$7F.
    #   We show the extended version, extended with the inverse of N.
    #   `x` above the N flag indicates it's incorrect.
    #
    #   +$7E - -$01            = +$7F         no overflow
    sub(0x7E,  0xFF); assert R(a=0x7F, N=0, V=0) == M.regs
    #   +$7E - -$02     = +$80 ($0080)   x    overflow
    sub(0x7E,  0xFE); assert R(a=0x80, N=1, V=1) == M.regs
    #   +$00 - -$80     = +$80 ($0080)   x    overflow
    sub(0x00,  0x80); assert R(a=0x80, N=1, V=1) == M.regs
    #   +$7F - -$80     = +$FF ($00FF)   x    overflow
    sub(0x7F,  0x80); assert R(a=0xFF, N=1, V=1) == M.regs

####################################################################

def cmp(M, a, b):
    M.deposit(0x200, [ I.LDA, a, I.CMP, b, I.RTS, ])
    M.call(0x200)

#   CMP nn is a subtract without carry (SEC; SBC nn) but the result is
#   thrown away and only the flags are kept. Further, the V flag is
#   never changed; only the N, Z and C flags are set.
#
#   For a lot more, see "Beyond 8-bit Unsigned Comparisons" by Bruce Clark:
#       http://www.6502.org/tutorials/compare_beyond.html

def test_cmp_equality(M):
    ''' For equality, signed and unsigned are the same:
        Z set → a = b (BEQ).     Z clear → a ≠ b (BNE).
    '''
    def cmp(a, b): global cmp; return cmp(M, a, b)

    cmp(0x00, 0x00); assert R(a=0x00, Z=1) == M.regs   # a = b
    cmp(0x00, 0x01); assert R(a=0x00, Z=0) == M.regs   # a ≠ b
    cmp(0x00, 0xFF); assert R(a=0x00, Z=0) == M.regs   # a ≠ b

def test_cmp_unsigned(M):
    ''' For unsigned comparisons, we use only the carry:
        C set → a ≥ b (BCS/BGE). C clear → a < b (BCC/BLT).
    '''
    def cmp(a, b): global cmp; return cmp(M, a, b)

    cmp(0xFE, 0xFE); assert R(a=0xFE, C=1) == M.regs   # a ≥ b
    cmp(0xFE, 0xFD); assert R(a=0xFE, C=1) == M.regs   # a ≥ b
    cmp(0xFE, 0x00); assert R(a=0xFE, C=1) == M.regs   # a ≥ b
    cmp(0xFE, 0xFF); assert R(a=0xFE, C=0) == M.regs   # a < b

    cmp(0x00, 0x00); assert R(a=0x00, C=1) == M.regs   # a ≥ b
    cmp(0x00, 0x01); assert R(a=0x00, C=0) == M.regs   # a < b
    cmp(0x00, 0xFF); assert R(a=0x00, C=0) == M.regs   # a < b

def test_signed_comparison(M):
    ''' CMP does only unsigned comparisons because it does not affect
        the V flag. Thus we must use SBC to do signed comparisons.

        Signed comparisons use a comparison of the N and V flags:
            N = V → a ≥ b.    N ≠ V → a < b

        (The result and the carry can be ignored, but I have them here
        to make sure I understand everything that's going on.)
    '''
    def sub(a, b): global sub; return sub(M, a, b)

    #   N = V → a ≥ b

    '+$7E ≥ +$7E'; sub(0x7E, 0x7E); assert R(N=0, V=0, a=0x00, C=1) == M.regs
    '+$7E ≥ +$00'; sub(0x7E, 0x00); assert R(N=0, V=0, a=0x7E, C=1) == M.regs
    '+$7E ≥ -$01'; sub(0x7E, 0xFF); assert R(N=0, V=0, a=0x7F, C=0) == M.regs
    '+$7E ≥ -$7F'; sub(0x7E, 0x81); assert R(N=1, V=1, a=0xFD, C=0) == M.regs
    '+$7E ≥ -$80'; sub(0x7E, 0x80); assert R(N=1, V=1, a=0xFE, C=0) == M.regs

    '+$00 ≥ +$00'; sub(0x00, 0x00); assert R(N=0, V=0, a=0x00, C=1) == M.regs
    '+$00 ≥ -$01'; sub(0x00, 0xFF); assert R(N=0, V=0, a=0x01, C=0) == M.regs
    '+$00 ≥ -$7F'; sub(0x00, 0x81); assert R(N=0, V=0, a=0x7F, C=0) == M.regs
    '+$00 ≥ -$80'; sub(0x00, 0x80); assert R(N=1, V=1, a=0x80, C=0) == M.regs

    '-$7E ≥ -$7E'; sub(0x81, 0x81); assert R(N=0, V=0, a=0x00, C=1) == M.regs
    '-$7E ≥ -$7F'; sub(0x81, 0x80); assert R(N=0, V=0, a=0x01, C=1) == M.regs

    #   N ≠ V → a < b

    '+$7E < +$7F'; sub(0x7E, 0x7F); assert R(N=1, V=0, a=0xFF, C=0) == M.regs
    '+$00 < +$7F'; sub(0x00, 0x7F); assert R(N=1, V=0, a=0x81, C=0) == M.regs
    '+$00 < +$01'; sub(0x00, 0x01); assert R(N=1, V=0, a=0xFF, C=0) == M.regs
    '-$7F < +$7F'; sub(0x81, 0x7F); assert R(N=0, V=1, a=0x02, C=1) == M.regs
    '-$7F < +$00'; sub(0x81, 0x00); assert R(N=1, V=0, a=0x81, C=1) == M.regs
    '-$7F < -$01'; sub(0x81, 0xFF); assert R(N=1, V=0, a=0x82, C=0) == M.regs
    '-$7F < -$7E'; sub(0x81, 0x82); assert R(N=1, V=0, a=0xFF, C=0) == M.regs

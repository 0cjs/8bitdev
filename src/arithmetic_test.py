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

        (To read 2's complement value when sign=1,
        drop sign, invert remaining bits, add 1 to get the absolute value.)
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

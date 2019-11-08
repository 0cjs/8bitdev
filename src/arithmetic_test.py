from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    return Machine()

def test_adc(M):
    ''' Demonstrate ADC add with carry instruction.

        When you look at additions as unsigned, you ignore the
        negative and overflow flags, and use only the carry.

        When you look at them as signed you use the negative flag,
        but overflow set indicates that the negative flag is wrong.
        The borrow (inverted carry) is ignored.
    '''

    def add(a, b):
        M.deposit(0x200, [ I.LDA, a, I.CLC, I.ADC, b, I.RTS, ])
        M.call(0x200)

    #   0 + 7F = 7F: Positive. No overflow. No carry.
    add(0x00, 0x7F); assert R(a=0x7F, Z=0, N=0, V=0, C=0) == M.regs

    #   Unsigned view: 0 + FF = FF
    #     Negative ignored. Overflow ignored. Carry clear.
    #   Signed view: 0 + -1 = -1
    #     Negative set. Overflow clear. Borrow set.
    add(0x00, 0xFF); assert R(a=0xFF, Z=0, N=1, V=0, C=0) == M.regs
    add(0x00, 0x80); assert R(a=0x80, Z=0, N=1, V=0, C=0) == M.regs

    #   Unsigned view: 1 + FF = 100
    #     Negative ignored. Overflow clear but ignored. Carry set.
    #     (It did "overflow" but we know that from the carry.)
    #   Signed view: 1 + -1 = 0: not negative, no overflow
    #     Negative clear. Overflow clear. Borrow clear.
    add(0x01, 0xFF); assert R(a=0x00, Z=1, N=0, V=0, C=1) == M.regs

    #   Unsigned view: 80 + 1 = 81
    #     Negative ignored. Overflow ignored. Carry clear.
    #   Signed view: -80 + 1 = -79
    #     Negative set. Overflow clear. Borrow set but ignored.
    add(0x80, 0x01); assert R(a=0x81, Z=0, N=1, V=0, C=0) == M.regs

    #   Unsigned view: 80 + 7F = FF
    #     Negative ignored. Overflow clear. Carry clear.
    #   Signed view: -80 + 7F = -1
    #     Negative set. Overflow clear. Borrow set but ignored.
    add(0x80, 0x7F); assert R(a=0xFF, Z=0, N=1, V=0, C=0) == M.regs

    #   Unsigned view: 80 + 80 = 100
    #     Negative ignored. Overflow set. Carry set.
    #   Signed view: -80 + -80 = -100
    #     Negative set but wrong, as indicated by overflow.
    #     Overflow set. Borrow clear but ignored.
    add(0x80, 0x80); assert R(a=0x00, Z=1, N=0, V=1, C=1) == M.regs

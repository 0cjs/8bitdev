''' This is the generic test for prvischar routines. See the other
    files in this directory for examples of how to use it.
'''

def prvischar_test(m, R, S, loadbios, char, output):
    _, ostream = loadbios()
    m.call(S.prvischar, R(a=char))
    #   Not really ISO-8859-1, but just 8-bit output.
    actual = str(ostream.getvalue(), encoding='ISO-8859-1')
    assert (output,  R(a=char)) \
        == (actual,   m.regs )

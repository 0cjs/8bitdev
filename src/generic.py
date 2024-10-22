''' Generic test support.

    The routines here provide generic test functionality for use in
    ``*.pt`` test scripts. When importing functions from this, remember
    to enable pytest rewriting for this module::

        pytest.register_assert_rewrite('src.generic')
        from src.generic import …
'''

#   XXX There ought to be a better way to do this than to make the
#   user write a function that calls this function.
def a_output_test(addr, m, R, S, loadbios, a, output, trace=0):
    ''' This generic test loads the A register with value `a`, calls
        `addr`, and then compares the output (printed using ``prchar`` or
        other BIOS means) with `output`. Use `@pytest.mark.parametrize` to
        supply `a` and `output` to your ``test_*`` function, which should
        then call this with `addr` and all parameters it's received.
    '''
    _, ostream = loadbios()
    m.call(addr, R(a=a), trace=trace)
    #   Not really ISO-8859-1, but just 8-bit output.
    actual = str(ostream.getvalue(), encoding='ISO-8859-1')
    assert (output,  R(a=a)) \
        == (actual,   m.regs )

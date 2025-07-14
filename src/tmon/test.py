import  pytest
param = pytest.mark.parametrize

def log_interaction(command, expected, inp, out):
    ''' Takes the command executed, the expected output, and the I/O handles.

        Returns `(unread, echo, output)`: any unread data still present
        in the input, the entirety of the output including the echoed
        command, and the output with the echoed command removed. (The
        caller is expected to assert these values as appropriate.)

        For debugging purposes, prints out the command, any unread data
        remaining in the input, everything written to the output including
        the echoed command (if any), the expected output passed in, and the
        actual output with the echoed command removed.
    '''
    unread = inp.read()
    echo = out.written()                        # includes echoed input
    print(f' command: {command!r}')
    print(f'  unread: {unread!r}')
    print(f'    echo: {echo!r}')
    print(f'expected: {expected!r}')
    if b'\r' in echo:
        #   Removed echoed input through the '\r', if present.
        output = echo.split(b'\r', maxsplit=1)[1]
    else:
        output = echo
    print(f'  output: {output}')
    return unread, echo, output

####################################################################

#   XXX These are close to generic "given input produces expected output"
#   tests. But before we can factor out more of the common code, we need to
#   try some tests that depend on memory state setup and/or assertions.
#
#   We intend to maintain, as much as reasonable, the "send a command line"
#   form of tests for commands because that makes the tests more easily
#   genericised across different systems, and avoids forcing certain ways
#   of implementing the command.

#   '\n' is what the simulator BIOS prints as a newline. We expect this
#   to be '\r\n' on most machines; not clear how to test that, or even
#   if we should.
NL = b'\n'

def test_newline(m, S, loadbios):
    command  = b'\r'
    expected = b'M\x08 ' + NL    # erases visible ^M
    inp, out = loadbios(input=command)
    try:
        m.call(S['prompt.read'], stopat=[S.prompt], maxsteps=10000)
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output, 'expected output'
    assert b'' == unread, 'input was completely consumed'

def test_comment(m, S, loadbios):
    text     = b'  Text that should be ignored.'
    command  = b'#' + text + b'\r'
    expected = b'#' + text + NL
    inp, out = loadbios(input=command)
    try:
        m.call(S['prompt.read'], stopat=[S.prompt], maxsteps=10000)
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output, 'expected output'
    assert b'' == unread, 'input was completely consumed'

@param('command, expected', [
    (b'/    ?0    /0\r', b'0000:0000   0000 @    0000 @   \n'),
    (b'/ ?0040 /0000\r', b'0040:0000   0040 @@   0040 @@  \n'),
    (b'/ ?0000 /0040\r', b'0000:0040   0040 @@   FFC0 @   \n'),
    (b'/ ?1274 /0202\r', b'1274:0202   1476 vv   1072 rr  \n'),
    (b'/ ?6768 /7878\r', b'6768:7878   DFE0 `    EEF0 p   \n'),
])
def test_calc(m, S, loadbios, command, expected):
    inp, out = loadbios(input=command)
    #   Default values not tested; ensure all params are specifed in command.
    #m.call(S.init, stopat=[S['init.end']])  # setup default values

    #   We don't call `prompt` because that would cause a stop immediately
    #   and we prefer to not have the prompt in the output anyway. This
    #   does mean that the stack reset done between prompt and prompt.read
    #   is not executed; it's not clear if there will be tests this breaks.
    m.call(S['prompt.read'], stopat=[S.prompt], maxsteps=10000)

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output
    assert b'' == unread, 'input was completely consumed'

def test_params_good_bad_good(m, S, loadbios):
    ''' Show that if we enter a good param then a bad param, we get an
        error and still can enter a good param after that.
        This depends on test_calc() working correctly.
    '''
    expected = b'0004:0002   0006 F    0002 B   ' + NL
    command  = b'/ ?1 /2 x3 ?4\r'
    inp, out = loadbios(input=command)
    m.call(S['prompt.read'], stopat=[S.prompt], maxsteps=10000)

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output
    assert b'' == unread, 'input was completely consumed'

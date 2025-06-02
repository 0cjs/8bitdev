import  pytest

param = pytest.mark.parametrize

#   XXX This is actually a generic "any input produces expected output"
#   test, but we don't use it as such (at least not yet) until we try some
#   tests that depend on memory state setup and/or assertions to see how
#   the refactoring of the core bits of it roll out. We do intend to
#   maintain, as much as reasonable, the "send a command line" form of
#   tests for commands because that makes the tests more easily genericised
#   across different systems, and avoids forcing certain ways of
#   implementing the command.
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

    echo = out.written()                        # includes echoed input
    output = echo.split(b'\r', maxsplit=1)[1]   # remove echoed input
    print(f'   input: {command}')
    print(f'    echo: {echo}')
    print(f'expected: {expected}')
    print(f'  output: {output}')

    assert expected == output
    assert b'' == inp.read(), 'input was completely consumed'

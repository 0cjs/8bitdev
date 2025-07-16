from    random  import randrange
import  pytest
param = pytest.mark.parametrize

NAK     = b'\x15'   # Ctrl-U
CAN     = b'\x18'   # Ctrl-X
ZCMD    = b'\x1A'   # SUB/Ctrl-Z as an invalid command to make `prompt` error
ZOUT    = b'.Z'     # prompt and `prvischar` output of ZCMD

#   '\n' is what the simulator BIOS prints as a newline. We expect this
#   to be '\r\n' on most machines; not clear how to test that, or even
#   if we should.
NL = b'\n'

#####################################################################

#   XXX This is unused, but we leave it in place (with test) as an example
#   of how we should have tests for support functions in this file.
def remove_command_echo(command, output):
    ''' Remove `command`, a following CR if present, and a NL following
        that if present, from the given `output`.
    '''
    #   Not very pretty, but at least avoids checking for particular types.
    #   (Do this first to confirm we can handle type(output).)
    try:
        CR = type(output)('\r', encoding='ASCII')
        LF = type(output)('\n', encoding='ASCII')
    except TypeError:
        CR = type(output)('\r')
        LF = type(output)('\n')

    if not output.startswith(command):
        return output
    s = output[len(command):]
    if s.startswith(CR):  s = s[1:]
    if s.startswith(LF):  s = s[1:]
    return s

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

@param('command, expected', [
    #   In all cases we expect a prompt, a `prvischar` version of our
    #   input char, a BEL, and a CR returning us to the start of the
    #   line (whence the prompt will be printed again, if we didn't
    #   stop before that runs).
    (b'\x00',   b'.@\a\r'),         # possibly we should ignore NUL
    (ZCMD,      ZOUT + b'\a\r'),    # many tests rely on this being invalid!
    (b'\x1F',   b'._\a\r'),
    (b'\x7F',   b'.?\a\r'),
    (b'\xFF',   b'.?\a\r'),
    (b'!',      b'.!\a\r'),
    (b'~',      b'.~\a\r'),
])
def test_invalid_command(m, S, loadbios, command, expected):
    ''' Many other tests rely on this working. '''
    #   XXX Consider using pytest-dependencies to make this explicit.

    inp, out = loadbios(input=command)
    try:
        #   `.setstack` is required for the `ret` in `.cmderr` to work.
        m.call(S['prompt.setstack'], stopat=[S.prompt])
    except EOFError as ex:  print(f'OVERRUN! {ex}')
    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == echo

@param('command', [ b'\rZ', b'\nZ', b' Z', ])
def test_ignored(m, R, S, loadbios, command):
    ''' This is a bit awkward because ignored 'commands' should not be
        echoed, and thus generally don't go through the stanard command
        dispatch procedure, which echos the command char before
        dispatching. Here instead of going through the full command
        execution that finishes by going back to the prompt, we terminate
        at the point where we would echo, giving an extra char for it to
        read and echo after the ignored char.

        XXX This needs to be rethought to see if there will be any issues
        with implementations for other CPUs.
    '''
    expected = b''
    inp, out = loadbios(input=command)
    try:
        m.call(S['prompt.read'], stopat=[S['prompt.echocmd']])
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    #   XXX Probably we should just be looking at the echo.
    assert R(a=ord('Z')) == m.regs

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output, 'expected output'
    assert b'' == unread, 'input was completely consumed'

@param('command, expected', [
    (b'q'+NAK,  b'.q    \b\b\b\b\\\n'),     # cancel with Ctrl-U
    (b'q'+CAN,  b'.q    \b\b\b\b\\\n'),     # cancel with Ctrl-X
])
def test_cancel(m, loadbios, S, R,  command, expected):
    command += ZCMD         # invalid command to trigger prompt error
    expected += ZOUT
    cmderr = S['prompt.cmderr']

    inp, out = loadbios(input=command)
    try:
        m.call(S.prompt, stopat=[cmderr])
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert (b'', expected) == (inp.read(), out.written())
    assert cmderr == m.regs.pc

####################################################################

def test_newline(m, S, loadbios):
    command  = b'\v'
    expected = b'K\x08 ' + NL    # erases visible ^K
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

#   Also does some testing of parameter parsing.
@param('command, param, expected', [
    (b'q\n',            0, b'.q\n'),
    (b'q   \n',         0, b'.q   \n'),
    #   Cursor left on current param value; on CR, ???.
    #   XXX not clear why only one `0` in the reprint.
    (b'qt0\n',         0, b'.qt00\b\b0    \b\b\b\b\n'),
    (b'qt3\n',         3, b'.qt00\b\b3    \b\b\b\b\n'),
    (b'qt21\n',     0x21, b'.qt00\b\b21    \b\b\b\b\n'),
    (b'q  t0  \n',     0, b'.q  t00\b\b0     \b\b\b\b \n'),
    (b'qt14 t3\n',     3, b'.qt00\b\b14     \b\b\b\bt14\b\b3    \b\b\b\b\n'),
])
def test_quit(m, R, S, loadbios, command, param, expected):
    inp, out = loadbios(input=command)
    try:
        m.call(S.prompt, stopat=[S.exit])
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread, echo, output = log_interaction(command, expected, inp, out)
    assert (param,    b'', expected) \
        == (  m.a, unread, output)
    #   XXX Should check CRC on saved params as well.

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

#   Intel Hex record format: `:ccAAAAttDD…ss\r`
#       cc   byte count for data portion
#       AAAA address (always big-endian)
#       tt   type
#       DD…  data bytes, 0-255
#       ss   checksum (currently ignored)
#   Record Types:
#       00: Data
#       01: EOF: cc=00, AAAA=ignored, DD=empty
#       02,03,04,05: Extended addresses; unsupported
@param('command, addr, expected_dep', [
    (b':00aaaa01ee',        0xAAAA, b''),               # EOF record
    (b':00aabb00ee',        0xAABB, b''),               # data len=0
    (b':01aacc0012ee',      0xAACC, b'\x12'),           # data len=1
    (b':03cccc00876543ee',  0xCCCC, b'\x87\x65\x43'),   # data len=3
])
def test_intelhex_good(m, S, loadbios, command, addr, expected_dep):
    sentinel = b'\xEE'
    dlen = len(expected_dep)
    m.deposit(addr-1, sentinel*(dlen+2))
    expected_dep = sentinel + expected_dep + sentinel

    record_count = randrange(60000); m.depword(S.vL_calc, record_count)
    success_count  = randrange(60000); m.depword(S.vR_calc, success_count)

    inp, out = loadbios(input=command)
    try:
        m.call(S['prompt.read'], stopat=[S.prompt])
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread_actual, echo, output = log_interaction(command, '\n', inp, out)
    actual_dep = sentinel + m.bytes(addr, dlen) + sentinel

    print(f' exp_dep: {addr-1:04X}: ' \
        + ' '.join(f'{b:02X}' for b in (expected_dep)))
    print(f' act_dep: {m.hexdump(addr-1, dlen+2)}')
    assert      expected_dep == actual_dep, 'deposit'
    assert               b'' == unread_actual, 'unread'
    assert      command + NL == echo, 'echoed command and added newline'

    assert (   record_count+1,   success_count+1) \
        == (m.word(S.vL_calc), m.word(S.vR_calc)) \
        ,  'Record count incremented; success count incremented'

IHE = b'\a\n?\n'        # error indicator: beep and '?' on a new line
IHP = b'.Z'             # prompt and ^Z bad command echoed at `prompt.cmderr`
IH_ = b'00aaaa01cc'     # good end record (note no ':' prefix)
@param( 'rcincr, command, expected', [
    #   Bad hex digit, not CR, returns to prompt 'normally.'
    (0, b':0x\r',           b':0x'              +IHE +IHP), # count
    (0, b':00aaax\r',       b':00aaax'          +IHE +IHP), # addr
    (0, b':00aaaa2x\r',     b':00aaaa2x'        +IHE +IHP), # type
    (0, b':00aaaaFF\r',     b':00aaaaFF'        +IHE +IHP), # type ≠ 0/1
    (0, b':00aaaa02\r',     b':00aaaa02'        +IHE +IHP), # type ≠ 0/1
    (0, b':02aaaa00ddeX\r', b':02aaaa00ddeX'    +IHE +IHP), # data
    (0, b':00aaaa01cX\r',   b':00aaaa01cX'      +IHE +IHP), # checksum
    #   Bad checksum (0, XXX not yet checked)
    #   Bad hex digit is CR or ':'; alternate code path
    (0, b':\r',             b':M'               +IHE +IHP), # restart prompt
    (1, b':0:' +IH_,        b':0:'     +IHE +IH_ +NL +IHP), # restart hex entry
    #   Additional chars all consumed
    (0, b':0x more stuff\r',b':0x'              +IHE +IHP), # \r term
    (1, b':0x also:' +IH_,  b':0x'     +IHE +IH_ +NL +IHP), # : term
])
def test_intelhex_errors(m, S, loadbios, rcincr, command, expected):
    #   rcincr should be set to the number of additional records that
    #   are in the test, if any.
    record_count = randrange(60000); m.depword(S.vL_calc, record_count)
    success_count  = randrange(60000); m.depword(S.vR_calc, success_count)

    command += ZCMD             # bad command if sent back to prompt
    expected = b'.' + expected  # prefix prompt

    inp, out = loadbios(input=command)
    try:
        #   We stop on prompt.cmderr to be able to test that \r takes us
        #   back to the prompt.
        m.call(S['prompt'], stopat=[S['prompt.cmderr']])
    except EOFError as ex:  print(f'OVERRUN! {ex}')

    unread_actual, echo, output = log_interaction(command, expected, inp, out)
    assert expected == output

    assert (   record_count+1+rcincr,   success_count+0+rcincr) \
        == (m.word(S.vL_calc), m.word(S.vR_calc)) \
        ,  'Record count incremented; success count not incremented'

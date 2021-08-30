' b8tool.run - Run and control subprocesses '

import  os, subprocess
from    b8tool  import path

def tool(toolbin, *args, input=None, stdout_path=None, is32bit=False):
    ''' Run `toolbin` with the given `args`. On success this simply
        returns; on failure it prints the command line and the exit code
        and then exits this program. (This makes error output more readable
        than if a Python exception is thrown and printed.)

        `input` is passed directly to `subprocess.run()` and is typically
        a byte string.

        If `stdout_path` is given, that file will be opened in binary mode
        (creating it if necessary) and the standard output of the program
        will be written to it. (No output will produce an empty file.)

        For tools that under Linux are 32-bit binaries, set `is32bit` to
        `True` to have a helpful message printed when the exit code is 127,
        usually indicating that support for running 32-bit binaries is not
        installed.
    '''
    #   Relative `toolbin` uses explict path to project tool, if available.
    b8tool = path.tool('bin', toolbin)
    if os.access(str(b8tool), os.X_OK):
        toolbin = b8tool

    runargs = (str(toolbin),) + tuple(map(str, args))
    if stdout_path is None:
        ret = subprocess.run(runargs, input=input)
    else:
        with open(str(stdout_path), 'wb') as f:
            ret = subprocess.run(runargs, input=input, stdout=f)

    if ret.returncode == 0:
        return
    print('FAILED (exit={}): {} {}'.format(ret.returncode, toolbin,
        ' '.join(map(path.pretty, args))))
    if is32bit and ret.returncode == 127:
        print('(Do you support 32-bit executables?)', file=sys.stderr)
    exit(ret.returncode)


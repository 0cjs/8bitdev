from    pathlib import Path
import  os, shutil, subprocess, sys, traceback

####################################################################
#   Globals

#   From /usr/include/sysexits.h
EX_USAGE        = 64    # Bad command arguments, etc.
EX_UNAVAILABLE  = 69    # A service or support program/file doesn't exist
EX_SOFTWARE     = 70    # (Non-OS) internal software error
EX_CONFIG       = 78    # Configuration error

#   The list of standard subdirectories for build and installation of
#   toolsets under the tool directory, $BUILD/tool/. This follows
#   the standard Unix /usr/local/* arrangement.
PREFIX_SUBDIRS = ('bin', 'doc', 'include', 'lib', 'man', 'share', 'src')

####################################################################
#   printconfig()
#
#   Define printconfig() to print a configuration command to be
#   executed by the caller. This should be bash code, e.g., ``export
#   PATH=...``.
#
#   The string will be printed on file descriptor 3, if it was open
#   when we started, otherwise it it will be printed on stdout
#   prefixed with ``CONFIG: ``, presumably for the user to read and do
#   by hand.
#

try:
    #   Use file descriptor 3, if it's open. This open(3) call can be
    #   done only once per process; it will fail with [Errno 9] Bad
    #   file descriptor if tried a second time.
    config_out = open(3, 'w')
    def printconfig(*s):
        print(*s, file=config_out)
except OSError as e:                     # [Errno 9] Bad file descriptor
    def printconfig(*s):
        print('CONFIG:', *s)

####################################################################
#   Utility routines

def errprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

def errexit(exitcode, *messages):
    errprint(*messages)
    printconfig('return', exitcode)   # Sourced stdout also exits with code.
    sys.exit(exitcode)

def successexit():
    printconfig('return 0')
    sys.exit(0)

def runcmd(command, *, cwd=None):
    ''' Run a command, failing the program with an error message if the
        command fails.

        Stdout is being used for shell commands to be executed by our
        caller, so the subprocess' stdout is sent to stderr.
    '''
    if cwd: cwd = str(cwd)  # Convert Path object for Python ≤3.5
    c = subprocess.run(command, cwd=cwd, stdout=sys.stderr)
    if c.returncode != 0:
        errexit(c.returncode, 'Command failed: {}'.format(command))


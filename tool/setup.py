'''
    Configure use of toolsets, installing if necessary.

    The abstract `Setup` class here contains support code for checking
    whether or not the environment provides a toolset (e.g., an assembler)
    and, if not, doing any of fetching, configuring, building and
    installing (all in the local project build dir) that toolset.

    A subclass of `Setup` should be generated for every toolset. The
    subclass has considerable control over how the process works. It's
    usually in a file that can be run from the command line, so that
    non-Python build tools and humans can easily use it.

    Generally the subclass will prefer to:
      1. Use an already-built version local to the project under .build/.
      2. Use a version provided by the environment.
      3. Fetch, build and install a local version for #1 above.

    Any program importing this file has three output streams: stdout and
    stderr from the program (and any programs it calls) and the
    "configuration output," which prints Bash commands to configure the
    caller to use what it's set up.

    If file descriptor 3 is open when the program is started, the
    configuration commands will be printed to that. The caller is expected
    to execute these, while passing through stdout and stderr, with the
    following Bash magic incantation:

        . <($tool_path 3>&1 1>/proc/$$/fd/1)

    If file descriptor 3 is not open, the configuration commands will be
    printed to stdout, prefixed by ``CONFIG: ``. (The caller can copy these
    and execute them by hand if he likes.)

    TODO:
    - Add ability to force fetch/build/use of local tool version even
      when one is available from the environment.
'''

from    pathlib  import Path
import  abc, os, pathlib, shutil, subprocess, sys, traceback

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

def checkrun(cmdargs, exitcode=0, banner=b''):
    ''' Attempt to execute the given `cmdargs`, a sequence of the
        command name followed by its arguments. If it successfully
        runs, the exit code is `exitcode`, and stdout or stderr contains
        the byte string `banner`, return `True`. Othewrise return `False`.
    '''
    try:
        c = subprocess.run(cmdargs,
            stderr=subprocess.STDOUT, stdout=subprocess.PIPE)
    except FileNotFoundError:
        return False
    if c.returncode != exitcode or banner not in c.stdout:
        return False
    return True

####################################################################
#   Setup class

class Setup(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def toolset_name():
        ''' Return the name of the toolset we're setting up. This will
            be the name of its subdirectory under $basedir/tools/src/.
        '''

    def __init__(self):
        #   Project build directory under which we put our tool/ directory.
        self.builddir = None

    def main(self):
        ''' Run the setup etc. process by calling the `setup` function.

            To help shells scripts sourcing this exit properly when an
            unepxected error occurs, this catches most exceptions that the
            interpreter would otherwise handle, prints an error message as
            the interpreter does, but also generates a `return` command
            with an error exit code on the config channel. (This does not,
            however, catch syntax errors, bad imports and other errors
            that occur before this is called.)
        '''
        try:
            self.setup()
        except Exception as ex:
            printconfig('return', EX_SOFTWARE)
            errprint('INTERNAL ERROR in', sys.argv[0])
            traceback.print_exc()
            sys.exit(EX_SOFTWARE)

    def printaction(self, *args, **kwargs):
        ' Note to stdout an action that is starting. '
        print('-----', self.toolset_name() + ':', *args, **kwargs)

    def pdir(self, dir, *subdirs, create=True):
        ''' Return an absolute path to a subdirectory under the prefix
            ($builddir/tools) we use for toolsets. The first level `dir`
            must be a member of `PREFIX_SUBDIRS`.

            If `create` is `True`, this will create the directory, if
            necessary.
        '''
        if not dir in PREFIX_SUBDIRS:
            raise ValueError('Internal error: {} not in PREFIX_SUBDIRS'.format(dir))

        d = self.builddir.joinpath('tool', dir, *subdirs)
        if create:
            d.mkdir(parents=True, exist_ok=True)
        d = d.resolve()   # strict=False not available in Python ≤3.5, so we
                          # must have created the directories before we resolve.
        return d

    def srcdir(self, resolve=False):
        if not resolve:
            return self.builddir.joinpath('tool', 'src', self.toolset_name())
        else:
            #   Work around not having ``strict=True`` option to
            #   `Path.resolve()` in Python ≤3.5 by resolving `BUILDDIR`
            #   instead, which will always exist if we've reached the point
            #   of needing the target dir.
            return self.builddir.joinpath('tool', 'src') \
                .resolve().joinpath(self.toolset_name())

    def downloaddir(self):
        ''' Return the cache directory for downloaded software. It will be
            created if it does not exist.

            This is at the same level as `builddir`, not underneath it,
            because we don't normally want to re-download these when
            doing a clean build.
        '''
        dir = self.builddir.parent.joinpath('.download')
        #   This should fail if builddir doesn't exist because that
        #   indicates that something likely went wrong earlier in our
        #   setup.
        dir.mkdir(exist_ok=True)
        return dir

    def setbuilddir(self):
        ''' Locate build and target directories.

            If the ``BUILDDIR`` environment variable is set, we use that,
            creating that directory if necessary. Otherwise if ``.build/``
            exists in the current working directory, we use that.
        '''
        if os.environ.get('BUILDDIR', None):
            self.builddir = Path(os.environ['BUILDDIR'])
            for d in PREFIX_SUBDIRS:
                self.builddir.joinpath('tool', d) \
                    .mkdir(parents=True, exist_ok=True)
            return

        if Path('.build').is_dir():
            self.builddir = Path('.build')
            return

    def setpath(self):
        ''' Update ``PATH`` to include the tools we're building.

            XXX This does not work on Windows.
        '''
        if not self.builddir:
            #   Cannot build; must rely on the environment providing the tool.
            return

        path = os.environ.get('PATH', None)
        if path is None:
            errexit(EX_CONFIG, 'ERROR: No PATH variable in environment')
        separator = ':'                     # XXX not right for Windows
        td = str(self.pdir('bin'))
        if td in path:                      # XXX mismatches if substring
            return
        path = td + separator + path
        os.environ['PATH'] = path
        printconfig("PATH='{}'".format(path))

    def fetch(self):        pass
    def configure(self):    pass
    def build(self):        pass
    def install(self):      pass

    def setup(self):
        self.setbuilddir()
        self.setpath()
        self.check_installed()
        if not self.builddir:
            errexit(EX_USAGE,
                'BUILDDIR not set and {} is not a directory.'.format(BUILDDIR))
        else:
            self.fetch()
            self.configure()
            self.build()
            self.install()

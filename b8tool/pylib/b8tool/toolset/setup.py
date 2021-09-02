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

from    b8tool  import path

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
#   XXX The previous version of this was designed to let stand-alone
#   programs print configuration commands to be viewed or run by the caller
#   to configure the environment running the tool. (These would be Bash
#   commands such as ``export PATH=...``.) This should no longer be needed
#   once b8tool is dealing with finding and running commands, but for the
#   moment we just consume and ignore printconfig requests.

def printconfig(*s): pass

#   The previous version of printconfig() would print the string(s) on file
#   descriptor 3, if it was open when we started, otherwise on printed on
#   stdout prefixed with ``CONFIG: ``, presumably for the user to read and
#   do by hand.
#
#   try:
#       #   Use file descriptor 3, if it's open. This open(3) call can be
#       #   done only once per process; it will fail with [Errno 9] Bad
#       #   file descriptor if tried a second time.
#       config_out = open(3, 'w')
#       def printconfig(*s):
#           print(*s, file=config_out)
#   except OSError as e:                     # [Errno 9] Bad file descriptor
#       def printconfig(*s):
#           print('CONFIG:', *s)

####################################################################
#   Utility routines

def errprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr, flush=True)

def errexit(exitcode, *messages):
    errprint(*messages)
    printconfig('return', exitcode)   # Sourced stdout also exits with code.
    sys.exit(exitcode)

def runcmd(command, *, cwd=None, suppress_stdout=False):
    ''' Run a command, failing the program with an error message if the
        command fails.

        Stdout is being used for shell commands to be executed by our
        caller, so the subprocess' stdout is sent to stderr.
    '''
    if suppress_stdout:
        stdout = subprocess.DEVNULL
    else:
        stdout = sys.stderr
    if cwd: cwd = str(cwd)  # Convert Path object for Python ≤3.5
    c = subprocess.run(command, cwd=cwd, stdout=stdout)
    if c.returncode != 0:
        errexit(c.returncode, 'Command failed: {}'.format(command))

def checkrun(cmdargs, exitcode=0, banner=b''):
    ''' Attempt to execute the given `cmdargs`, a sequence of the
        command name followed by its arguments. If it successfully
        runs, the exit code is `exitcode`, and stdout or stderr contains
        the byte string `banner`, return `True`. Othewrise return `False`.
    '''
    b8tool = path.tool('bin', cmdargs[0])
    if os.access(str(b8tool), os.X_OK):
        cmdargs[0] = str(b8tool)

    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT
    try:
        c = subprocess.run(cmdargs, stderr=stderr, stdout=stdout)
    except FileNotFoundError:
        return False
    if c.returncode != exitcode or banner not in c.stdout:
        return False
    return True


####################################################################
#   Generic Setup Class

class Setup(metaclass=abc.ABCMeta):

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

    ####################################################################
    #   Output and printing

    def printaction(self, *args, **kwargs):
        ' Note to stdout an action that is starting. '
        print('-----', self.toolset_name() + ':', *args, **kwargs)

    ####################################################################
    #   Configuration

    def toolset_name(self):
        ''' The toolset name, used among other things for the directory
            name under $basedir/tool/src/, defaults to the name of the
            class in lower case. Override this if necessary.
        '''
        return type(self).__name__.lower()

    ####################################################################
    #   Directory and file handling

    def pdir(self, dir=None, *subdirs, create=True):
        ''' Return an absolute path to the prefix ($builddir/tools) we use
            for toolsets, or a subdirectory under it if `dir` set. `dir`
            must be a member of `PREFIX_SUBDIRS`.

            If `create` is `True`, this will create the directory, if
            necessary.
        '''
        if not dir in (None,) + PREFIX_SUBDIRS:
            raise ValueError(
                'Internal error: {} not in PREFIX_SUBDIRS'.format(dir))

        d = self.builddir.joinpath('tool')
        if dir is not None:
            d = d.joinpath(dir)
        d = d.joinpath(*subdirs)
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
        #   XXX This class should be using path.tool() everywhere.
        self.builddir = path.build()
        for d in PREFIX_SUBDIRS:
            self.builddir.joinpath('tool', d) \
                .mkdir(parents=True, exist_ok=True)

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

    ####################################################################
    #   Implementations of various parts of the setup/config/build/install
    #   process, normally used by the core setup routines defined in
    #   sublcasses.

    def fetch_git(self):
        ''' Clone the source if necessary.

            If `srcdir` does not exist, clone into it from the `source_repo`
            URL. If `source_ref` is set, switch to that branch.
        '''
        if self.srcdir().is_dir():
            self.printaction(
                'Using existing source in {}'.format(self.srcdir()))
            return

        self.printaction('Cloning {} from {}'.format(
            self.toolset_name(), self.source_repo))
        runcmd([ 'git', 'clone', str(self.source_repo), str(self.srcdir()) ])

        if getattr(self, 'source_ref', None):
            self.printaction(
                'Switching to ref or branch {}'.format(self.source_ref))
            runcmd([ 'git', '-C', str(self.srcdir()),
                'checkout', str(self.source_ref) ])


    def check_packages(self, *, debian=[], redhat=[]):
        ''' Check that the given packages are present. This is usually
            used to confirm that we have what we need to build from source.
        '''
        if redhat:
            raise NotImplementedError(
                "I don't know how to check redhat packages yet.")
        if not debian:
            return

        self.printaction('Checking dependencies:', ' '.join(debian))
        runcmd(['dpkg', '-s'] + debian, suppress_stdout=True)

    def make_src(self, *makeargs):
        ''' Run ``make`` in the source directory.

            This provides some standard arguments, including a PREFIX
            definition. Further arguments may be passed as `*makeargs`.
        '''
        prefix = 'PREFIX=' + str(self.pdir())
        cmd = ('make', '-j8', prefix) + makeargs
        self.printaction(*cmd)
        runcmd(cmd, cwd=self.srcdir())

    ####################################################################
    #   High-level setup description

    @abc.abstractmethod
    def check_installed(self):
        ' Return true if the toolset is available in the current path. '

    def fetch(self):
        if getattr(self, 'source_repo', None):
            self.fetch_git()

    def configure(self):
        pass

    def build(self):
        ' Build the tool, rebuilding if any dependencies have changed. '
        pass

    def install(self):
        ''' Install executables in ``pdir('bin')`` etc. '''
        pass

    def setup(self):
        self.setbuilddir()
        self.setpath()
        if self.check_installed():
            #   Already built or system-supplied
            printconfig('return 0')
            return

        if not self.builddir:
            errexit(EX_USAGE,
                'BUILDDIR not set and {} is not a directory.'.format(BUILDDIR))
        self.fetch()
        self.configure()
        self.build()
        self.install()

''' b8tool.path - Define path conventions and build paths

    Everything is relative to a base project directory defined by the
    environment variable ``$B8_BASEDIR``, which must be an absolute path.
    Source code may be anywhere in or under the base directory; other files
    have specific locations defined in docstrings below for the functions
    that generate paths underneath these locations.

    The one path not defined here is b8tool's ``pylib/``; that's added
    to `sys.path` by the b8tool when it starts.

    Source code and data may be placed directly in $B8_BASEDIR but more
    often is under ``src/`` (libraries), ``exe/`` (complete executable
    programs) or other subdirectories.

    Subdirectories under ``$B8_BASEDIR/.build/`` include:
    • ``obj/``: Build output. Paths underneath this will match the path to
      the source code file relative to `$B8_BASEDIR`, e.g., ``src/foo/bar.a65``
      will produce output files ``.build/obj/src/foo/bar.*``.
    • ``tool/bin/``: Project-local binaries for tools used by this project.
      Executable files here will always be used if present, otherwise the
      usual $PATH search will occur.

'''

from    os  import environ
from    pathlib  import Path

B8_BASEDIR = environ.get('B8_BASEDIR')

def base(*components):
    ''' Return absolute `Path` for path `components` relative to `B8_BASEDIR`.

        Most other path functions eventually call this one.
    '''
    return Path(B8_BASEDIR, *components)

def pretty(s):
    ''' If `s` is a path where `B8_BASEDIR` is its prefix, return, `s` with
        that prefix replaced by '$BASEDIR'. Otherwise return `s` unmodified.
        This reduces noise when printing diagnostics while still giving
        complete path information.
    '''
    s = str(s)
    if s.startswith(B8_BASEDIR + '/'):
        return s[len(B8_BASEDIR)+1:]
    else:
        return s

def build(*components):
    ''' The build directory in which we place all generated files for
        this project. This is always a single directory so that it can
        be easily removed when cleaning.

        Standard subdirectories of build include `tool()` and `obj()` and
        one for a Python virtual environment.

        At some point in the future it may be possible to have multiple
        build directories for, e.g., testing with different versions of
        Python or other tools.
    '''
    return base('.build/', *components)

def tool(*components):
    ''' Return a path relative to the local project tools directory.
        Sub-paths under this follow the usual conventions of ``$PREFIX``
        for Unix systems:
        * src/: Fetched/downloaded source code for tools built locally,
          each in a subdirectory named for the tool.
        * bin/: Binaries (or more frequently, symlinks to binaries) for
          local project tools (built from src/ or otherwise).
        * include/, lib/, share/, etc.: Per usual with ``$PREFIX``.
    '''
    return build('tool/', *components)

def obj(*components):
    ''' Given components for a project source path relative to `B8_BASEDIR`,
        return the corresponding object path, which is the same path under
        ``.build/obj/``.
    '''
    return build('obj/', *components)

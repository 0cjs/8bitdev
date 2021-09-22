''' b8tool.path - Define path conventions and build paths

    Everything is relative to a project directory defined by the
    environment variable ``$B8_PROJDIR``, which must be an absolute path.
    Source code may be anywhere in or under the project directory; other
    files have specific locations defined in docstrings below for the
    functions that generate paths underneath these locations.

    The one path not defined here is b8tool's ``pylib/``; that's added
    to `sys.path` by the b8tool when it starts.

    Source code and data may be placed directly in $B8_PROJDIR but more
    often is under ``src/`` (libraries), ``exe/`` (complete executable
    programs) or other subdirectories.

    Subdirectories under ``$B8_PROJDIR/.build/`` include:
    • ``obj/``: Build output. Paths underneath this will match the path to
      the source code file relative to `$B8_PROJDIR`, e.g., ``src/foo/bar.a65``
      will produce output files ``.build/obj/src/foo/bar.*``.
    • ``tool/bin/``: Project-local binaries for tools used by this project.
      Executable files here will always be used if present, otherwise the
      usual $PATH search will occur.

'''

from    pathlib  import Path
import  os

B8_PROJDIR = os.environ.get('B8_PROJDIR')

####################################################################
#   Public API for getting/creating paths

def proj(*components):
    ''' Return absolute `Path` for path `components` relative to `B8_PROJDIR`.

        Most other path functions eventually call this one.
    '''
    if B8_PROJDIR:
        return Path(B8_PROJDIR, *components)
    else:
        raise NameError('B8_PROJDIR not set in environment')

def pretty(s):
    ''' If `s` is a path where `B8_PROJDIR` is its prefix, return, `s` with
        that prefix and its slash removed, i.e. a relative path from
        `B8_PROJDIR`. Otherwise return `s` unmodified. This reduces noise
        when printing diagnostics while still giving complete path
        information.
    '''
    s = str(s)
    if s.startswith(B8_PROJDIR + '/'):
        return s[len(B8_PROJDIR)+1:]
    else:
        return s

def b8home(*components):
    ''' The path to the b8tool repo or installation.

        This assumes that the `__main__` module has figured out where
        the b8tool installation is (since it needed to do this to make
        this module available in the first place) and has set its global
        `B8_HOME` to that. (If it's not, a NameError pointing at this
        function will be raised.)
    '''
    from __main__ import B8_HOME
    return Path(B8_HOME, *components)

def pylib(*components):
    ' The top-level directory of Python libraries supplied by by b8tool. '
    return b8home('pylib', *components)

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
    return proj('.build/', *components)

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
    ''' Given components for a project source path relative to `B8_PROJDIR`,
        return the corresponding object path, which is the same path under
        ``.build/obj/``.
    '''
    return build('obj/', *components)

####################################################################
#   File manipulation

def symlink_tool(targetpath, linkpath):
    ''' Create a symlink to `targetpath` at `tool(linkpath)`, making any
        intermediate directories required. This will silently remove any
        existing file or symlink at `linkpath`.

        `targetpath` may be relative to `proj()`. To help catch developer
        errors, `targetpath` must point to an existing and readable file or
        directory or a `ValueError` will be raised.
    '''
    target = build(targetpath)
    if not os.access(str(target), os.R_OK):
        raise ValueError('Not readable target: {}'.format(pretty(str(target))))
    link = tool(linkpath)
    if link.exists() or link.is_symlink():  # catch dangling symlink
        link.unlink()                       # no `missing_ok` before Py 3.8
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)

def symlink_toolbin(*exepath):
    ''' Create a symlink in `tool('bin/')` named for the last component
        in `exepath` that points to `exepath`. This will silently remove
        any existing file or symlink in tool/bin/. To help catch developer
        errors, `exepath` must point to an executable file or a
        `ValueError` will be raised.
    '''
    file = proj(*exepath)
    if not os.access(str(file), os.X_OK):
        raise ValueError('Not executable file: {}'.format(pretty(str(file))))
    link = tool('bin', file.name)
    symlink_tool(file, link)

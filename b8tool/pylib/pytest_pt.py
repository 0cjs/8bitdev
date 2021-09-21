''' Pytest plugin to find/execute .pt files as tests

    This plugin adds a new collection hook that recognizes files
    ending in ``.pt`` and loads them as test files. The ``python_files``
    `configuration option`_ need not be changed to include ``*.pt``.

    This will work only in Python ≥3.5 because it uses new importlib
    routines. Further, it does not (as traditional pytest did) change
    the import path per ``--import-mode`` to add the directory in
    which the file resides, since this was needed only with the older
    import routines and caused its own set of problems. If you are
    importing from paths that were automatically added, you will need
    to change your test framework configuration to explicitly add the
    necessary paths.

    The module name for file ``foo.pt`` will be ``foo_pt``. This is
    done only to make test framework debugging easier; since these
    modules are not added to `sys.modules`, there should be no problem
    with collisions as there is in standard pytest loading system,
    which is not yet able to use the ``py`` package's
    ``ensuresyspath='importlib'`` option on `pyimport()`.

    Filename collisions in ``__pycache__/`` between pytest-compiled
    and standard-compiled files are not an issue (pytest appends
    ``-pytest-M.N.P.pyc`` to the bytecode filename) but collisions can
    happen if you create both ``foo.pt`` and ``foo_pt.py`` files and
    ask pytest to run both as tests, so don't do that.

    .. _configuration option: https://docs.pytest.org/en/latest/reference.html#hook-reference
'''

import  importlib, importlib.machinery

from    _pytest.assertion.rewrite import assertstate_key
from    py._path.local import LocalPath
import  pytest

PYTEST_CONFIG = None

def pytest_configure(config):
    ''' Cache a copy of the pytest configuration.

        The configuration is needed by our collect_file hook to get a
        reference to pytest's special assertion-rewriting loader, if
        we're using it.
    '''
    global PYTEST_CONFIG
    PYTEST_CONFIG = config

def pt_pyimport(self, modname=None, ensuresyspath=True):
    ''' This replaces the pyimport() method on an instance of
        LocalPath. This version loads modules from files that the
        standard loading mechanim doesn't recognize as containing
        pytest (or even Python) code. It also tweaks the module name
        appropriately.

        Replace `pyimport()` in an instance ``lp`` with
        ``lp.pyimport = pt_pyimport.__get__(lp, LocalPath)``.
    '''

    #   Here we add `_pt` just to help with test framework debugging.
    #   There won't be any collisions in `sys.modules` becuase we
    #   never add the modules we load to it.
    modname = self.purebasename + '_pt'
    path = str(self)

    #   If we are configured to use the assertion-rewriting loader
    #   (_pytest.assertion.rewrite.AssertionRewritingHook), use that
    #   to load the test code. Otherwise use the standard Python loader.
    loader = None
    assertstate = PYTEST_CONFIG._store.get(assertstate_key, None)
    if assertstate:
        loader = PYTEST_CONFIG._store[assertstate_key].hook
    if loader is None:
        loader = importlib.machinery.SourceFileLoader(modname, path)

    spec = importlib.util.spec_from_file_location(modname, path, loader=loader)
    if spec is None:
        #   This should never happen; if it does most likely we mucked up
        #   our loader setup or something like that.
        raise ImportError(
            "Can't create spec for module %s at location %s" % (modname, path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def pytest_collect_file(path, parent):
    #   We handle only files with our custom extension, otherwise we
    #   return `None` to let something else handle it (or not).
    if path.ext != '.pt':
        return None

    #   Replace this LocalPath's `pyimport()` with our custom code.
    path.pyimport = pt_pyimport.__get__(path, LocalPath)

    #   Continue collection exactly as pytest normally does.
    ihook = parent.session.gethookproxy(path)
    return pytest.Module.from_parent(parent, fspath=path)

''' b8tool.tool - classes to set up build tools

    The `TOOLS` dictionary maps tool names to the classes that fetch,
    configure, build and install (into the project build directory) that
    tool.

    XXX This whole system needs to be cleaned up and documented. It's
    currently suffering the hang-over from being ported from a rather
    different version of this system designed for the pre-b8tool
    environment.
'''

TOOLSETS = {}
TOOLSET_NAMES = ['asl', 'asxxxx', 'bm2', 'diskimg', 'dos33fs', 'linapple']

from importlib import import_module
for t in TOOLSET_NAMES:        # deliberately not lazy loading
    m = import_module('b8tool.toolset.' + t)
    TOOLSETS[t] = m.TOOLSET_CLASS

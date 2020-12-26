''' Verbosity level handling for cmtconv.

    cmtconv programs want to be able to print information about what's
    being processed (such as Block data) to aid in developing and
    debugging code to process the various tape formats.

    This is different and separate from traditional logging that other
    Python modules may be doing (not least because verbosity levels are the
    inverse of logging levels--higher verbosity levels correspond to lower
    logging levels), but the standard Python logging library is flexible
    enough to be re-used for this and still work separately from any other
    standard logging being done.

    We set up our own 'cmtconv' Logger object that does not propagate
    messages up to Python's root logger and instead just prints to
    stdout in our own format. Each cmtconv module's logger is a child
    logger of the 'cmtconv' "root" logger; these routines automatically
    select the right child logger and print output in our own format.

    The verbosity levels to be printed are set with `set_verbosity()`;
    these are internally here translated to log level 9 for verbosity
    level 1, log level 8 for verbosity level 2, and so on.

    Client modules will generally just ``from cmtconv.logging import *`` to
    get `v1()` through `v4()` and use those. Since we are using our
    own functions, we can also now use ``{}``/`format()`-style parameter
    substitution in log messages, e.g.,

    ::
        v1('checksum {:02X} calculated for {!r}', checksum, block)

    TODO:
    - Add hexdump routines for dumping binary data.
'''

from    inspect  import currentframe
import  logging

####################################################################
#   Public API

__all__ = ['v1', 'v2', 'v3', 'v4', ]

def v1(message, *args): vN(1, message, *args, up=2)
def v2(message, *args): vN(2, message, *args, up=2)
def v3(message, *args): vN(3, message, *args, up=2)
def v4(message, *args): vN(4, message, *args, up=2)

def vN(verbosity_level, message, *args, up=1):
    ''' Log `message` if the command-line program's verbosity level is at
        least `verbosity_level`, which should be 1 through 4.
        `format(*args)` is called on `message` so you can use ``{}``-style
        substitutions in it.

        The `up` argument is mainly for internal use; it determines how
        many levels back on the call stack we go to get the module name of
        the caller.
    '''
    log_level = ZERO_VERBOSITY_LOG_LEVEL - verbosity_level
    pkg = caller_pkgname(up+1)
    l = logging.getLogger(pkg)

    #   We do our own message.format(*args) processing here because we
    #   can't (easily) change the standard '%'-formatting processing
    #   of Logger.log(). See:
    #   https://github.com/0cjs/sedoc/blob/master/lang/python/logging.md
    #   https://docs.python.org/3/howto/logging-cookbook.html#
    #       using-particular-formatting-styles-throughout-your-application
    l.log(log_level, message.format(*args))

def set_verbosity(n):
    ' Set the global verbosity level for the system from 0 to 4. '
    l = get_cmtconv_logger()
    l.setLevel(ZERO_VERBOSITY_LOG_LEVEL - n)

####################################################################

#   Verbosity is the inverse of logging level: higher verbosity levels
#   must enable lower-level log messages. So we set our base non-verbose
#   level as 10: messages for verbosity level 1 will be logged at level 9,
#   verbosity level 2 at at level 8, and so on.
ZERO_VERBOSITY_LOG_LEVEL = 10

def get_cmtconv_logger():
    ' Return the root logger for the cmtconv system. '
    return logging.getLogger(parent_pkgname())

def parent_pkgname(name=__name__):
    ''' This is used to get the name of our top-level logger for the whole
        cmtconv system. It assumes that this module is directly under
        the top-level package for the system.
    '''
    components = name.split('.')
    if len(components) > 1:
        components = components[:-1]
    return '.'.join(components)

def caller_pkgname(up):
    frame = currentframe()
    while up > 0:
        frame = frame.f_back
        up -= 1
    return frame.f_globals['__name__']

####################################################################
#   Logging initial setup

HANDLER = logging.StreamHandler()
HANDLER.setFormatter(logging.Formatter(style='{', fmt='{name}: {message}'))

def logging_init():
    ''' Set up our logger as independent from the main logging system by
        disabling propagation and using our own handler to send output to
        stdout.
    '''
    l = get_cmtconv_logger()
   #l.disabled = True
    l.propagate = False
    l.addHandler(HANDLER)
    #   XXX For some reason this is reset by the time we get into a unit test.
    l.setLevel(ZERO_VERBOSITY_LOG_LEVEL)

logging_init()

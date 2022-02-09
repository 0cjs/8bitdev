'''
    The Macroassembler AS.

    .. https://github.com/KubaO/asl.git

    This fetches from `ASL.source_repo` and builds the `ASL.source_ref`
    branch.

    See the module documentation for `setup` for more details.

'''

from    os.path  import abspath, dirname
import  shutil, sys

from    b8tool.toolset.setup  import *

class ASL(Setup):

    #   ASL Version Information:
    #
    #   1.42 Builds 205 through at least 218 are broken for 8bitdev; from
    #   205 the "Symbols in Segment NOTHING" section has disappeared from
    #   the .map file (using the default format=MAP) so that user-defined
    #   symbols such as as "negoffcalc equ negoff(no_data_end)" (from
    #   src/asl/simple.asl) as well as predefined symbols such as
    #   "ARCHITECTURE" and "BIGENDIAN" are no longer present in the file.
    #   (A bug report was sent to the as-users@ccac.rwth-aachen.de list on
    #   2022-02-09.)

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://github.com/KubaO/asl.git'
        self.source_ref  = 'dev/cjs/current'
       #self.source_ref  = 'dev/cjs/testing'

    def check_installed(self):
        return checkrun(['asl', '-this-is-not-an-option'], 4,
            b'Invalid option')

    GITIGNORE = '''\
#   .o and .obj are the only two TARG_OBJEXTENSION in Makefile.def-samples/
/*.o
/*.obj
#   These are generated for most executables; wildcard them to save typing.
/*.msg
/*.rsc
#   Generated binaries.
/alink
/asl
/mkdepend
/p2bin
/p2hex
/pbind
/plist
/rescomp
'''

    def configure(self):
        ''' Configure build, if not already done. '''
        if self.srcdir().joinpath('Makefile.def').exists():
            self.printaction('Using existing build configuration')
            return

        self.printaction('Configuring {}'.format(self.srcdir()))

        dot_gitignore = self.srcdir().joinpath('.gitignore')
        with open(str(dot_gitignore), 'wt') as f:
            f.write(self.GITIGNORE)

        mfdef_template = self.srcdir().joinpath(
                'Makefile.def-samples', 'Makefile.def-x86_64-unknown-linux')
        mfdef = self.srcdir().joinpath('Makefile.def')
        shutil.copyfile(str(mfdef_template), str(mfdef))
        with mfdef.open('at') as fd:
            print('\n\n#', '-'*73, file=fd)
            print('# tool/asl/Setup additional configuration\n', file=fd)
            #   These are the two dirs defined when compiling.
            print('LIBDIR =', self.pdir('lib', 'asl'), file=fd)
            print('INCDIR =', self.pdir('include', 'asl'), file=fd)

    def build(self):
        #   Note we avoid building the documentation here.
        self.make_src()

    def install(self):
        ''' For ASL we don't use `make install` because that wants to build the
            documentation, which requires LaTeX and even then tends to drop to
            interactive prompts about missing `german.sty` etc.

            As well, it's nicer four our purposes to use symlinks back to the
            build directory because then a developer tweaking AS can just
            `make` in the source directory to make the new version available to
            the build system.

            So instead we emulate the parts of install.{bat,cmd,sh} we want,
            which is bin/, lib/ (the message files are required) and include/.
        '''

        binfiles = ('asl', 'plist', 'alink', 'pbind', 'p2hex', 'p2bin',)
        for f in binfiles:
            self.symlink_toolbin(self.srcdir(), f)

        #   The localization message files normally go in lib/asl/, but the
        #   programs don't find them there by default (unless perhaps the
        #   prefix is /usr/local/). We could emit a setting for the AS_MSGPATH
        #   environment variable to indicate where they are, but to allow use
        #   of these tools from the command line without running the Setup
        #   script, it seems better to just drop the files into bin/, where the
        #   programs can automatically find them.
        #
        for path in self.srcdir().glob('*.msg'):
            dest = self.pdir('lib', 'asl').joinpath(path.name)
            self.symlink_tool(path, dest)

        srcs = self.srcdir().joinpath('include')
        for src in srcs.glob('**/*'):
            if src.is_dir(): continue
            dest = self.pdir('include', 'asl').joinpath(src.relative_to(srcs))
            self.symlink_tool(src, dest)

TOOLSET_CLASS = ASL

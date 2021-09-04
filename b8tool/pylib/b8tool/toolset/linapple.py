#!/usr/bin/env python3
'''
    Configure for use of the linapple Apple II simulator (emulator).

    This will fetch from `source_repo` and build the `source_ref`
    branch, if necessary.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    b8tool.toolset.setup  import *

class LinApple(Setup):
    pass

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://github.com/linappleii/linapple.git'
        #   Versions before 2e787e97b (2020-05-22) have a broken
        #   dependency graph; you may need to build twice.
        #self.source_repo = 'https://github.com/0cjs/linapple.git'
        #self.source_ref = 'fork/cjs/master'

    def check_installed(self):
        return checkrun(['linapple', '--help'], 0,
            b'show this help message')

    DEPENDENCIES = (
        ('git',                     ('git', '--version')),
        ('imagemagick',             ('convert', '--version')),
        ('libzip-dev',              ('pkg-config', 'libzip')),
        ('libsdl1.2-dev',           ('pkg-config', 'sdl')),
        ('libsdl-image1.2-dev',     ('pkg-config', 'SDL_image')),
        ('libcurl4-openssl-dev',    ('pkg-config', 'libcurl')),
        ('zlib1g-dev',              ('pkg-config', 'zlib')),
    )

    def build(self):
        ''' Build  the tool.

            This is generally expected to rebuild the tool if any files have
            changed in the local source copy.
        '''
        self.make_src()

    def install(self):
        ''' We need to do the install "by hand" because the Makefile
            ``install`` target must be run as root and changes the
            ownership of the installed files to root.
        '''
        #self.make_src('install')

        dest = self.pdir('bin').joinpath('linapple')
        if not dest.exists():
            #   This is $src/bin/linapple in older versions
            self.symlink_toolbin(self.srcdir(), 'build', 'bin', 'linapple')

        #   The only other non-documentation things that get installed are
        #   linapple.conf and Master.dsk, neither of which we need. (The
        #   config and disk iamge will generally be supplied by the test
        #   framework.)

        #   Most of the stuff under res/ in the source directory seems to
        #   be either included in the binary (like font.xpm) or used for
        #   packaging or other non-runtime purposes. The one exception
        #   is the .SYM symbol tables for the debugger, which seem to be
        #   searched for only in the current working directory, anyway.

TOOLSET_CLASS = LinApple

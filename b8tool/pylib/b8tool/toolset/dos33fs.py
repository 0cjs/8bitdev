#!/usr/bin/env python3
'''
    Configure for use of dos33fs-utils used for manipulating
    Apple II files and DOS 3.3 disk images.

    This will fetch from `source_repo` and build the `source_ref`
    branch, if necessary.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    b8tool.toolset.setup import *

class DOS33FS(Setup):

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://github.com/deater/dos33fsprogs.git'
        #   NOTE: Commits on master from c3a278b up to 6b5c361 had an error
        #   that caused the DELETE command to trash the diskette image. See:
        #   https://github.com/deater/dos33fsprogs/issues/11
        #self.source_ref  = '8e05dc8b32be'      # just before c3a278b

    def check_installed(self):
        return checkrun( ['dos33', '-h'], 0,
            b'by Vince Weaver <vince@deater.net>')

    DEPENDENCIES = (
         ('liblz4-dev', ('pkg-config', 'liblz4')),
         ('libpng-dev', ('pkg-config', 'libpng')),
    )

    def build(self):
        self.make_src()

    def install(self):
        dos33 = 'utils/dos33fs-utils'
        basic = 'utils/asoft_basic-utils'
        bins = (
            (dos33,             'char2hex'),
            (dos33,             'dos33'),
            (dos33,             'dos33_text2ascii'),
            (dos33,             'make_b'),
            (dos33,             'mkdos33fs'),
            (basic,             'asoft_compact'),
            (basic,             'asoft_detoken'),
            (basic,             'bin2data'),
            (basic,             'integer_detoken'),
            (basic,             'tokenize_asoft'),
            ('utils/bmp2dhr',   'b2d'),
            )
        for subdir, file in bins:
            self.symlink_toolbin(self.srcdir(), subdir, file)

TOOLSET_CLASS = DOS33FS

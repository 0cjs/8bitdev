#!/usr/bin/env python3
'''
    Fetch disk images used for testing.

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  sys

from    b8tool.toolset.setup  import *


class OSImg(Setup):

    def __init__(self):
        super().__init__()
        self.source_repo = 'https://gitlab.com/retroabandon/osimg.git'

    def check_installed(self):
        #   Since the repo is only data files, we simply check to see
        #   if it's been cloned.
        return self.pdir('src').joinpath('osimg', 'README.md').exists()

TOOLSET_CLASS = OSImg

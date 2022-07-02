#!/usr/bin/env python3
'''
    The ASxxxx assembler suite.

    This fetches the binaries and extracts them, if necessary. The binaries
    are for 32-bit Linux; on 64-bit systems these will error out with "No
    such file or directory" when run unless the 32-bit dynamic linker
    (`ld-linux.so.2`) and libraries are installed. To do this on a 64-bit
    Debian 9 system:

        dpkg --add-architecture i386
        apt update
        apt install libc6-i386

    See the module documentation for `setup` for more details.
'''

from    os.path  import abspath, dirname
import  zipfile

from    b8tool.toolset.setup import *

class ASxxxx(Setup):

    def toolset_name(self):
        return 'asxxxx'

    def __init__(self):
        super().__init__()
        self.source_archive = '5p31_exe_linux.zip'
        self.source_url = 'http://shop-pdp.net/_ftp/asxxxx'
        self.source_sha = \
            '648a11d48daab3b67e97d82221315b074e874ea30b3f0ead2836baec211940c7'

    def check_installed(self):
        ''' *Silently* determine if the toolset is currently available or
            not and exit with success if it is.

            XXX This does not handle the case where the executables have
            been installed but we can't run them because we don't have
            32-bit support installed. Not sure how best to deal with this,
            but maybe checkrun() will throw a useful exception?
        '''
        #   Don't ask why, after displaying the usage message,
        #   the linker exits with 3 but the assemblers exit with 1.
        return  checkrun(['aslink'], 3, b'ASxxxx Linker') \
            and checkrun(['as6500'], 1, b'ASxxxx Assembler')

    def install(self):
        self.printaction('Installing from {}'.format(self.dlfile.name))
        bindir = self.pdir('bin')
        with zipfile.ZipFile(self.dlfile.open('rb')) as zip:
            zip.extractall(str(bindir))
            for filename in zip.namelist():
                #   Make writable by user so subsequent unzip can overwrite
                #   anything that was removed.
                bindir.joinpath(filename).chmod(0o755)

TOOLSET_CLASS = ASxxxx

''' testmc.midump - Dump a memory image in human-readable format

    This currently reads only CoCo Disk BASIC binary files, as
    produced by ASlink. It should be fairly easy to extend to do work
    with 16-bit Intel hex or Motoroala S-record files, though we'd
    have either to add an option to force the file format, try to do
    auto-detection, or both.

    Ouput lines are in a typical standard address/hex/char format,
    though not exactly the same as either `hexdump -C` or `xxd`. The
    biggest difference is that the line address is always a multiple
    of 16 and locations without data are displayed as spaces.

    Lines are displayed in order of memory location, regardless of the
    order of records in the input file. If there are overlapping
    records, separate lines with the same address will be displayed
    for each overlapping 16-byte chunk. Possibly we should emit a
    warning to stderr if overlapping chunks were found during the
    dump.
'''

from    testmc.asxxxx import  MemImage
from    argparse  import ArgumentParser

def dump_memoryimage(mi):
    #   Overlapping records are displayed in adjacent lines.
    #   Possibly we should have an option to warn about this
    #   a bit more clearly.
    for mr in sorted(mi):
        dump_memrecord(mr)

def dump_memrecord(mr):
    #print('MEMRECORD @{:04x}: {}'.format(mr.addr, mr.data))
    print(format_memline(mr.addr, mr.data))
    pos, curaddr = alignmentshift(mr.addr)
    while True:
        curaddr += 16; pos += 16
        curdata = mr.data[pos:pos+16]
        if not curdata: return
        print(format_memline(curaddr, curdata))

def alignmentshift(addr):
    ''' Given an address, return a pair of the offset to the 16-byte
        aligned address at or lower than it, and that aligned address.
    '''
    shift = 0 - addr % 16
    return (shift, addr + shift)

def format_memline(addr, data):
    ''' Given an address and list of integer data starting at that
        address, return a human-readable output line displaying the
        first 16 bytes of those data starting at the the first 16-byte
        aligned address at or below `addr`.

        Missing data positions will be filled in with `None`; data
        `None` indicates that nothing (spaces) should be printed for
        that location.
    '''
    #   Ensure we have at least 16 bytes, filling with `None` on right.
    if len(data) < 16:
        data = tuple(data) + ((None,) * (16-len(data)))

    #   Align our start address down to a 16-byte boundary.
    shift, addr = alignmentshift(addr)
    data = (None,)*(-shift) + tuple(data)

    line = '{:04x}: '.format(addr)
    for i in range(0, 8):
        line += hexfield(data[i])
    line += '- '
    for i in range(8, 16):   line += hexfield(data[i])
    line += ' '
    for i in range(0, 8):   line += charfield(data[i])
    line += ' '
    for i in range(8, 16):   line += charfield(data[i])
    return line

def hexfield(i):
    ' Return string with formatted hex field displaying integer i. '
    if i is None: return '   '
    else:         return '{:02x} '.format(i)

def charfield(i):
    ' Return string with formatted char field displaying integer i. '
    if i is None:
        return ' '
    else:
        if i >= 0x20 and i < 0x7f:
            return chr(i)
        else:
            return '.'

def parseargs():
    p = ArgumentParser(description='midump')
    arg = p.add_argument
    arg('inputfile')
    return p.parse_args()

def main():
    args = parseargs()
    mi = MemImage.parse_cocobin_fromfile(args.inputfile)
    dump_memoryimage(mi)

if __name__ == '__main__': main()

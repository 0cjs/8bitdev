from    collections import namedtuple as ntup

class MemImage(list):
    ''' A memory image, usually loaded from an assembler or linker
        output file, consisting of an entrypoint and a list of
        `MemRecord` data records, each with the memory address at
        which it starts.

        This is a mutable ordered collection. The records are
        not necessarily in order of address, but `sorted()` will
        return the records ordered by address.
    '''

    def __init__(self):
        self.entrypoint = None

    MemRecord = ntup('MemRecord', 'addr data')
    MemRecord.__docs__ = \
        ''' A memory record, with an int starting address and sequence
            of byte values that start at that address.
        '''
    def addrec(self, addr, data):
        self.append(MemImage.MemRecord(addr, data))

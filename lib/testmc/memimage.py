from    collections import namedtuple as ntup

class MemImage(list):
    ''' A memory image, usually loaded from an assembler or linker
        output file, consisting of an entrypoint and a list of
        `MemRecord` or similar data records, each with the memory
        address at which it starts and the data.

        The data records may contain additional information, but
        iterating over the sequence will always return ``(addr,data)``
        tuples.

        This is a mutable ordered collection. The records are
        not necessarily in order of address, but `sorted()` will
        return the records ordered by address.
    '''

    def __init__(self):
        self.entrypoint = None
        self.clear_cache()

    def clear_cache(self):
        ' Clear any cached values that have been calculated. '
        self.startaddr      = None
        self.endaddr        = None  # one past the last address with data
        self.contig_fill    = None
        self.contig_data    = None

    class OverlapError(ValueError):
        pass

    MemRecord = ntup('MemRecord', 'addr data')
    MemRecord.__docs__ = \
        ''' A memory record, with an int starting address and sequence
            of byte values that start at that address.
        '''
    def addrec(self, addr, data):
        self.clear_cache()
        self.append(MemImage.MemRecord(addr, data))

    def __iter__(self):
        return (self.MemRecord(mr.addr, mr.data) for mr in super().__iter__())

    def contiglen(self):
        ''' Return the number of bytes in this image covers from the
            lowest to highest address. This is the number of bytes
            that will be returned by `contigbytes()`.

            This does not check to see if the image has overlapping
            records.
        '''
        if self.startaddr is not None and self.endaddr is not None:
            return self.endaddr - self.startaddr
        endaddr = None
        for mr in sorted(self):
            if len(mr.data) == 0:
                continue                # Ignore empty records
            if self.startaddr is None:
                self.startaddr = mr.addr
            recend = mr.addr + len(mr.data)
            if endaddr is None or endaddr < recend:
                endaddr = recend
        self.endaddr = endaddr
        return self.contiglen()

    def contigbytes(self, fill=0xFF):
        ''' Return the binary contents of this image as a contiguous
            list of bytes from the lowest address to the highest,
            filling in unset areas with `fill`.

            If the image has any overlapping records a `MemOverlap`
            exception will be raised. (Possibly we should add a
            parameter to disable this check.)
        '''
        if fill == self.contig_fill and self.contig_data is not None:
            return self.contig_data

        self.contig_fill = fill
        data = [None] * self.contiglen()
        for mr in self:
            start = mr.addr - self.startaddr
            sl = slice(start, start+len(mr.data))
            for pos, val in enumerate(data[sl], mr.addr):
                if val is not None:
                    raise self.OverlapError(
                        'Data overlap at location ${:04X}'.format(pos))
            data[sl] = list(mr.data)
        self.contig_data = bytes(map(lambda x: fill if x is None else x, data))
        return self.contig_data

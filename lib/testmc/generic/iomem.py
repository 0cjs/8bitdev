''' A memory with (mock) I/O devices.
'''
from    collections.abc  import Container, Sequence
from    io  import BytesIO

class IOMem(bytearray):
    ''' This is a memory and I/O device simulator. Typically it would be
        used as the backing storage for a CPU simulator.

        As well as acting as a memory store with a little more error
        checking than a standard `bytearray`, it also allows attaching
        functions to be called on reads from or writes to particular memory
        addresses to simulate I/O devices. See the `setio()` function for
        details on how to do this.

        To help surface errors when running tests, the following additional
        safety features not usual to Python sequences have been added:
        1. It is not possible to change the length of memory. `del will
           raise a `TypeError` and attempting to replace a slice with a
           value of different length will raise a `ValueError`.
        2. Negative indexes are invalid and will raise an `IndexError`.
        3. Slices that extend beyond the end of the memory are invalid and
           will raise an `IndexError`. (I.e., while `b'01'[:8]` will return
           a two-byte sequence , the same on this will raise an exception.)

        When using this as backing storage for a CPU simulator object, you
        will probably want to use `copyapi()` to copy the public API of
        this to your object so that users don't need to access it through
        your memory attribute (which may be considered private).
    '''

    PUBLIC_API = ('setiostreams', 'streamiof', 'setio')

    def copyapi(self, o):
        for attr in self.PUBLIC_API:
            setattr(o, attr, getattr(self, attr))

    def __init__(self, size=65536):
        super().__init__(size)
        self.iofs = {}          # address → f(location, byte)

    def setiostreams(self, addr, input=None, output=None):
        ''' Attach binary I/O streams to a memory location, and return the
            streams.

            If not provided, `input` and `output` default to a freshly
            instantiated (separate) `BytesIO` for each.

            If `input` has a `read` method it will be used as the source of
            data for reads from `addr`; ``read(1)`` must return a `bytes`
            (or similar) of length 1. Otherwise `input` will be passed to
            `BytesIO()` to be used as the initial value.

            If `output` has a `write` method it will be used as the
            destination of data for writes to `addr`; ``write()`` will be
            given a `bytes` of length 1 for each byte written.
        '''
        if isinstance(addr, Container):
            raise TypeError('setiostreams does not yet support Containers')

        if input is None:
            istream = BytesIO()
        elif callable(getattr(input, 'read', None)):
            istream = input
        else:
            istream = BytesIO(input)

        if output is None:
            ostream = BytesIO()
        elif callable(getattr(output, 'write', None)):
            ostream = output
        else:
            raise ValueError('output has no write() function')

        self.setio(addr, self.streamiof(istream, ostream))
        return istream, ostream

    def streamiof(self, istream, ostream):
        ''' Given a pair of streams (which may be the same stream), return
            an I/O function suitable for passing to `setio()` that will
            read from `istream` and write to `ostream`.
        '''
        def f(_location, byte):
            if byte is not None:
                ostream.write(bytes((byte,)))
                #   In case we're connected to a buffered tty or similar.
                ostream.flush()
            else:
                bs = istream.read(1)
                if len(bs) > 0:
                    return bs[0]
                else:
                    raise EOFError('No more input available from streamiof')
        return f

    def setio(self, addr, iof=None):
        ''' Set a function `iof` to be called on reads from and writes
            to memory address `addr`.

            The first parameter to the function is the memory address that
            was accessed. This can be ignored if the function has no need
            for it.

            The second parameter is `None` for a read, in which case
            the function should return an `int` or similar value, or
            an int or similar value for a write.

            Passing `None` as the function will clear an existing function
            at that address. Multiple functions may not be set at the same
            address; clear an existing function before replacing it.
        '''
        if isinstance(addr, Container):
            raise TypeError('setio does not yet support Containers')
        if isinstance(addr, slice):
            raise TypeError('setio does not yet support slices')

        if (iof is not None) and (not callable(iof)):
            raise ValueError('Not callable: {}'.format(repr(iof)))

        self._check_index(addr)

        if iof is None:
            del self.iofs[addr]
        else:
            if addr in self.iofs:
                raise ValueError('iof function already set at address'
                    ' ${:04X}; remove it first.'.format(addr))
            self.iofs[addr] = iof

    def _slice_to_range(self, s):
        ''' Convert a slice to a range.

            Any and all of a slice's start, stop and step may be done;
            these default to the start of memory, end of memory and 1.

            Unlike ``range(slice.indices(n))``, we do not truncate the
            slice if it's longer than our sequence; we want later to
            generate an `IndexError` so as to surface bugs in memory
            access code.
        '''
        start = 0          if s.start is None  else s.start
        stop  = len(self)  if s.stop  is None  else s.stop
        step  = 1          if s.step  is None  else s.step
        return range(start, stop, step)

    def _check_index(self, addr):
        if addr < 0 or addr >= len(self):
            raise IndexError('Invalid memory address: ${:04X}'.format(addr))

    def __getitem__(self, key):
        if isinstance(key, slice):
            return bytearray(
                ( self[addr] for addr in self._slice_to_range(key) )) # recurse

        self._check_index(key)
        if key in self.iofs:
            return self.iofs[key](key, None)
        return super().__getitem__(key)

    def _badlen(self, alen, vlen):
        msg = "'{}' object cannot change length" \
            + ' (length {} slice had {} value(s) provided)'
        raise ValueError(msg.format(self.__class__.__name__, alen, vlen))

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            addrs = self._slice_to_range(key)
            values = tuple(value)
            if len(addrs) != len(values):
                self._badlen(len(addrs), len(values))
            for a, v in zip(addrs, values):
                self[a] = v  # recurse
            return

        self._check_index(key)
        if key in self.iofs:
            return self.iofs[key](key, value)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        raise TypeError("'{}' object doesn't support item deletion"
            .format(self.__class__.__name__))

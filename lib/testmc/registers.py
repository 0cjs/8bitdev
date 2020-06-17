''' Classes of immutable objects containing register and flag values.
    Values of `None` indicate "don't care" to comparisons and "don't
    change" to update operations.

    Create a class for a specific machine's set of registers and
    flags/status register bits by sublcassing `GenericRegisters` as
    described in its docstring.
'''

from    math  import ceil

class Reg:
    ' A register with a name and width. '
    def __init__(self, name, width=8):
        self.name = name
        self.width = width

    def checkvalue(self, value):
        ' Return `value` if valid, otherwise raise `ValueError()`. '
        if value is None: return value
        maxval = (1 << self.width) - 1
        if value < 0 or value > maxval:
            raise ValueError(
                "Register '{}' value ${:02X} exceeds range $00-${:02X}"
                .format(self.name, value, maxval))
        return value

    def formatvalue(self, value):
        ''' Format `value` as "name=value" where the value will be hyphens
            if ignored or a hexadecimal number otherwise. The width will
            always be exactly the number of digits/chars required for the
            register width.
        '''
        vlen = ceil(self.width / 4)
        if value is None:
            return '{}={}'.format(self.name, '-' * vlen)
        else:
            return '{}={:0{}X}'.format(self.name, value, vlen)

class Bit:
    ''' An unused status register bit that does not correspond to a flag.

        The default value is used when generating a status register value.
    '''
    def __init__(self, default):
        self.name = None
        self.default = default

    valid_bit_values = (None, False, True)

    def checkvalue(self, value):
        ' Return `value` if valid, otherwise raise `ValueError()`. '
        if value in self.valid_bit_values: return value
        raise ValueError("Status bit '{}' value {} not in set {}"
            .format(self.name, value, self.valid_bit_values))

    def formatvalue(self, value):
        ''' Format `value` as ``-`` if ignored, ``.`` if it's the default
            value, or a ``?`` if it's some other value (indicating that you
            should probably look in to how it got set to an invalid value).

            XXX Possibly we should be doing something like ``*`` and ``#``
            for non-default clear and set values.
        '''
        if value is None:
            return '-'
        elif value == self.default:
            return '.'
        else:
            return '?'

class Flag(Bit):
    ''' A flag with a name and default value.

        The default value is used when generating a status register
        value if the flag is set to "don't-care" (`None`).
    '''
    def __init__(self, name, default=False):
        super().__init__(default)
        self.name = name

    def formatvalue(self, value):
        ''' Format `value` as ``-`` if ignored, the name in lower/upper
            case if clear/set, or a ``?`` if it's some other value
            (indicating that you should probably look in to how it got set
            to an invalid value).
        '''
        if value is None:
            return '-'
        elif value == 0:
            return self.name.lower()
        elif value == 1:
            return self.name.upper()
        else:
            return '?'

class GenericRegisters:
    ''' A superclass providing support for "Registers" objects that hold
        register values, pretty-print them and allow comparisons including
        "don't-care" values.

        Subclass this and define the following class attributes:

        * `machname`: (Optional; default is ``CPU``.) Defines a machine
          name (typically the CPU name) to be printed in front of the
          string representation.
        * `registers`: A tuple (or sequence) of `Reg` objects defining
          the machine's register names and widths (in bits). By convention,
          register names are lower case. Define them in the order in which
          you wish them printed in the `str()` output.
        * `srbits`: A tuple (or sequence) of `Bit` and `Flag` objects
          definining the machine's flags and status register bits. (The
          status register is optional; you may use just stand-alone flags.)
          Define these in the MSB to LSB order of the status register. By
          convention, the names are upper case; they will be printed in
          lower case for unset and upper case for set in the string
          representation. You must use `Bit(1)` or `Bit(0)` values for bits
          in the status register that do not correspond to flags.
        * `srname`: The name of the status register, if present. Typically
          ``sr`` or ``psr`` (Program Status Register).

        By convention, register names are lower case and flag names are
        upper case.

        To help catch programming errors, objects have a simple form of
        immutibility after creation: normal attribute assignment or
        deletion will throw an exception. Minor trickery will work around
        this if necessary, but this may break some of the class
        functionality.
    '''

    immutable = False   # during setup only

    machname = 'CPU'

    def __init__(self, **kwargs):
        #   Assert that sublcass was correctly defined or configured.
        self.machname
        self.registers
        self.srbits
        self.srname

        initvals = kwargs.copy()

        for regspec in self.registers:
            self.__setattr__(regspec.name,
                regspec.checkvalue(initvals.pop(regspec.name, None)))

        if self.srname and self.srname in initvals:
            self._init_with_sr(initvals)
        else:
            self._init_with_flags(initvals)

        if len(initvals) > 0:   # Unknown keyword parameters on instantiation?
            name = tuple(initvals.keys())[0]
            raise TypeError(
                "__init__() got an unexpected keyword argument '{}'"
                .format(name))

        self._init_repr()

        self.immutable = True   # new instance value overrides class value

    def _init_with_flags(self, initvals):
        for srbit in self.srbits:
            if srbit.name:
                self.__setattr__(srbit.name,
                    srbit.checkvalue(initvals.pop(srbit.name, None)))
        if self.srname:
            #   Generate status register
            srval = 0
            for srbit in self.srbits:
                v = None
                if srbit.name:  v = getattr(self, srbit.name, None)
                if v is None:   v = srbit.default
                srval = (srval << 1) | srbit.checkvalue(v)
            setattr(self, self.srname, srval)


    def _init_with_sr(self, initvals):
        initsr = initvals.pop(self.srname, None)
        setattr(self, self.srname, initsr)

        nextbits = initsr
        for srbit in self.srbits[::-1]:
            if srbit.name in initvals:
                raise ValueError(
                    "Cannot specify status bit values for both '{}' and '{}'"
                    .format(self.srname, srbit.name))
            if srbit.name:
                setattr(self, srbit.name, bool(nextbits & 1))
            nextbits = nextbits >> 1
        if nextbits > 0:
            raise ValueError('Too many status bit values: ${:X}'.format(initsr))

    ####################################################################
    #   Immutability support

    def _check_immutable(self, name):
        if not self.immutable:  return
        getattr(self, name)     # Raise AttributeError if invalid name
        raise TypeError(
            "'{}' object is immutable".format(self.__class__.__name__))

    def __setattr__(self, name, value):
        self._check_immutable(name)
        super().__setattr__(name, value)

    def __delattr__(self, name):
        self._check_immutable(name)
        super().__delattr__(name)

    ####################################################################
    #   String representations

    def __repr__(self):
        return self._repr

    def _init_repr(self):
        repr = self.machname
        for reg in self.registers:
            repr += ' ' + reg.formatvalue(getattr(self, reg.name))
        if self.srbits:
            repr += ' '
        for srbit in self.srbits:
            if srbit.name:
                v = getattr(self, srbit.name)
            else:
                v = None    # XXX should come from status register?
            repr += srbit.formatvalue(v)
        self._repr = repr

    ####################################################################
    #   Equality comparisons

    def __eq__(a, b):
        ''' Compare all register and flag values in `a` and `b` where
            neither one is `None`. This does not include the status
            register in the comparison.
        '''
        if type(a) != type(b): return False

        def comp(a, b):     # should we compare a and b?
            return a is not None and b is not None

        for reg in a.registers:
            aval = getattr(a, reg.name)
            bval = getattr(b, reg.name)
            if comp(aval, bval) and aval != bval:
                return False

        for srbit in a.srbits:
            if srbit.name is None:
                continue
            aval = getattr(a, srbit.name)
            bval = getattr(b, srbit.name)
            if comp(aval, bval) and aval != bval:
                return False

        return True

''' Classes of immutable objects containing register and flag values.

    Each register and flag is *valued* (has a non-`None` value) or
    *non-valued* (has a value of `None` meaning "don't care.") Non-valued
    registers are not included in comparisons or update operations.

    Create a class for a specific machine's set of registers and
    flags/status register bits by subclassing `GenericRegisters` as
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
        value if the flag non-valued (i.e., is `None`).
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
        register and flag values, pretty-print them, and ignore non-valued
        registers and flags in comparisions.

        Subclass this and define the following class attributes:

        * `machname` (optional; default ``CPU``): Defines a machine
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
        * `srname` (optional): The name of the status pseudo-register,
          typically used for flags pushed on the stack. (Common names are
          ``sr``, ``psr`` (Program Status Register) or ``cc`` (Condition
          Codes).) This is a word of `srbits` size containing the flags and
          any constant 1 or 0 bits in the order defined in `srbits`. If
          present, the `Registers` may be initialized with either
          individual flag values or an `srname` value and both will be
          available to be read.

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

    def _srname(self):
        ''' Return value of optional `srname` property if present,
            otherwise `None`.
        '''
        #   This is not a class method since an instance property would
        #   override the class property when accessed in the normal way,
        #   as it is in various places. Clients without an instance may
        #   just instantiate an "empty" instance to use this.
        return getattr(self, 'srname', None)

    def __init__(self, **kwargs):
        #   Assert that sublcass was correctly defined or configured.
        self.machname
        self.registers
        self.srbits

        initvals = kwargs.copy()

        for regspec in self.registers:
            self.__setattr__(regspec.name,
                regspec.checkvalue(initvals.pop(regspec.name, None)))

        if self._srname() in initvals:
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
        if self._srname():
            #   Generate status register
            srval = 0
            for srbit in self.srbits:
                v = None
                if srbit.name:  v = getattr(self, srbit.name, None)
                if v is None:   v = srbit.default
                srval = (srval << 1) | srbit.checkvalue(v)
            setattr(self, self.srname, srval)


    def _init_with_sr(self, initvals):
        #   If this is called, the class must have an `srname` property.
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
    #   Copies and modifications

    def valued(self):
        ''' Produce a `dict` of the valued registers and flags of this
            object. This is suitable for use as the argument list to the
            constructor.

            This always produces flag entries, never a status register.
            This isn't a limitation since it's trivial to generate
            the status register value if necessary (and if the class
            has one) by constructing an object with these parameters.
        '''
        d = {}
        for reg in self.registers:
            v = getattr(self, reg.name)
            if v is not None:
                d[reg.name] = v
        for srbit in self.srbits:
            if not srbit.name:  continue
            v = getattr(self, srbit.name)
            if v is not None:
                d[srbit.name] = v
        return d

    def all(self):
        ''' Produce a `dict` of all the registers and flags (valued and
            non-valued) of this object. This is suitable for use as the
            argument list to the constructor.

            This always produces flag entries, never a status register.
            This isn't a limitation since it's trivial to generate
            the status register value if necessary (and if the class
            has one) by constructing an object with these parameters.
        '''
        d = {}
        for reg in self.registers:
            v = getattr(self, reg.name)
            d[reg.name] = v
        for srbit in self.srbits:
            if not srbit.name:  continue
            v = getattr(self, srbit.name)
            d[srbit.name] = v
        return d

    def clone(self, **changes):
        ''' Produce a clone of this Registers object. `changes` is an
            optional list of registers and/or flags with new values to
            replace in the clone current values from this object.

            This does not allow a status register argument in `changes`;
            you must use individual flags.
        '''
        return self.__class__(**dict(self.valued(), **changes))

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

    ####################################################################
    #   Setting and retrieving register/flag values on other objects

    def set_attrs_on(self, o, setsr, *, regtype=None):
        ''' Set our valued register and flag values as attributes on
            another object.

            All valued registers and flags will have same-named attributes
            on `o` set to those values. The values will first be passed to
            the function `regtype` for conversion, if `regtype` not `None`.

            If `setsr` is false, valued flags will be set as individual
            attributes (always converted with `bool()`) in the same way.

            If `setsr` is true, instead the attribute named by `srname`
            will be read, the bits for valued flags set and cleared in it,
            and the attribute set to that new value. There is currently no
            way to have it set the unused or constant bits in the status
            register (defined with `Bit()`).
        '''
        if regtype is None:
            regtype = lambda x: x

        for reg in self.registers:
            val = getattr(self, reg.name)
            if val is not None:
                setattr(o, reg.name, regtype(val))

        if not setsr:
            for flag in self.srbits:
                if flag.name is not None:
                    val = getattr(self, flag.name)
                    if val is not None:
                        setattr(o, flag.name, bool(val))
        else:
            if not self._srname():
                raise AttributeError('{} for {} has no status register'
                    .format(type(self).__name__, self.machname))
            sr = getattr(o, self.srname)
            for i, srbit in enumerate(self.srbits[::-1]):
                if srbit.name is not None:
                    val = getattr(self, srbit.name)
                    if val is None:
                        continue
                    elif val:
                        sr |= 1 << i
                    else:
                        sr &= ~(1 << i)
            setattr(o, self.srname, sr)

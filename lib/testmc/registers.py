''' Mixin for adding registers and flags to a test machine.

    Inheriting `HasRegisters` this enables the `RegistersSetup` functions
    during class definition that let you define registers and flags that
    will be attributes on instantiations of your class. The attributes that
    are added will not allow users to set them to invalid values.

    An additional (read-only) `Registers` attribute contains a class object
    whose instances have attributes only for the registers and flags
    defined above. These attributes allow an additional value of `None`,
    meaning "don't care." Such values do not trigger difference in
    comparisons (if register ``a`` is `None` in one `Registers` instance,
    it will compare equal with any value of ``a`` in the second instance)
    and do not change current values when passed to `setreg()`. These
    objects will also produce nice printable representations of the
    registers and flags

    The following additional functions, taking and returning Registers
    values, will also be added to the class:

    - `regs()`: Return a Registers instance containing the current register
      and flag values of the owning object. None of the attributes will
      ever be set to "don't care."

    - `setregs(r)`: Given a Registers instance _r_, set all register/flag
      attributes on the owning object to those from _r_, not changing any
      owned values that are "don't care" in _r_.
'''

#   XXX The naming here is still kind of awkward; we need to find a way to
#   clearly distinguish:
#   1. The class you inherit to get Register functionality. Currently,
#      HasRegisters.
#   2. The class that has this Register functionality (along with
#      additional information and functionality) and holds the current
#      values of the registers. Currently often called Machine.
#   3. The class holding only register information and allowing don't-care
#      values, used for setting and comparisons. Currently "Registers"
#      above.

#   Not sure if it's clear, but though regs() and setregs() give us full
#   access to all the registers and flags, we still add an individual
#   attribute for each one because in many situations, especially in the
#   internal workings of Machine, it's easier and clearer to access
#   `self.pc` or whatever than create a new Registers object and pass it
#   to setregs(). Or is it?

__all__ = ['HasRegisters']

class RegistersSetup:
    ''' During class definition collects information about the registers
        and flags that the class should have, and then sets up the
        register/flag attributes.
    '''

    ####################################################################
    #   Functions for use during class definition.

    def register(self, name, width=8):
        ''' Define a register with the given `name` and `width` in bits.
        '''
        self.registers.append((name, width))

    ####################################################################
    #   The machinery that implments the class setup.

    def __init__(self):
        self.registers = []

    def _class_def_namespace(self):
        ''' Return a namespace to be used during class definition. This
            will includes the "meta" functions that define registers, and
            this object itself for later use by `__new__()`. This
            should be returned by `__prepare__()`.
        '''
        return {
            '__register_setup': self,
            'register': self.register,
        }

    def _setup_class(self, cls):
        ''' From the lists of registers and flags collected during class
            definition, set up the attributes/accessors and the
            `__init__()` function on the given class object.
        '''

        #   Substitute an __init__ function that does our own setup and
        #   then calls the class's init function (either the default
        #   do-nothing one or, importantly, the user-defined one).
        classinit = cls.__init__
        def init(obj, *args, **kwargs):
            classinit(obj, *args, **kwargs)
        cls.__init__ = init
        for (name, width) in self.registers:
            setattr(cls, name, RegisterDescriptor(name, width))

        cls.Registers = None        # XXX the Registers class, read-only
        cls.regs = None             # regs(self) function
        cls.setregs = None          # setregs(self, registers) function

class RegisterDescriptor:
    ''' Using the descriptor protocol, implement value storage for
        and access to a register.
    '''

    #   N.B.: The descriptor protocol to access instance attributes is:
    #
    #       type(o).__dict__['x'].__get__(o, type(o))
    #
    #   Thus you must bind **the class attribute** to an object
    #   implementing the descriptor protocol, not the instance attribute.
    #
    #   The docs say that the default lookup order for instance attributes
    #   is `a.__dict__['x']` then `type(a).__dict__['x']` but this is not
    #   the case when a descriptor is set as above; perhaps this is
    #   actually describing the default descriptor implementation. This
    #   should probably be worked out at some point; maybe start out with
    #   PEP 252.

    def __init__(self, name, width):
        self.name = name
        self.value = 0
        self.width = width; self.minval = 0; self.maxval = (1 << width) - 1

    #   We ignore the obj on which we're an attribute because we handle our
    #   values entirely internally. XXX is this correct?

    def __get__(self, instance, owner=None):
        return self.value

    def __set__(self, instance, value):
        if value < self.minval or value > self.maxval:
            raise ValueError(
                '{} value out of range ${:02X}-${:02X}: ${:02X}'
                .format(self.name, self.minval, self.maxval, value))
        self.value = value


class HasRegistersMeta(type):

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        namespace = super().__prepare__(name, bases, **kwds)
        return RegistersSetup()._class_def_namespace()

    def __new__(thisclass, name, bases, classdict):
        ''' After class definition has completed executing, create the
            attributes/accessors for the registers and flags, and the
            `__init__()` function.
        '''
        #print('__new__:', thisclass, name, '\n    ', bases, '\n    ', classdict)
        newclass = super().__new__(thisclass, name, bases, classdict)
        setup = classdict['__register_setup']
        setup._setup_class(newclass)
        return newclass

class HasRegisters(metaclass=HasRegistersMeta):
    ''' Inherit from this class to gain functions for use at class
        definition time to define in that class registers and flags, their
        accessors and an appropriate __init__ function.

        See the `RegistersSetup` instance methods for details about the
        functions provided.
    '''
    # XXX document this better

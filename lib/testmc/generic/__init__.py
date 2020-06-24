''' testmc.generic - generic machine support

    The modules here contain an API and generic support for test machines
    on which you can manipulate memory and registers and execute code.

    Generally, `testmc.generic.machine.GenericMachine` will be subclassed
    to make a test machine for a particular CPU (and perhaps other hardware).
    The subclass need only implement a few lower-level details to let the
    generic API then do much of the work of providing the interface.
'''

from testmc.generic.machine import GenericMachine
from testmc.generic.registers import GenericRegisters, Reg, Flag, Bit
from testmc.generic.iomem  import IOMem

#   This is all that most implementations will need to implement the API.
__all__ = [
    'GenericMachine',
    'GenericRegisters', 'Reg', 'Flag', 'Bit',
    'IOMem',
    ]

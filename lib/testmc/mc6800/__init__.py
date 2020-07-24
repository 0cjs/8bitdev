''' A quickly hacked and incomplete Motorola MC6800 simulator.

    This is designed for unit-testing MC6800 code, not to be a complete
    simulation.
'''

from    testmc.mc6800.machine  import LSB, MSB, Machine
from    testmc.mc6800.opcodes  import Instructions

__all__ = ['LSB', 'MSB', 'Machine', 'Instructions']

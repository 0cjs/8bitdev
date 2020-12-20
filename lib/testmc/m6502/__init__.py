''' testmc.m6502 - test framework for 6502 microcomputer code

    This uses the py65 emulator to emulate a 6502 microcomputer system.
'''

from    testmc.m6502.instructions  import Instructions
from    testmc.m6502.machine  import Machine

I = Instructions

__all__ = ['Machine', 'Instructions', 'I']

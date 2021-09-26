''' testmc.mos65 - test framework for 6502 microcomputer code

    This uses the py65 emulator to emulate a 6502 microcomputer system.
'''

from    testmc.mos65.instructions  import Instructions
from    testmc.mos65.machine  import Machine

I = Instructions

__all__ = ['Machine', 'Instructions', 'I']

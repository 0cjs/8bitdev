''' Opcode and instruction mappings.
'''

from    testmc.mc6800.opimpl  import *

####################################################################
#   Map opcodes to mnemonics and implementations.
#   See `Instructions` below for mnemonic naming.

OPCODES = {
    0x86: ('LDAA', ldaa),
}

####################################################################
#   Map instructions to opcodes

class Instructions:
    ''' Opcode constants for the 6800, named after the assembly instructions.

        There are often multiple opcodes per instruction, one for each of
        the different addressing modes. We distinguish these with a
        lower-case suffix:

            Suffix  Asm     Description
            -------------------------------------------------------
                            implied
                    #nn     immediate
              z     nn      zero page
              a     addr    absolute (extended)
              x     n,X     indirect via offset + [X register]

        One day we might find it worthwhile to have an Assembler class that
        can itself determine correct addressing modes and whatnot when
        assembling instructions, but there doesn't seem to be any
        gain from that at the moment.
    '''

for opcode, (mnemonic, f) in OPCODES.items():
    setattr(Instructions, mnemonic, opcode)

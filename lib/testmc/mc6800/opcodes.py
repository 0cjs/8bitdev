''' Opcode and instruction mappings.
'''

from    testmc.mc6800.opimpl  import *

__all__ = ( 'OPCODES', 'Instructions', 'InvalidOpcode' )

####################################################################
#   Map opcodes to mnemonics and implementations.
#   See `Instructions` below for mnemonic naming.

OPCODES = {

    0x00: (None,    invalid),
    0x01: ('NOP',   lambda m: None),
    0x02: (None,    invalid),
    0x03: (None,    invalid),
    0x04: (None,    invalid),
    0x05: (None,    invalid),
    0x06: ('TAP',   tap),
    0x07: ('TPA',   tpa),
    0x08: ('INX',   inx),
    0x09: ('DEX',   dex),
    0x0A: ('CLV',   lambda m: setattr(m, 'V', 0)),
    0x0B: ('SEV',   lambda m: setattr(m, 'V', 1)),
    0x0C: ('CLC',   lambda m: setattr(m, 'C', 0)),
    0x0D: ('SEC',   lambda m: setattr(m, 'C', 1)),
    0x0E: ('CLI',   lambda m: setattr(m, 'I', 0)),
    0x0F: ('SEI',   lambda m: setattr(m, 'I', 1)),

    0x12: (None,    invalid),
    0x13: (None,    invalid),
    0x14: (None,    invalid),
    0x15: (None,    invalid),
    0x18: (None,    invalid),
    0x1A: (None,    invalid),
    0x1C: (None,    invalid),
    0x1D: (None,    invalid),
    0x1E: (None,    invalid),
    0x1F: (None,    invalid),

    0x20: ('BRA',   bra),
    0x21: (None,    invalid),
    0x24: ('BCC',   bcc),
    0x25: ('BCS',   bcs),
    0x26: ('BNE',   bne),
    0x27: ('BEQ',   beq),
    0x28: ('BVC',   bvc),
    0x29: ('BVS',   bvs),
    0x2A: ('BPL',   bpl),
    0x2B: ('BMI',   bmi),

    0x32: ('PULA',  pula),
    0x36: ('PSHA',  psha),
    0x38: (None,    invalid),
    0x39: ('RTS',   rts),
    0x3A: (None,    invalid),
    0x3C: (None,    invalid),
    0x3D: (None,    invalid),

    0x41: (None,    invalid),
    0x42: (None,    invalid),
    0x44: ('LSRA',  lsra),
    0x45: (None,    invalid),
    0x46: ('RORA',  rora),
    0x47: ('ASRA',  asra),
    0x48: ('ASLA',  asla),
    0x49: ('ROLA',  rola),
    0x4B: (None,    invalid),
    0x4E: (None,    invalid),
    0x4F: ('CLRA',  clra),

    0x51: (None,    invalid),
    0x52: (None,    invalid),
    0x55: (None,    invalid),
    0x58: ('ASLB',  aslb),
    0x5A: ('DECB',  decb),
    0x5B: (None,    invalid),
    0x5E: (None,    invalid),
    0x5F: ('CLRB',  clrb),

    0x61: (None,    invalid),
    0x62: (None,    invalid),
    0x65: (None,    invalid),
    0x68: ('ASLx',  aslx),
    0x6B: (None,    invalid),
    0x6E: ('JMPx',  jmpx),
    0x6F: ('CLRx',  clrx),

    0x71: (None,    invalid),
    0x72: (None,    invalid),
    0x75: (None,    invalid),
    0x78: ('ASLm',  aslm),
    0x7B: (None,    invalid),
    0x7E: ('JMP',   jmp),
    0x7F: ('CLRm',  clrm),

    0x80: ('SUBA',  suba),
    0x81: ('CMPA',  cmpa),
    0x83: (None,    invalid),
    0x84: ('ANDA',  anda),
    0x86: ('LDAA',  ldaa),
    0x87: (None,    invalid),
    0x8B: ('ADDA',  adda),
    0x8C: ('CPX',   cpx),
    0x8D: ('BSR',   bsr),
    0x8F: (None,    invalid),

    0x93: (None,    invalid),
    0x96: ('LDAAz', ldaaz),
    0x9C: ('CPXz',  cpxz),
    0x9D: (None,    invalid),

    0xA3: (None,    invalid),
    0xA6: ('LDAAx', ldaax),
    0xA7: ('STAAx', staax),
    0xAD: ('JSRx',  jsrx),

    0xB3: (None,    invalid),
    0xB6: ('LDAAm', ldaam),
    0xB7: ('STAAm', staam),
    0xBC: ('CPXm',  cpxm),
    0xBD: ('JSR',   jsr),

    0xC3: (None,    invalid),
    0xC6: ('LDAB',  ldab),
    0xC7: (None,    invalid),
    0xCC: (None,    invalid),
    0xCD: (None,    invalid),
    0xCE: ('LDX',   ldx),
    0xCF: (None,    invalid),

    0xD3: (None,    invalid),
    0xD6: ('LDABz', ldabz),
    0xDC: (None,    invalid),
    0xDD: (None,    invalid),
    0xDE: ('LDXz',  ldxz),
    0xDF: ('STXz',  stxz),

    0xE3: (None,    invalid),
    0xE6: ('LDABx', ldabx),
    0xE7: ('STABx', stabx),
    0xEC: (None,    invalid),
    0xED: (None,    invalid),
    0xEE: ('LDXx',  ldxx),

    0xF3: (None,    invalid),
    0xF6: ('LDABm', ldabm),
    0xF7: ('STABm', stabm),
    0xFC: (None,    invalid),
    0xFD: (None,    invalid),
    0xFE: ('LDXm',  ldxm),
    0xFF: ('STXm',  stxm),

}

####################################################################
#   Map instructions to opcodes

class InstructionsClass:
    ''' Opcode constants for the 6800, named after the assembly instructions.

        These are available both as attributes on the class or object
        (``I.LDABx``) and via subscript lookup (``I['LDABx']``).

        There are often multiple opcodes per instruction, one for each of
        the different addressing modes. We distinguish these with a
        lower-case suffix:

            Suffix  Asm     Description
            -------------------------------------------------------
                            implied
                    #nn     immediate
              z     nn      memory: direct page ($00-$FF)
              m     addr    memory: absolute (extended)
              x     n,X     indirect via offset + [X register]

        One day we might find it worthwhile to have an Assembler class that
        can itself determine correct addressing modes and whatnot when
        assembling instructions, but there doesn't seem to be any
        gain from that at the moment.
    '''

    def __getitem__(self, key):
        ' Return the opcode value for the given opcode name. '
        return getattr(self, key)

#   Add all opcode names as attributes to InstructionsClass.
for opcode, (mnemonic, f) in OPCODES.items():
    if mnemonic is not None:
        setattr(InstructionsClass, mnemonic, opcode)

Instructions = InstructionsClass()

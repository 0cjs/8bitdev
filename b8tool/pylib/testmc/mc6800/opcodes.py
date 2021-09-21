''' Opcode and instruction mappings.
'''

from    testmc.mc6800.opimpl  import *

__all__ = ( 'OPCODES', 'Instructions', 'InvalidOpcode' )

####################################################################
#   Map opcodes to opcode mnemonics and implementations.
#   See `Instructions` below for mnemonic naming.

OPCODES = {

    0x00: (None,    invalid),       0x10: ('SBA',   sba),
    0x01: ('NOP',   lambda m:None), 0x11: ('CBA',   cba),
    0x02: (None,    invalid),       0x12: (None,    invalid),
    0x03: (None,    invalid),       0x13: (None,    invalid),
    0x04: (None,    invalid),       0x14: (None,    invalid),
    0x05: (None,    invalid),       0x15: (None,    invalid),
    0x06: ('TAP',   tap),           0x16: ('TAB',   tab),
    0x07: ('TPA',   tpa),           0x17: ('TBA',   tba),
    0x08: ('INX',   inx),           0x18: (None,    invalid),
    0x09: ('DEX',   dex),           # 19: ('DAA',   daa),
    0x0A: ('CLV',   clv),           0x1A: (None,    invalid),
    0x0B: ('SEV',   sev),           0x1B: ('ABA',   aba),
    0x0C: ('CLC',   clc),           0x1C: (None,    invalid),
    0x0D: ('SEC',   sec),           0x1D: (None,    invalid),
    0x0E: ('CLI',   cli),           0x1E: (None,    invalid),
    0x0F: ('SEI',   sei),           0x1F: (None,    invalid),

    0x20: ('BRA',   bra),           0x30: ('TSX',   tsx),
    0x21: (None,    invalid),       0x31: ('INS',   ins),
    0x22: ('BHI',   bhi),           0x32: ('PULA',  pula),
    0x23: ('BLS',   bls),           0x33: ('PULB',  pulb),
    0x24: ('BCC',   bcc),           0x34: ('DES',   des),
    0x25: ('BCS',   bcs),           0x35: ('TXS',   txs),
    0x26: ('BNE',   bne),           0x36: ('PSHA',  psha),
    0x27: ('BEQ',   beq),           0x37: ('PSHB',  pshb),
    0x28: ('BVC',   bvc),           0x38: (None,    invalid),
    0x29: ('BVS',   bvs),           0x39: ('RTS',   rts),
    0x2A: ('BPL',   bpl),           0x3A: (None,    invalid),
    0x2B: ('BMI',   bmi),           0x3B: ('RTI',   rti),
    0x2C: ('BGE',   bge),           0x3C: (None,    invalid),
    0x2D: ('BLT',   blt),           0x3D: (None,    invalid),
    0x2E: ('BGT',   bgt),           # 3E: ('WAI',   wai),
    0x2F: ('BLE',   ble),           0x3F: ('SWI',   swi),

    0x40: ('NEGA',  nega),          0x50: ('NEGB',  negb),
    0x41: (None,    invalid),       0x51: (None,    invalid),
    0x42: (None,    invalid),       0x52: (None,    invalid),
    0x43: ('COMA',  coma),          0x53: ('COMB',  comb),
    0x44: ('LSRA',  lsra),          0x54: ('LSRB',  lsrb),
    0x45: (None,    invalid),       0x55: (None,    invalid),
    0x46: ('RORA',  rora),          0x56: ('RORB',  rorb),
    0x47: ('ASRA',  asra),          0x57: ('ASRB',  asrb),
    0x48: ('ASLA',  asla),          0x58: ('ASLB',  aslb),
    0x49: ('ROLA',  rola),          0x59: ('ROLB',  rolb),
    0x4A: ('DECA',  deca),          0x5A: ('DECB',  decb),
    0x4B: (None,    invalid),       0x5B: (None,    invalid),
    0x4C: ('INCA',  inca),          0x5C: ('INCB',  incb),
    0x4D: ('TSTA',  tsta),          0x5D: ('TSTB',  tstb),
    0x4E: (None,    invalid),       0x5E: (None,    invalid),
    0x4F: ('CLRA',  clra),          0x5F: ('CLRB',  clrb),

    0x60: ('NEGx',  negx),          0x70: ('NEGm',  negm),
    0x61: (None,    invalid),       0x71: (None,    invalid),
    0x62: (None,    invalid),       0x72: (None,    invalid),
    0x63: ('COMx',  comx),          0x73: ('COMm',  comm),
    0x64: ('LSRx',  lsrx),          0x74: ('LSRm',  lsrm),
    0x65: (None,    invalid),       0x75: (None,    invalid),
    0x66: ('RORx',  rorx),          0x76: ('RORm',  rorm),
    0x67: ('ASRx',  asrx),          0x77: ('ASRm',  asrm),
    0x68: ('ASLx',  aslx),          0x78: ('ASLm',  aslm),
    0x69: ('ROLx',  rolx),          0x79: ('ROLm',  rolm),
    0x6A: ('DECx',  decx),          0x7A: ('DECm',  decm),
    0x6B: (None,    invalid),       0x7B: (None,    invalid),
    0x6C: ('INCx',  incx),          0x7C: ('INCm',  incm),
    0x6D: ('TSTx',  tstx),          0x7D: ('TSTm',  tstm),
    0x6E: ('JMPx',  jmpx),          0x7E: ('JMP',   jmp),
    0x6F: ('CLRx',  clrx),          0x7F: ('CLRm',  clrm),

    0x80: ('SUBA',  suba),          0x90: ('SUBAz', subaz),
    0x81: ('CMPA',  cmpa),          0x91: ('CMPAz', cmpaz),
    0x82: ('SBCA',  sbca),          0x92: ('SBCAz', sbcaz),
    0x83: (None,    invalid),       0x93: (None,    invalid),
    0x84: ('ANDA',  anda),          0x94: ('ANDAz', andaz),
    0x85: ('BITA',  bita),          0x95: ('BITAz', bitaz),
    0x86: ('LDAA',  ldaa),          0x96: ('LDAAz', ldaaz),
    0x87: (None,    invalid),       0x97: ('STAAz', staaz),
    0x88: ('EORA',  eora),          0x98: ('EORAz', eoraz),
    0x89: ('ADCA',  adca),          0x99: ('ADCAz', adcaz),
    0x8A: ('ORAA',  oraa),          0x9A: ('ORAAz', oraaz),
    0x8B: ('ADDA',  adda),          0x9B: ('ADDAz', addaz),
    0x8C: ('CPX',   cpx),           0x9C: ('CPXz',  cpxz),
    0x8D: ('BSR',   bsr),           0x9D: (None,    invalid),
    0x8E: ('LDS',   lds),           0x9E: ('LDSz',  ldsz),
    0x8F: (None,    invalid),       0x9F: ('STSz',  stsz),

    0xA0: ('SUBAx', subax),         0xB0: ('SUBAm', subam),
    0xA1: ('CMPAx', cmpax),         0xB1: ('CMPAm', cmpam),
    0xA2: ('SBCAx', sbcax),         0xB2: ('SBCAm', sbcam),
    0xA3: (None,    invalid),       0xB3: (None,    invalid),
    0xA4: ('ANDAx', andax),         0xB4: ('ANDAm', andam),
    0xA5: ('BITAx', bitax),         0xB5: ('BITAm', bitam),
    0xA6: ('LDAAx', ldaax),         0xB6: ('LDAAm', ldaam),
    0xA7: ('STAAx', staax),         0xB7: ('STAAm', staam),
    0xA8: ('EORAx', eorax),         0xB8: ('EORAm', eoram),
    0xA9: ('ADCAx', adcax),         0xB9: ('ADCAm', adcam),
    0xAA: ('ORAAx', oraax),         0xBA: ('ORAAm', oraam),
    0xAB: ('ADDAx', addax),         0xBB: ('ADDAm', addam),
    0xAC: ('CPXx',  cpxx),          0xBC: ('CPXm',  cpxm),
    0xAD: ('JSRx',  jsrx),          0xBD: ('JSR',   jsr),
    0xAE: ('LDSx',  ldsx),          0xBE: ('LDSm',  ldsm),
    0xAF: ('STSx',  stsx),          0xBF: ('STSm',  stsm),

    0xC0: ('SUBB',  subb),          0xD0: ('SUBBz', subbz),
    0xC1: ('CMPB',  cmpb),          0xD1: ('CMPBz', cmpbz),
    0xC2: ('SBCB',  sbcb),          0xD2: ('SBCBz', sbcbz),
    0xC3: (None,    invalid),       0xD3: (None,    invalid),
    0xC4: ('ANDB',  andb),          0xD4: ('ANDBz', andbz),
    0xC5: ('BITB',  bitb),          0xD5: ('BITBz', bitbz),
    0xC6: ('LDAB',  ldab),          0xD6: ('LDABz', ldabz),
    0xC7: (None,    invalid),       0xD7: ('STABz', stabz),
    0xC8: ('EORB',  eorb),          0xD8: ('EORBz', eorbz),
    0xC9: ('ADCB',  adcb),          0xD9: ('ADCBz', adcbz),
    0xCA: ('ORAB',  orab),          0xDA: ('ORABz', orabz),
    0xCB: ('ADDB',  addb),          0xDB: ('ADDBz', addbz),
    0xCC: (None,    invalid),       0xDC: (None,    invalid),
    0xCD: (None,    invalid),       0xDD: (None,    invalid),
    0xCE: ('LDX',   ldx),           0xDE: ('LDXz',  ldxz),
    0xCF: (None,    invalid),       0xDF: ('STXz',  stxz),

    0xE0: ('SUBBx', subbx),         0xF0: ('SUBBm', subbm),
    0xE1: ('CMPBx', cmpbx),         0xF1: ('CMPBm', cmpbm),
    0xE2: ('SBCBx', sbcbx),         0xF2: ('SBCBm', sbcbm),
    0xE3: (None,    invalid),       0xF3: (None,    invalid),
    0xE4: ('ANDBx', andbx),         0xF4: ('ANDBm', andbm),
    0xE5: ('BITBx', bitbx),         0xF5: ('BITBm', bitbm),
    0xE6: ('LDABx', ldabx),         0xF6: ('LDABm', ldabm),
    0xE7: ('STABx', stabx),         0xF7: ('STABm', stabm),
    0xE8: ('EORBx', eorbx),         0xF8: ('EORBm', eorbm),
    0xE9: ('ADCBx', adcbx),         0xF9: ('ADCBm', adcbm),
    0xEA: ('ORABx', orabx),         0xFA: ('ORABm', orabm),
    0xEB: ('ADDBx', addbx),         0xFB: ('ADDBm', addbm),
    0xEC: (None,    invalid),       0xFC: (None,    invalid),
    0xED: (None,    invalid),       0xFD: (None,    invalid),
    0xEE: ('LDXx',  ldxx),          0xFE: ('LDXm',  ldxm),
    0xEF: ('STXx',  stxx),          0xFF: ('STXm',  stxm),

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

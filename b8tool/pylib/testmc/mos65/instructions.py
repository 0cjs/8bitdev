class Instructions():
    ''' Opcode constants for the 6502, named after the assembly
        instructions.

        There are often multiple opcodes per instruction, one for each
        of the different addressing modes. We distinguish these with a
        lower-case suffix:

                             implied
                  #nn        immediate
            z     nn         zero page
            zx    nn,X       zero indexed by X
            zy    nn,Y       zero indexed by Y
            a     addr       absolute (extended)
            ax    addr,X     absolute,X
            ay    addr,Y     absolute,Y
            i     [addr]     indirect
            ix    [addr,X]   indexed indirect
            iy    [addr],Y   indirect indexed


        One day we might find it worthwhile to have an Assembler class
        that can itself determine correct addressing modes and whatnot
        when assembling instructions, but there doesn't seem to be any
        gain from that at the moment.
    '''

    JSR = 0x20; RTS = 0x60; JMP = 0x4C; JMPi= 0x6C; RTI = 0x40;
    BRK = 0x00; NOP = 0xEA;

    BEQ = 0xF0; BNE = 0xD0; BMI = 0x30; BPL = 0x10
    BCS = 0xB0; BCC = 0x90; BVS = 0x70; BVC = 0x50

    CLC = 0x18; CLV = 0xB8; CLI = 0x58; CLD = 0xD8
    SEC = 0x38;             SEI = 0x78; SED = 0xF8

    TAX = 0xAA; TAY = 0xA8; TSX = 0xBA; PHA = 0x48; PHP = 0x08
    TXA = 0x8A; TYA = 0x98; TXS = 0x9A; PLA = 0x68; PLP = 0x28

    INX = 0xE8; INY = 0xC8
    DEX = 0xCA; DEY = 0x88

    EOR     = 0x49
    ADC     = 0x69
    STYa    = 0x8C
    STAzy   = 0x91
    STAay   = 0x99
    STAax   = 0x9d
    LDXz    = 0xA6
    LDA     = 0xA9
    LDYa    = 0xAC
    LDAax   = 0xBD
    CMP     = 0xC9
    SBC     = 0xE9

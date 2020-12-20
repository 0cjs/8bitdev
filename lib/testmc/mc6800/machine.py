from    itertools  import chain
from    testmc.generic  import *
from    testmc.mc6800.opcodes  import OPCODES, Instructions
from    testmc.mc6800.opimpl  import (
            InvalidOpcode, incword, readbyte, signedbyteat,
            )

class Machine(GenericMachine):

    def __init__(self, *, memsize=65536):
        ''' Initialize the machine.

            To make life easier for unit test clients, we initialize the
            stack pointer to $BFFF. (This assumes that the usual
            configuration may involve using any of the lower 32K as RAM and
            upper 16K as ROM and I/O.)

            All other registers, and all of memory, are initialized to
            zero. On a real machine certainly the memory, and probaby the
            registers and flags as well would all be left in a random state
            on power-up, but that doesn't seem worth emulating here.
        '''
        super().__init__()
        self.mem = IOMem(memsize)
        self.mem.copyapi(self)

        self.pc = self.a = self.b = self.x = 0
        self.sp = 0xBFFF
        self.H = self.I = self.N = self.Z = self.V = self.C = False

    is_little_endian = False
    def get_memory_seq(self):
        return self.mem

    class Registers(GenericRegisters):
        machname  = '6800'
        registers = (
            Reg('pc', 16), Reg('a'), Reg('b'), Reg('x', 16), Reg('sp', 16) )
        srbits    = ( Bit(1), Bit(1),
            Flag('H'), Flag('I'), Flag('N'), Flag('Z'), Flag('V'), Flag('C') )
        srname    = 'cc'    # Condition Codes Register

    ####################################################################
    #   Instruction Execution

    _RTS_opcodes    = set([Instructions.RTS])
    _ABORT_opcodes  = set([0x00])   # not an opcode and test mem init'd to this

    def _getpc(self):   return self.pc
    def _getsp(self):   return self.sp

    InvalidOpcode = InvalidOpcode

    class NotImplementedError(Exception):
        ''' Get rid of this once we're more complete. ''' # XXX

    def _step(self):
        opcode = readbyte(self)
        _, f = OPCODES.get(opcode, (None, None))
        if not f:
            raise self.NotImplementedError(
                'opcode=${:02X} pc=${:04X}'
                .format(opcode, incword(self.pc, -1)))
        f(self)

    def pushretaddr(self, word):
        self.sp -= 2
        self.depword(self.sp+1, word)

    def getretaddr(self):
        return self.word(self.sp+1)

    ####################################################################
    #   Tracing and similar information

    def disasm(self):
        ''' Disassemble a 6800 opcode and its operands at the PC.

            This has not been fully tested and may still get a few
            instructions or addressing modes wrong.

            TODO: Make this check `self.symtab` for addresses and,
            if present there, print them as symbols.
        '''
        pc = self.regs.pc
        op = self.byte(pc)
        mnemonic, _ = OPCODES[op]
        if mnemonic is None:
            return 'FCB ${:02X}'.format(op)
        else:
            #   To be most general we should add an addressing mode field
            #   to each tuple of opcode data and then just decode based on
            #   that. But due to our method of encoding the addressing mode
            #   in many mnemonics (described in the InstructionsClass
            #   docstring) this information is already explicit for many
            #   instructions, so for the moment we just re-use that until
            #   we see how many exceptions actually arise.
            mode = mnemonic[-1]
            if mode == 'm':
                return '{} ${:04X}'.format(mnemonic[0:-1], self.operand16())
            if mode == 'z':
                return '{} ${:02X}'.format(mnemonic[0:-1], self.operand8())
            if mode == 'x':
                return '{} ${:02X},X'.format(mnemonic[0:-1], self.operand8())
            if mnemonic[0] == 'B':
                #   Only relative branch instructions start with 'B'.
                offset = signedbyteat(self, incword(self.regs.pc, 1))
                return '{} ${:04X}'.format(mnemonic,
                    incword(self.regs.pc, offset + 2))
            if mnemonic in ['JMP', 'JSR']:
                #   All remaining (i.e., not postfixed with 'm')
                #   instructions with two-byte operands.
                return '{} ${:04X}'.format(mnemonic, self.operand16())
            if op in self.NO_OPERAND:
                return mnemonic

            #   Immediate operands
            return '{} #${:02X}'.format(mnemonic, self.operand8())

    #   Opcodes that take no operand
    NO_OPERAND = frozenset(chain(
        range(0x00, 0x10),  # NOP, TAP, INX, CLV, etc.
        range(0x30, 0x40),  # TSX, PULA, RTS, RTI, WAI, SWI, etc.
        ))

    def operand8(self):
        ' Return the first byte after the PC, handling wraparound. '
        return self.mem[incword(self.regs.pc, 1)]

    def operand16(self):
        ' Return the first word after the PC, handling wraparound. '
        pc1 = incword(self.regs.pc, 1)
        pc2 = incword(self.regs.pc, 2)
        return self.mem[pc1] * 0x100 + self.mem[pc2]

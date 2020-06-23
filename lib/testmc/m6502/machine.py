''' The test "machine" itself.
    Wraps py65 in an API suitable for use in unit tests.
'''

from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    sys import stderr

from    testmc.generic  import *
from    testmc.m6502.instructions  import Instructions as I

from    testmc import symtab
from    testmc.tool import asl, asxxxx

class Machine(GenericMachine):

    is_little_endian = True
    def get_memory_seq(self):
        return self.mpu.memory

    class Registers(GenericRegisters):
        machname = '6502'
        registers = (Reg('pc', 16), Reg('a'), Reg('x'), Reg('y'), Reg('sp'))
        #   No "B flag" here; it's not actually a flag in the PSR, it's
        #   merely set in the value pushed on to the stack on IRQ or `BRK`.
        srbits = (  Flag('N'), Flag('V'),   Bit(1),     Bit(1),
                    Flag('D'), Flag('I'), Flag('Z'), Flag('C'), )
        srname = 'p'

    ####################################################################

    class Abort(RuntimeError):
        ' The emulator encoutered an instruction on which to abort.'
        pass

    def __init__(self):
        self.mpu = MPU()
        self.regsobj = self.mpu
        self.symtab = symtab.SymTab([])     # symtab initially empty

    def _stackaddr(self, depth, size):
        addr = 0x100 + self.mpu.sp + 1 + depth
        if addr >= 0x201 - size:
            raise IndexError("stack underflow: addr={:04X} size={}" \
                .format(addr, size))
        return addr

    def spbyte(self, depth=0):
        return self.byte(self._stackaddr(depth, 1))

    def spword(self, depth=0):
        return self.word(self._stackaddr(depth, 2))

    def _getpc(self):
        return self.mpu.pc

    def _step(self):
            self.mpu.step()

    #   Opcodes that execute an unconditional call. This must be a `set()`
    #   or other object that supports the `|` operator for set union.
    #
    _JSR_opcodes = set([I.JSR])

    #   Opcodes that execute an unconditional return from a called
    #   subroutine. This must be a `set()` or other object that supports
    #   the `|` operator for set union.
    #
    _RTS_opcodes = set([I.RTS])

    #   The default set of opcodes that should abort the execution of
    #   `call()`. This must be a `set()` or other object that supports the
    #   `|` operator for set union.
    #
    #   Which opcode(s) you choose for this set will depend on both the CPU
    #   and the conventions of programming on that CPU. For example `BRK`
    #   is a reasonable abort default on 6502 because it's not often used
    #   as a call mechanism in 6502 programs, but that is not true for the
    #   very similar 6800 `SWI` instruction.
    #
    _ABORT_opcodes = set([I.BRK])

    #   Default maximum number of opcodes to execute when using stepto(),
    #   call() and related functions. Even on a relatively slow modern
    #   machine, 100,000 opcodes should terminate within a few seconds.
    MAXSTEPS = 100000

    def call(self, addr, regs=None, *,
            maxsteps=MAXSTEPS, aborts=_ABORT_opcodes, trace=False):
        ''' Simulate a JSR to `addr`, after setting any `registers`
            specified, returning when its corresponding RTS is reached.

            A `Timeout` will be raised if `maxsteps` opcodes are executed.
            An `Abort` will be raised if any opcodes in the `aborts`
            collection are about to be executed. (By default this list
            contains all instructions in `_ABORT_opcodes`.) `step()`
            tracing will be enabled if `trace` is `True`.

            The PC will be left at the final (unexecuted) RTS opcode. Thus,
            unlike `step()`, this may execute no opcodes if the PC is
            initially pointing to an RTS.

            JSR and RTS opcodes will be tracked to allow the routine to
            call subroutines, but tricks with the stack (such as pushing an
            address and executing RTS, with no corresponding JSR) will
            confuse this routine and may cause it to terminate early or not
            at all.
        '''
        if regs is None:
            regs = self.Registers()
        self.setregs(regs)

        if addr is not None:
            self.setregs(self.Registers(pc=addr))   # Overrides regs

        stopat = self._JSR_opcodes | self._RTS_opcodes | set(aborts)
        depth = 0
        while True:
            opcode = self.byte(self.mpu.pc)
            if opcode in self._RTS_opcodes:
                if depth > 0:
                    depth -=1
                else:
                    #   We don't execute the RTS because no JSR was called
                    #   to come in, so we may have nothing on the stack.
                    return
            elif opcode in self._JSR_opcodes:
                #   Enter the new level with the next execution
                depth += 1
            elif opcode in stopat:   # Abort
                raise self.Abort('Abort on opcode={}: {}' \
                    .format(self.byte(self.regs.pc), self.regs))
            self.stepto(stopat, maxsteps=maxsteps, trace=trace)

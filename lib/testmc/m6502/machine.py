''' The test "machine" itself.
    Wraps py65 in an API suitable for use in unit tests.
'''

from    collections.abc   import Container, Sequence
from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    sys import stderr

from    testmc.generic  import *
from    testmc.m6502.instructions  import Instructions

from    testmc import symtab
from    testmc.tool import asl, asxxxx

class Machine(GenericMachine):

    def is_little_endian(self):
        return True

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

    class Timeout(RuntimeError):
        ' The emulator ran longer than requested. '
        pass

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

    def _step(self):
            self.mpu.step()

    #   Default maximum number of opcodes to execute when using stepto(),
    #   call() and related functions. Even on a relatively slow modern
    #   machine, 100,000 opcodes should terminate within a few seconds.
    MAXSTEPS = 100000

    def stepto(self, stopat, *, maxsteps=MAXSTEPS, trace=False):
        ''' Step an opcode and then, as long as the next opcode
            is not `stopat` (if a single value) or in `stopat` (if a
            container), continue stepping.

            If a `stopat` opcode hasn't been reached after `maxsteps`
            opcodes have been executed, raise a `Timeout` exception.
        '''
        if not isinstance(stopat, Container):
            stopat = (stopat,)
        self.step(trace=trace)
        count = maxsteps - 1
        while self.byte(self.mpu.pc) not in stopat:
            self.step(trace=trace)
            count -= 1
            if count <= 0:
                raise self.Timeout(
                    'Timeout after {} opcodes: {} opcode={}' \
                    .format(maxsteps, self.regs, self.byte(self.regs.pc)))

    def call(self, addr, regs=None, *,
            maxsteps=MAXSTEPS, aborts=(0x00,), trace=False):
        ''' Simulate a JSR to `addr`, after setting any `registers`
            specified, returning when its corresponding RTS is reached.

            A `Timeout` will be raised if `maxsteps` opcodes are executed.
            An `Abort` will be raised if any opcodes in the `aborts`
            collection are about to be executed. (By default this list
            contains ``BRK``.) `step()` tracing will be enabled if `trace`
            is `True`.

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

        I = Instructions
        stopat = (I.JSR, I.RTS) + tuple(aborts)
        depth = 0
        while True:
            opcode = self.byte(self.mpu.pc)
            if opcode == I.RTS:
                if depth > 0:
                    depth -=1
                else:
                    #   We don't execute the RTS because no JSR was called
                    #   to come in, so we may have nothing on the stack.
                    return
            elif opcode == I.JSR:
                #   Enter the new level with the next execution
                depth += 1
            elif opcode in stopat:   # Abort
                raise self.Abort('Abort on opcode={}: {}' \
                    .format(self.byte(self.regs.pc), self.regs))
            self.stepto(stopat, maxsteps=maxsteps, trace=trace)

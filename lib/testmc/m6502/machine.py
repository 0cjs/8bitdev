''' The test "machine" itself.
    Wraps py65 in an API suitable for use in unit tests.
'''

from    collections.abc   import Container, Sequence
from    itertools  import repeat
from    numbers  import Integral
from    py65.devices.mpu6502  import MPU
from    sys import stderr

from    testmc.memory  import MemoryAccess
from    testmc.m6502.instructions  import Instructions
from    testmc.m6502.registers  import Registers

from    testmc import symtab
from    testmc import asl, asxxxx

class Machine(MemoryAccess):

    class Timeout(RuntimeError):
        ' The emulator ran longer than requested. '
        pass

    def is_little_endian(self):
        return True

    def get_memory_seq(self):
        return self.mpu.memory

    class Abort(RuntimeError):
        ' The emulator encoutered an instruction on which to abort.'
        pass

    def __init__(self):
        self.mpu = MPU()
        self.symtab = symtab.SymTab([])     # symtab initially empty

    @property
    def regs(self):
        m = self.mpu
        return Registers(m.pc, m.a, m.x, m.y, m.sp, psr=m.p)

    def setregs(self, r):
        m = self.mpu
        if r.pc is not None:  m.pc = r.pc
        if r.a  is not None:  m.a  = r.a
        if r.x  is not None:  m.x  = r.x
        if r.y  is not None:  m.y  = r.y
        if r.sp is not None:  m.sp = r.sp

        flags_masks = (
            ('N', 0b10000000),
            ('V', 0b01000000),
            ('D', 0b00001000),
            ('I', 0b00000100),
            ('Z', 0b00000010),
            ('C', 0b00000001),
            )
        for (flagname, mask) in flags_masks:
            flag = getattr(r, flagname)
            if flag is None:
                continue
            elif flag == 0:
                m.p &= ~mask
            elif flag == 1:
                m.p |= mask
            else:
                raise ValueError('Bad {} flag value: {}'.format(flagname, flag))

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

    def load(self, path):
        ''' Load the given ``.bin`` file and, if available, the
            symbols from a ``.rst`` (ASxxxx linker listing file)
            in the same directory.
        '''
        if path.lower().endswith('.p'):
            #   Assume it's Macro Assembler AS output.
            self.load_memimage(asl.parse_obj_fromfile(path))
            mapfile_path = path[0:-2] + '.map'
            try:
                self.symtab = asl.parse_symtab_fromfile(mapfile_path)
            except FileNotFoundError as err:
                print('WARNING: could not read symbol table file from path ' \
                    + mapfile_path, file=stderr)
                print('FileNotFoundError: ' + str(err), file=stderr)
        else:
            #   Assume it's the basename of ASxxxx toolchain output.
            #   (This should probably be changed to require something
            #   indicating this explicitly.)
            self.load_memimage(asxxxx.parse_cocobin_fromfile(path + '.bin'))
            try:
                self.symtab = asxxxx.AxSymTab.readsymtabpath(path)
            except FileNotFoundError as err:
                print('WARNING: could not read symbol table file from path ' \
                    + path, file=stderr)
                print('FileNotFoundError: ' + str(err), file=stderr)

    def load_memimage(self, memimage):
        for addr, data in memimage:
            self.deposit(addr, data)
        self.mpu.pc = memimage.entrypoint

    def step(self, count=1, *, trace=False):
        ''' Execute `count` instructions (default 1).

            If `trace` is `True`, the current machine state and
            instruction about to be executed will be printed
            before executing the step.

            XXX This should check for stack under/overflow.
        '''
        for _ in repeat(None, count):
            if trace:
                print('{} opcode={:02X}' \
                    .format(self.regs, self.byte(self.regs.pc)))
            self.mpu.step()

    #   Default maximum number of instructions to execute when using
    #   stepto(), call() and related functions. Even on a relatively
    #   slow modern machine, 100,000 instructions should terminate
    #   within a few seconds.
    MAXOPS = 100000

    def stepto(self, instrs, *, maxops=MAXOPS, trace=False):
        ''' Step an instruction and then continue stepping until an
            instruction in `instrs` is reached. Raise a `Timeout`
            after `maxops`.
        '''
        if not isinstance(instrs, Container):
            instrs = (instrs,)
        self.step(trace=trace)
        count = maxops - 1
        while self.byte(self.mpu.pc) not in instrs:
            self.step(trace=trace)
            count -= 1
            if count <= 0:
                raise self.Timeout(
                    'Timeout after {} instructions: {} opcode={}' \
                    .format(maxops, self.regs, self.byte(self.regs.pc)))

    def call(self, addr, regs=Registers(), *,
            maxops=MAXOPS, aborts=(0x00,), trace=False):
        ''' Simulate a JSR to `addr`, after setting any `registers`
            specified, returning when its corresponding RTS is
            reached.

            A `Timeout` will be raised if `maxops` instructions are
            executed. An `Abort` will be raised if any instructions in
            the `aborts` collection are about to be executed. (By
            default this list contains ``BRK``.) `step()` tracing will
            be enabled if `trace` is `True`.

            The PC will be left at the final (unexecuted) RTS
            instruction. Thus, unlike `step()`, this may execute no
            instructions if the PC is initially pointing to an RTS.

            JSR and RTS instructions will be tracked to allow the
            routine to call subroutines, but tricks with the stack
            (such as pushing an address and executing RTS, with no
            corresponding JSR) will confuse this routine and may
            cause it to terminate early or not at all.
        '''
        self.setregs(regs)
        if addr is not None:
            self.setregs(Registers(pc=addr))    # Overrides regs
        I = Instructions
        stopon = (I.JSR, I.RTS) + tuple(aborts)
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
            elif opcode in stopon:   # Abort
                raise self.Abort('Abort on opcode={}: {}' \
                    .format(self.byte(self.regs.pc), self.regs))
            self.stepto(stopon, maxops=maxops, trace=trace)

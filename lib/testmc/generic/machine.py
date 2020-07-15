from    abc  import abstractmethod, abstractproperty
from    collections.abc   import Container
from    itertools  import repeat
from    testmc.generic.memory  import MemoryAccess
from    testmc.tool  import asl, asxxxx

class GenericMachine(MemoryAccess): # MemoryAccess is already an ABC
    ''' Superclass for "Machines" that simulate a microprocessor system
        with memory and registers.

        The interface offers the following properties and methods. The ones
        marked with ◑ must be implemented by the subclass; see the
        attribute/method docstring for details.

        - ◑`MemoryAccess` routines: `byte()`, `word()`, `deposit()`, etc.
          (See that class for subclassing information.)
        - ◑`Registers`: The subclass of `GenericRegisters` that defines
          the registers and flags of the machine.
        - `regs`: The current machine registers and flags.
        - `setregs()`: Set some or all machine registers and flags.
    '''

    @abstractproperty
    def Registers(self):
        ''' The class defining the registers of the machine.

            This is typically a subclass of `GenericRegisters`, and the
            attribute can be defined most easily with a nested class
            declaration in the subclass:

                class Registers(GenericRegisters):
                    registers = (...)
                    srbits = (...)
                    srname = '...'
        '''

    def _regsobj(self):
        return getattr(self, 'regsobj', self)

    @property
    def regs(self):
        ''' A `Registers` instance containing the current values of the
            machine registers and flags.

            If the `regsobj` attribute has a value, the register values
            will be read from attributes on that object, otherwise they
            will be read from attributes on `self`.
        '''
        R = self.Registers
        srname = R()._srname()
        regsobj = self._regsobj()
        vals = {}
        for reg in R.registers:
            vals[reg.name] = getattr(regsobj, reg.name)
        if srname:
            vals[srname] = getattr(regsobj, srname)
        else:
            for flag in R.srbits:
                if flag.name:
                    vals[flag.name] = getattr(regsobj, flag.name)
        return R(**vals)

    def setregs(self, r):
        ''' Given a `Registers` object, set the machine's registers and
            flags to the value of any non-`None` values in the `Registers`.
        '''
        r.set_attrs_on(self._regsobj(), setsr=bool(r._srname()))

    ####################################################################
    #   Object code loading

    def load_memimage(self, memimage):
        for addr, data in memimage:
            self.deposit(addr, data)
        self.setregs(self.Registers(pc=memimage.entrypoint))

    def load(self, path):
        ''' Load the given ``.bin`` file and, if available, the
            symbols from a ``.rst`` (ASxxxx linker listing file)
            in the same directory. The Machine's ``pc`` register
            will be set to the entry point of the loaded binary.
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

    ####################################################################
    #   Execution - abstract methods

    @abstractproperty
    def _JSR_opcodes(self):
        ''' Opcodes that execute an unconditional call. This must be a `set()`
            or other object that supports the `|` operator for set union.
        '''
    @abstractproperty
    def _RTS_opcodes(self):
        ''' Opcodes that execute an unconditional return from a called
            subroutine. This must be a `set()` or other object that
            supports the `|` operator for set union.
        '''

    @abstractproperty
    def _ABORT_opcodes(self):
        ''' The default set of opcodes that should abort the execution of
            `call()`. This must be a `set()` or other object that supports
            the `|` operator for set union.

            Which opcode(s) you choose for this set will depend on both the
            CPU and the conventions of programming on that CPU. For example
            `BRK` is a reasonable abort default on 6502 because it's not
            often used as a call mechanism in 6502 programs, but that is
            not true for the very similar 6800 `SWI` instruction.
        '''

    @abstractmethod
    def _getpc(self):
        ''' Efficiently return the current program counter value.

            The PC is checked very frequently by `stepto()`, `call()`, etc.
            and checking it via `regs` (which generates a new a Registers
            object each time it's called) slows down stepping by an order
            of magnitude compared to returning the PC value as directly
            as possible from the underlying simulator.
        '''

    @abstractmethod
    def _step(self):
        ' Execute current opcode (and its arguments), updating machine state. '

    ####################################################################
    #   Execution - implementation

    def step(self, count=1, *, trace=False):
        ''' Execute `count` instructions (default 1).

            If `trace` is `True`, the current machine state and instruction
            about to be executed will be printed before executing the step.

            XXX This should check for stack under/overflow.
        '''
        for _ in repeat(None, count):
            if trace:
                print('{} opcode={:02X}' \
                    .format(self.regs, self.byte(self.regs.pc)))
            self._step()

    class Timeout(RuntimeError):
        ' The emulator ran longer than requested. '

    class Abort(RuntimeError):
        ' The emulator encoutered an instruction on which to abort.'

    #   Default maximum number of opcodes to execute when using stepto(),
    #   call() and related functions. Even on a relatively slow modern
    #   machine, 100,000 opcodes should terminate within a few seconds.
    MAXSTEPS = 100000

    def stepto(self, *, stopat=set(), stopon=set(), maxsteps=MAXSTEPS,
        trace=False):
        ''' Step an opcode and then continue until an address in `stopat`
            or an opcode in `stopon` is reached, or until we have done
            `maxsteps`. (At least one opcode is always executed.)

            An attempt to exceed `maxsteps` will raise a `Timeout`
            exception; if you want to run just a specific number of steps
            use `step()` instead. Any other stop condition simply returns.

            `stopat` and `stopon` are checked to ensure that they are
            `collections.abc.Container` instances.
        '''
        assert isinstance(stopat, Container), \
            "'stopat' must be a collections.abc.Container"
        assert isinstance(stopon, Container), \
            "'stopon' must be a collections.abc.Container"

        remaining = maxsteps - 1
        while True:
            self.step(trace=trace)
            pc = self._getpc()
            if pc in stopat or self.byte(pc) in stopon:
                break
            if remaining <= 0:
                raise self.Timeout(
                    'Timeout after {} opcodes: {} opcode={}' \
                    .format(maxsteps, self.regs, self.byte(self.regs.pc)))
            remaining -= 1

    def call(self, addr, regs=None, *,
            maxsteps=MAXSTEPS, aborts=None, trace=False):
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
        if regs is None: regs = self.Registers()
        self.setregs(regs)

        if aborts is None:
            aborts = self._ABORT_opcodes
        if not isinstance(aborts, Container):
            aborts = (aborts,)

        if addr is not None:
            self.setregs(self.Registers(pc=addr))   # Overrides regs

        stopon = self._JSR_opcodes | self._RTS_opcodes | set(aborts)
        depth = 0
        while True:
            opcode = self.byte(self._getpc())
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
            elif opcode in stopon:   # Abort
                raise self.Abort('Abort on opcode=${:02X}: {}' \
                    .format(self.byte(self.regs.pc), self.regs))
            self.stepto(stopon=stopon, maxsteps=maxsteps, trace=trace)

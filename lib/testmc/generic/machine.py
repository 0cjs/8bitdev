from    abc  import abstractmethod, abstractproperty
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

        XXX Eventually this should also include `step()`, `call()`, etc.
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

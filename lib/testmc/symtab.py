''' The symbol table from toolchain output, mapping symbol names to
    values.

    This is the generic part of the symbol table produced by a
    toolchain; both the `SymTab` itself and the `Symbol` objects it
    holds may be subclassed for a particular toolchain.

    Each `Symbol` in a `SymTab` has a name and a value and also
    belongs to a *section* which may determine output addresses and/or
    banks, addressing modes, and the like, or may just be an
    assembly-time distinction (such as non-contiguous addresses in
    source code). Names are unique across all sections; sec section
    names (or numbers) are toolchain-dependent.

    Sections are often called "segments" and sometimes "areas" in
    particular toolchains; we use "section" to avoid confusion with
    the "segments" used in memory addressing in some processors. This
    is the same terminology as ELF, where "sections" refer to
    link-time distinctions (such as symbols) and "segments" refer to
    run-time image setup.
'''

from    collections   import namedtuple as ntup

class SymTab():
    ''' The symbol table of an assembled module, mapping symbol names
        to values. The entries are stored as `Symbol` objects that may
        be subclassed, allowing extra toolchain-specific attributes to
        be added to symbols.

        You may look up the value of a symbol directly with ``stab.name``
        or ``stab['name']`` or get the `Symbol` object by name with
        ``stab.sym('name')``.
    '''

    class Symbol(ntup('Symbol', 'name, value, section')):
        ''' A Symbol has a name, value, section and possibly other
            toolchain-specific information. The section is a
            toolchain-specific value and may be `None` if the
            toolchain does not support sections or an equivalent
            concept.
        '''
        pass

    def __init__(self, symbols):
        self.symbols = { s.name: s for s in symbols }

    def sym(self, name):
        ' Given a symbol name, return its Symbol object. '
        return self.symbols[name]

    def __len__(self):
        return len(self.symbols)

    def __getitem__(self, key):
        ' Given a symbol name, return its value. '
        return self.sym(key).value

    def __getattr__(self, name):
        ''' Allow reading of symbol values as attributes, so long as
            they do not collide with existing attributes.
        '''
        if name in self.symbols:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)


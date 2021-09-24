''' The symbol table from toolchain output, mapping symbol names to
    values.

    This is the generic part of the symbol table produced by a
    toolchain; both the `SymTab` itself and the `Symbol` objects it
    holds may be subclassed for a particular toolchain.

    Each `Symbol` in a `SymTab` maps a unqiue name to a value and optional
    *section*. Sections may have run-time distinctions (e.g., indicating
    the address is in a different bank of memory) or may indicate only
    assembly-time characteristics (e.g., for non-contiguous address areas
    in source code). Section naming/numbering is toolchain-dependent;
    toolchains without section support should use `None` as the section..

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
        ``stab.sym('name')``. Iterating over the `SymTab` will produce a
        stream of ``(name, value)`` tuples for those attributes of each
        `Symbol`.
    '''

    class Symbol(ntup('Symbol', 'name, value, section')):
        ''' A Symbol has a name, value, section and possibly other
            toolchain-specific information. The section is a
            toolchain-specific value and may be `None` if the
            toolchain does not support sections or an equivalent
            concept.
        '''
        pass

    @staticmethod
    def fromargs(**kwargs):
        ''' Create a `SymTab` from the arguments list of symbol names
            bound to values. This can also be used to create a `SymTab`
            from a `dict` or other collection of mappings with an `items()`
            method.
        '''
        symlist = []
        for k, v in kwargs.items():
            symlist.append(SymTab.Symbol(k, v, None))
        return SymTab(symlist)

    def __init__(self, symbols=None):
        if symbols is None:
            symbols = ()
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

    def __iter__(self):
        ''' Iteration iterates over just the ``(name,value)`` of all symbols.

            This avoids having to deconstruct returned Symbol objects.
            We anticipate that most users of this iteration will be
            generic, so not returning the additional information is ok.
        '''
        return ((s.name, s.value) for _, s in self.symbols.items())

    def valued(self, value):
        ' Given a value, return a `set` of Symbol objects having that value. '
        return set(( s for s in self.symbols.values() if s.value == value ))

    def merge(self, symtab, style='conflict'):
        ''' Merge the symbols from `symtab` into this symbol table. `style`
            determines how the merge is done, and must be one of the
            following values:
            - ``ignorenew``: Ignore all symbols in `symtab` (no-op).
            - ``prefcur``: If a new symbol has the same name as an existing
              symbol, keep the existing one and drop the new one.
            - ``prefnew``: If a new symbol has the same name as an existing
              symbol, drop the existing one and replace it with the new one.
            - ``conflict``: If a new symbol has the same name as an existing
              symbol, raise a `ValueError`.

            This returns `symtab`.

            XXX ``style='conflict'`` merges should not raise a conflict
            if a new `Symbol` with the same name as an existing `Symbol`
            also has the same value and other fields.
        '''
        ss = self.symbols
        newvals = symtab.symbols.values()
        if style == 'conflict':
            for sym in newvals:
                if sym.name in ss:
                    raise ValueError('duplicate symbol: ' + repr(sym))
                else:
                    ss[sym.name] = sym
        elif style == 'ignorenew':
            pass
        elif style == 'prefcur':
            for sym in newvals:
                if sym.name not in ss: ss[sym.name] = sym
        elif style == 'prefnew':
            for sym in newvals: ss[sym.name] = sym
        else:
            raise ValueError('Bad `style` parameter: ' + style)
        return symtab

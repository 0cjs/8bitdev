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

    class Symbol(ntup('Symbol', 'name, value')):
        ''' A Symbol has a name, value and possibly other
            toolchain-specific information.
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


from    testmc.symtab   import SymTab

def test_SymTab():
    sym1 = SymTab.Symbol('one', 1)
    sym2 = SymTab.Symbol('two', 'Two')
    s = SymTab([sym1, sym2])

    assert        2 == len(s)
    assert     sym1 == s.sym('one')
    assert     sym2 == s.sym('two')

    assert        1 == s['one']
    assert   'Two'  == s['two']
    assert        1 == s.one
    assert    'Two' == s.two


from    testmc.symtab   import SymTab

def test_SymTab():
    sym1 = SymTab.Symbol('one', 1, None)
    sym2 = SymTab.Symbol('two', 'Two', None)
    s = SymTab([sym1, sym2])

    #   .sym() interface
    assert     sym1 == s.sym('one')
    assert     sym2 == s.sym('two')

    #   Attribute interface
    assert        1 == s.one
    assert    'Two' == s.two

    #   Collection interface
    assert        1 == s['one']
    assert   'Two'  == s['two']
    assert        2 == len(s)
    for name, value in s:
        assert name in ('one', 'two')
        assert value in (1, 'Two')

from    testmc.m6502 import  Machine, Registers as R, Instructions as I
import  pytest

@pytest.fixture
def M():
    M = Machine()
    M.load('.build/obj/reloctest')
    return M

@pytest.mark.xfail(strict=True)
#   See test_ident for details.
def test_global(M):
    s = "@[reloctest]@"
    assert s == M.str(M.symtab.reloctest, len(s))

@pytest.mark.xfail(strict=True)
#   This fails because the symbol table in the linker listing still
#   says that the object is at 0000 even though it's been relocated
#   to 0400 (as shown in the listing itself). We need to fix our
#   symbol table loader to handle this before this will pass.
def test_ident(M):
    S = M.symtab
    ident_str = "reloctest.a65"
    assert ident_str == M.str(S.ident, len(ident_str))

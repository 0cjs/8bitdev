''' Implementation of opcodes.

    Each function here is passed a reference to an `MC6800` instance with
    the program counter pointing to its opcode. The function is responsible
    for updating all machine state before returning.

    See `testmc.mc6800.opcodes.Instructions` for details of the naming scheme.
'''

####################################################################
#   Tests of values for setting flags (HINZVC)

def isnegative(b):
    return 0 != b & 0b10000000

def iszero(b):
    return b == 0

####################################################################
#   Opcode implementations

def ldaa(m):
    m.a = m.byte(m.pc+1)
    m.N = isnegative(m.a)
    m.Z = iszero(m.a)
    m.V = False
    m.pc += 2

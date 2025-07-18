8-bit Assembler Code
====================

### Directory Structure

There are three basic types of directories: CPU directories containing
generic code for any platform using a particular CPU; platform directories
containing code for a particular microcomputer or other system, and
toolchain directories mainly used for testing features of various
assemblers.

    Misc        notes/      Programming notes and ideas for software
                skip.pt     ./Test src/skip.pt to skip all unit tests
                generic/    Cross-CPU test code
                generic/funtions.py  Generic test support functions

    CPU         mos65/      MOS 6502
                mc68/       Motorola MC6800
                i8080/      Intel 8080
                z80/        Zilog Z80

    Platform    a1/         Apple 1 (and clones/similar machines)
                a2/         Apple II, including later models
                cbm/        Commodore, all models
                fm7/        Fujitsu FM-7/FM77
                kc85/       Kyocera Kyotronic 85 and derivatives
                            (NEC PC-8201, TRS-80 Model 100, etc.)
                jr200/      National/Panasonic JR-200
                mb6885/     Hitachi Basic Master Jr.
                tk80/       NEC TK-80 and TK-85 trainer boards
                tmc68/      bin/tmc6800 (testmc.mc6800) simulator

    Toolchain   asl/        The Macroassembler AS
                asxxxx/     ASxxx assembler toolki

    Other       bios.md     Test system BIOS interface
                tmon/       Documentation for tmon/ portable monitor


Code Conventions
----------------

The header comments for a routine generally use the following conventions
to describe register and flag usage:

    Flags are assumed to be destroyed unless otherwise indicated.
    ♠ indicates registers and locations holding return values.
    ♡ indicates registers preserved
    ♣ indicates registers and locations destroyed.

Common symbol prefixes:
- `pr`: Print routines that send output to the console, potentially
  converting binary data into ASCII.
- `rd`: Read routines that read input from the console, generally doing
  little or no conversion.
- `q`: (Remember as "query.") Parsing routines that read data in memory and
  produce a result or error, often moving a parse position pointer.
  Sometimes designed used as parsing combinators.

Library Files
-------------

Some source files, such as `src/i8080/arith.i80` are noted in their headers
as being "library" files. These contain multiple routines and use a trick
with `ifnused` to avoid assembling into the including file any routines
that are not referenced.

This is not entirely reliable: you _must_ reference the routine _before_
you `include` the file for this to work. (If you are calling a routine only
after the library file is included, you can ensure it's referenced before
inclusion with a `set _,NAME`, where `_` can be any symbol that is not
otherwise used.)

If you fail to reference the symbol before inclusion, the routine will
not be assembled into your output and the address will be $FFFF, causing
a (usually mysterious) error when the code is run. Typically unit tests
will catch this.

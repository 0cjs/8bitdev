8-bit Assembler Code
====================

### Directory Structure

There are three basic types of directories: CPU directories containing
generic code for any platform using a particular CPU; platform directories
containing code for a particular microcomputer or other system, and
toolchain directories mainly used for testing features of various
assemblers.

    CPU         m65/        MOS 6502
                mc68/       Motorola MC6800

    Platform    a1/         Apple 1 (and clones/similar machines)
                a2/         Apple II, including later models
                jr200/      National/Panasonic JR-200
                tmc68/      bin/tmc6800 (testmc.mc6800) simulator

    Toolchain   asl/        The Macroassembler AS
                asxxxx/     ASxxx assembler toolki


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

8-bit Assembler Code
====================

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

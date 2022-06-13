8bitdev "BIOS" Interface
========================

This repo has a standard strategy for handling machine-specific ROM and OS
symbols, along with a set of common names for the usual I/O routines. Here
we refer to all the vendor-provided code as "ROM" even when it may be code
loaded into RAM as part of a standard OS. (E.g., `cpm/bios.aXX` and
`cpm/bdos.aXX` would cover the standard APIs for the CP/M BIOS and BDOS,
though these are usually loaded into RAM.)

The `src/<machine>/bios.aXX` files define the low-level system routines in
the part of the ROM typically called "BIOS," "monitor," "KERNAL," etc.
These contain definitions only (they can be used by programs that do not
want to bring in extra library code) and should work across all versions of
the ROM. (E.g., on both the Apple II using Integer BASIC ROM and the Apple
II+ using Applesoft ROM.)

Separate files are used for additional ROM that may be enabled or disabled
independently, such as the KERNAL and BASIC ROMs on CBM machines, the BIOS
and BASIC ROMs on the National/Panasonic JR-200, or the BIOS and BDOS on
CP/M.

All these definition files are normally included at the top of the assembly
file so you can see at a glance which ROMs a program uses.

### Symbol Naming

The machine-specific symbol names in the files above are the officially
documented symbol names where known, otherwise the names are usually taken
from the [retroabandon disassemblies][rd].

The files may also contain generic names for any routines that match the
"common" API described below. Any common routines that are not provided
directly by system ROM may have equivalent code provided in
`<machine>/common.aXX`; see below for more details.


Common BIOS Routines and the Unit Test BIOS
-------------------------------------------

There are a few routines that are commonly used and generally work in the
same way across all platforms. This repo has some standard names for these.
(We annotate return registers with `♠`, preserved registers with `♡` and
registers that may be destroyed with `♣`.)

    prchar      ; ♡all      print char in A
    rdchar      ; ♠A ♡all   blocking read of char from input
    prnl        ; ♣all      print platform-appropriate newline
                            (move to left-hand side of screen on next line)
    errbeep     ; ♣all      sound an error tone

These symbols may be provided by a `<machine>/bios.aXX` or similar
definition file if the ROM provides routines matching the API (including
preserved registers). If it doesn't, code for the routines may be provided
in a `<machine>/common.aXX` file that can be included at the desired
location of the code in your assembly file. (These cannot generally be
included at the top of the file because they generate code, but they don't
define an API so that's no problem.)

### Unit Test BIOS

As with real hardware, the simulated machines (e.g., `tmc6800`) used for
unit testing have a BIOS that supplies the common routines above (and
perhaps others). For convenience in debugging and experimentation the entry
points are at fixed locations and are defined in `<machine>/bios.aXX` as
usual.

The code implementing the BIOS is in `<machine>/bioscode.aXX` and is loaded
separately from the code under test or program to be run by the simulator;
this is done by the unit test framework (`testmc.conftest.loadbios()`) or
by the simulator command-line program (e.g. `b8tool/bin/tmc6800`). The unit
test framework sets up input for the test run and collects any output; the
command-line simulator takes input from stdin and sends output to stdout.



<!-------------------------------------------------------------------->
[rd]: https://gitlab.com/retroabandon

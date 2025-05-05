BIOS Defintion Files
====================

This directory contains BIOS definition files (none of which generate code)
for all the various platforms we use. Keeping them together in one
directory helps us more easily see the differences between what various
BIOSes provide and also to work out what we can rely on to be common
amongst most BIOSes.

This does not include the TMC (command-line CPU simulator) BIOS files;
those are provided by the t8dev `biosdef.*` resource files in the
`testmc.*.tmc` modules.

The `src/biosdef/<machine>.<cpu>` files contain definitions only (they do
not generate code, at least not by default) and should work across all
versions of the ROM. (E.g., on both the Apple II using Integer BASIC ROM
and the Apple II+ using Applesoft ROM.)

These definition files are normally included at the top of the assembly
file so you can see at a glance which ROMs a program uses.

### Symbol Naming

The machine-specific symbol names in the files above are the officially
documented symbol names where known, otherwise the names are usually taken
from the [retroabandon disassemblies][rd].

The files may also contain generic names for any routines that match the
"common" API described below. common routines that are not provided
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

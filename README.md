8bitdev
=======


This demonstrates unit testing of machine-language code using pytest.
The code is built and linked with [ASxxxx]. We then bring up an
instance of a [py65] CPU within our test framework, load the binary
file into its memory, run a bit of code, and then check that the
registers and memory are correct. (The APIs for doing this still need
a _lot_ of work.)

Run the top-level `./Test` script to see everything go.


py65
----

[py65][] ([source][py65src]) is a Python-based 6502 emulator.

### py65 Monitor

py65 includes a monitor, `py65mon`, that can be run from the command
line. With no options it drops directly into the monitor on a
simulated 6502 with 64K RAM.

Options:
- `-l FILE`: Load file at address `$0000`.
- `-r FILE`: Load ROM image at top of address space and reset into it.
- `-g ADDR`: Goto _ADDR_ after loading files.
- `-i ADDR`: Location of TTY input register `getc` (default `0xf004`)
- `-o ADDR`: Location of TTY ouput register `putc` (default `0xf001`)

Addresses given on the command line use C/Python base notation (`10`,
`0xa`, `012`) rather than the `+$` notation used with monitor
commands.

#### [Command][py65-cmds] summary (similar to [VICE monitor][vice-mon]):

General:
- Readline command line editing available.
- Prefix numbers w/`$+%` for hex/decimal/binary. `radix` shows/sets default.
- `help [CMD]` with for more details.
- `quit`
- `add_label ADDR NAME`, `show_labels`, `delete_label NAME`: _NAME_ can be
  used in place of _ADDR_ below, and arithmetic (`start+8`) may be used.

Display and input:
- `~ NUMBER`: Displays _NUMBER_ in all bases.
- `registers`: display `PC  AC XR YR SP NV-BDIZC`.
  Set regs with `NAME=VALUE`, comma-separated.
- `mem START:END`: Display memory. Show 16-byte lines with `width 70`.
- `fill ADDR[:END] BYTE ...`: Deposit byte(s) starting at _ADDR_.
   Repeats bytes to _END_ if given.
- `disassemble START:END`
- `assemble ADDR [STMT]`: Interactive if no stmt given. Labels may be used.
- `load "FNURL" ADDR`: Load file or URL (quotes optional) at given
  address (`top` for top of memory). (Warning: C64 files will have a
  two-byte load address at the start of the file that's treated as data.)
- `save FNAME START END`

Execution:
- `reset`: Reset CPU and clear memory.
- `goto ADDR`: Set PC and resume execution
- `return`: Execute, return to monitor just before next `RTS/RTI`.
- `step`: Executes instr, disassembles next instr.
- `add_breakpoint ADDR`, `show_breakpoints`, `delete_breakpoint ADDR`.
- `cycles`: Display number of cycles since last reset.



<!-------------------------------------------------------------------->
[py65-cmds]: https://py65.readthedocs.io/en/latest/index.html#command-reference
[py65]: http://py65.readthedocs.org/
[py65src]: https://github.com/mnaberez/py65
[vice-mon]: http://vice-emu.sourceforge.net/vice_12.html

[ASxxxx]: http://shop-pdp.net/ashtml/asxxxx.htm

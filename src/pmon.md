PMON Monitor Notes
==================


Commands
--------

Hexadecimal numbers are always accpeted in lower or upper case. Commands by
default are case-sensitive. (XXX: add a build-time option to make them
case-insensitive.)

(✓=implemented; ☆=proposed)

- ✓ ` `: do nothing (useful as separator on input line)
- ☆ `!`: assemble
- ☆ `,`: set range end (and start? probably better to leave pending)
- ✓ `[0-9A-Fa-f]`: enter pending value
- ✓ `:`: deposit data
- ✓ `^`: print newline (used for testing; could be reassigned)
- ☆ `i`: return from Interrupt
- ☆ `j`: Jump (JMP) to address
- ✓ `k`: Call (JSR) address (must not change input buffer or move stack)
- ☆ `l`: List disassembled instructions
- ✓ `q`: Quit (return to caller)
- ☆ `r`: Read data from device
- ☆ `s`: Show/set registers
- ☆ `v`: Verify data written to device
- ☆ `w`: Write data to device
- ✓ `x`: eXamine memory


Monitor Entry
-------------

The "machine state" is the current values of CPU registers and flags
(including modes such as decimal mode on the 6502) and other parts of the
system (e.g., values of certain bank switch registers) that affect the
running of the monitor. "Monitor state" is memory, vectors and possibly I/O
device state needed to run the monitor.

There are three ways to enter the monitor:

1. __Cold Start:__ Stack is set up in a system-dependent way and minimum
   initialization of machine state, monitor state and I/O devices is done
   to bring the machine to a defined initial state for a working monitor.
   This is the entry point from the reset vector on machines that reset
   into the monitor. This may not be a complete initialization in order to
   allow some previous state to be read after a reset.

2. __Warm Start:__ Saves current machine state (XXX can it always all be
   saved?), validates monitor state, initializes monitor state if invalid.

3. __Break:__ Vectored from a `BRK`, `SWI` or similar instruction
   (deliberately or accidentally executed) or interrupt (typically NMI).
   Saves all registers from interrupt stack frame, removes that stack
   frame, and monitor continues to use the stack in use when the break
   instruciton was reached. The `i` (return from interrupt) command will
   continue from after the break instruction, though using the monitor's
   current register settings rather than the originally saved ones.


Todo
----

- improve error messages (and space/$00 to term args?)
- fix rdline not accepting backspace when buffer full
- extract rdline from pmon, use only for tmc68 version
- command table continuation which will also test that `cmdtbl` is used
- add option for case-insensitive commands.
- variables, `&` to read from location, etc.
- test use of DAA for prnyb

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
- ☆ `j`: Jump (JMP) to address
- ✓ `k`: Call (JSR) address (must not change input buffer or move stack)
- ☆ `l`: List disassembled instructions
- ✓ `q`: Quit (return to caller)
- ☆ `r`: Read data from device
- ☆ `s`: Show/set registers
- ☆ `v`: Verify data written to device
- ☆ `w`: Write data to device
- ✓ `x`: eXamine memory


Todo
----

- fix rdline not accepting backspace when buffer full
- extract rdline from pmon, use only for tmc68 version
- command table continuation which will also test that `cmdtbl` is used
- add option for case-insensitive commands.
- variables, `&` to read from location, etc.
- test use of DAA for prnyb

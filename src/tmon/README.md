tmon: A Monitor for Tiny Systems
================================

This monitor is intended to run on low-memory systems (requiring only a few
dozen bytes of RAM for work area) and be as small as reasonably possible
while providing a more convenient interface than traditional monitors.

The monitor requires a terminal or display that has a non-destructive
backspace character (i.e., moves the cursor back without erasing what's
underneath the cursor); the only I/O routines required are single character
input and output.

Where "newline" is used below this refers to the ASCII `CR`/Ctrl-M or
`LF`/Ctrl-J characters or the Enter key on a system with built-in keyboard.
When "Cancel" is used below this refers to ASCII `NAK`/Ctrl-U or
`CAN`/Ctrl-X character.

The user is prompted with a `.` or similar small dot. Input is case
insensitive, and consists of _input items_ that are single characters
representing commands or parameter names and strings of hexadecimal
numbers. Entering an invalid character will produce an ASCII `BEL`
and the cursor will be backspaced over the invalid character.

The first character after the prompt must be one of the commands below.
Commands marked with a dagger (†) execute immediately; most commands
(including all that take parameters) must be confirmed with a newline
or cancelled with a cancel character.

Commands that do not immediately execute may be be followed by spaces
(which are printed but ignored), and command _parameters,_ each of which
must be followed by a _parameter value._

Parameter values come in two sizes: byte (two hex digits) or word (16 bits;
four hex digits), represented below by `x##` and `x####`. Missing leading
characters are assumed to be zero; extra leading characters are ignored.
Thus both `6` and `12340006` will be interpreted as $0006 for a word value.

During hexadecimal value input you may also type a single quote (`'`)
followed by any character, and the ASCII value of that character will be
taken as the next two digits of input. (This includes characters that are
otherwise treated specially, such as newline and cancel characters.) A
double quote (`"`) will do the same but with the high bit (bit 7) set.

Parameter value input is terminated by:
- a space, which will be printed and allow for further parameters to be set
  on the same line;
- a newline, which both terminates value input and executes the command; or
- a cancel character, which cancels value input (the parameter value will
  not be updated) and cancels the command.

Note that you cannot cancel parameter value settings once they are
terminated; typing `e s1234 f56` followed by a cancel character will cancel
the update of the `f` parameter (as well as the command), but the `s`
parameter update has already been made. (This saves memory by avoiding the
need of a command line input buffer.)

Rubout (ASCII `BS`/Ctrl-H, ASCII `DEL`/Ctrl-?, or similar keys on a
built-in keyboard) is not supported. Incorrect input may be cancelled with
the cancel character, but (per above) this does not apply to previous
parameter values that have already been set. Incorrect parameter values can
be corrected simply by continuing to type the correct value, with as many
leading zeros as necessary for the value size.


Commands
--------

Most parameters have a memorised value that will be used if a new value for
it is not specified when entering the command. This is marked with a § sign
before the parameter name.

Certain parameter names have a common meaning across all commands that
support them, unless otherwise described in the command description. (The
remembered value is not shared between commands except where noted.)
- `s####`: a start address.
- `e####`: an end address; the first address _after_ the range used by the
  command.

This is a summary of the commands, in ASCII (alphabetical) order.
The full command descriptions follow.

    '  †ASCII character deposit
    /   calculate and display value
    .  †hex byte deposit
    >  †hex word deposit
    :   deposit Intel hex record
    c   Copy memory
    d   set Deposit options
    e   Examine memory
    f   Find data in memory
    i   Interrupt return
    j   Jump to address
    k   call address
    l   Load data from storage device to memory
    o   Output (write) to I/O port
    p   read from I/O Port
    q   Quit (exit) monitor
    r   examine/edit Registers
    s   deposit Motorola S-record
    t   Transfer memory To storage device
    v   checksum (Verify) memory
    w  †Walk through (fast examine) memory

    Unused letters: a b  g h  m n  u  x y z

    XXX fill (can be done with copy?)

#### Execution

- `i` Interrupt return. This sets the stack to the saved value and executes
  an `RTI` or similar instruction. Useful for continuing after a `BRK`,
  `SWI` or similar instruction, or an NMI or other user-generated
  interrupt.

- `j` Jump to address given as §`s####`, "start address," which is shared
  with `k`. This reloads the saved registers and then jumps directly to the
  start address (i.e., `RTS` or `RET` will not return to the monitor).

- `k` Call address given as §`s####`, "start address," which is shared with
  `j`. This reloads the saved registers and loads the monitor entry point
  on the stack before executing at the start address, so that a `RTS` or
  `RET` will save the registers and return to the monitor.

- `q` Quit. Execute an `RTS` instruction, returning to the program that
  called the monitor. Depending on the system and the tmon entry point
  used, this may return to a default system monitor, BASIC or similar.
  Simulators will generally exit. Though this takes no parameters, it
  still requires confirmation (a newline) to avoid accidental exits.

#### Examining Machine State

- `e` Examine. Display memory in hex. Parameters:
  - §`s####`: Start address.
  - §`l##`: Number of lines to print (default 4).
  - §`w##`: Width as number of bytes to examine.
  - §`f##`: Format. This is a bitfield with values listed below; all
    formats that are enabled will be printed in sequence on the same line.
    - b0 ($01): Hex format as bytes separated by spaces.
    - b1 ($02): ASCII characters in "visible" form, where control
      characters and those with bit 7 set are shown as printable characters
      that may be distinguished in a special way.
    - b2 ($04): Screen codes, i.e., the character that is displayed if that
      value is deposited directly into the character buffer for the
      computer's display. (This generally produces just ASCII on systems
      without a built-in display.)
    - b3-7: Ignored.

- `w` "Walkthrough" examination of memory. The `e` command's start address
  `s####` will be updated to add the number of bytes it would display
  (`l##` × `w##`) and the examine (`e`) command will then be run. This can
  be used to examine forward through memory a page at a time, leaving the
  `e` command's start address at the start of the last examined range when
  you've found something of interest. This takes the same parameters as the
  `e` command, and all values are shared with the `e` command. Note that if
  you set the `s####` parameter here, it will start on the page _after_
  that address.

- `r` Examine/edit registers and flags. Execution with no parameters will
  display all registers and flags.
  - 8080/8085 parameters: `f##` (flags), `a##`, `b####` (BC pair),
    `d####` (DE pair), `h####` (HL pair), `s####` (stack pointer).
  - 6800 parameters: `f##` (flags), `a##`, `b##`, `x####`, `s####` (stack).
  - 6502 parameters: `f##` (flags), `a##`, `x##`, `y##`, `s##` (stack).

- `p` Read from I/O port. The only parameter is §`p##` or §`p####` for the
  port number, depending on the size of the I/O address space. This applies
  to machines with a separate I/O address space only.

- `f` Find data in memory. This command is optional and may not exist in
  all implementations. The parameters are:
  - §`s####`: address at which to start the search.
  - §`e####`: address at which to terminate the search.
  - §`t####`: address of target data to find. I.e., the search will find a
    byte in the s/e range that matches the byte at `t####`, the next byte
    must match the byte at `t####`+1, and so on, up to the length of the
    target data. (This may be any length up to the size of memory.)
  - §`l##`: The length of the search string stored at `t####`.
  - §`u##`: Update the find, examine and/or deposit start addresses (bitfield).
    - b0 ($01): Update the find `s####` address to the address at which the
      data were found.
    - b1 ($02): Update the examine `s####` address to the address at which
      the data were found.
    - b2 ($04): Update the deposit `s####` address to the address at which
      the data were found.

- `v` Checksum ("Verify") memory, starting at §`s####` up to (but not
  including) §`e####/`, and print the result. Both `s` and `e` parameter
  values are shared with the `c` (Copy) command below. The algorithm is
  selected with §`f##` (mnemonic "Format"), and is one of:
  - 0: [BSD checksum], as used by the Unix `sum` utility. A 16-bit checksum
    computed by, for each character, rotating right the accumulated 16-bit
    sum and then adding the character value to it.

#### Depositing Data

- `d` Set deposit options for `.`, `>` and `'` commands.
  - §`s####`: The address at which the next deposit will start.
  - `e##`: Copy examine start address to deposit start address. `##` must
    be any non-zero value. This is executed _after_ the command is
    confirmed and so will override any `s####` values given as parameters
    to the command. If set accidentally, it may be disabled with `e0`.
  - §`a##`: Advance mode. This may be:
    - $00: After executing a deposit command the §`s####` start address for
      the next deposit command will remain the same.
    - $01: After executing a deposit command, the §`s####` start address
      will be updated to the address after the last deposited, so the
      deposited will start filling memory after the last deposited byte.
  - §`q##`: Deposit data echo/quiet (optional).

- `<` Hex byte entry. The byte at the current address is displayed as two
  digits `##` and then backspaced over. Entering a space will skip to the
  next address, leaving that value intact in memory. Entering one or two
  digits followed by a space will replace that value in memory. Newline
  terminates entry and, if advance mode is set, updates the deposit start
  address to the address after the one where you terminated this command.

- `>` Hex word entry. Works as `>` but displaying two bytes in big-endian
  format, though read and written from memory in the machine's endianness.
  I.e., on i8080 or 6502 two consecutive locations containing $CD and $AB
  will be displayed and entered as `ABCD`.

- `'` ASCII entry. Works as to `>` but the value is displayed as an ASCII
  character using the same visible print routine as the `E` examine
  command's ASCII option. Typing a single letter or symbol (including
  space) immediately enters that value. (It is not possible to skip over
  locations in this mode.)

- `:` Deposit Intel hex record. All data from the colon to the next newline
  is read as [Intel hex format][intel] and deposited into memory at the
  address given in the record. A warning is printed if the checksum is
  incorrect or another format error occurs, but all data up to the error
  are still deposited into memory.

- `s` Deposit Motorola S-record. Data from the `S` (upper or lower case) to
  the next newline is read as a [Motorola S-record][motorola] and deposited
  into memory at the address given in the record. Error handling is as `:`
  above.

- `o` Output (write) to I/O port. Parameters are §`p##` or §`p####` for the
  port address (depending on the size of the machine's I/O address space)
  and §`d##` for the data to write. This applies to machines with a
  separate I/O address space only.

- `c` Copy memory from §`s####` up to (but not including) §`e####` to
  location §`t####` (target). The `s` and `e` parameters are shared with
  the `f` (Find) command above.

#### External Storage

- `l`: Load data from device to memory. (Parameters TBD. `v##` for verify?)
- `t`: Transfer data from memory to device (mnemonic, "To").
  (Parameters TBD.)

#### Miscellaneous Commands

- `/` Calculate values. This command has two parameters, §`?####` and
  §`/####`. The `/` parameter value will be added to the `?` parameter
  value and the result will be displayed as hex, visible ASCII and a screen
  code. Additionally the second may be subtracted from the first and
  displayed as hex. (This command is optional and may not be present in all
  monitors.)


Notes
-----

Previous versions of this document suggested that on typing a parameter
name the monitor should immediately display the current value of that
parameter and backspace over it. It's not clear if we're going to implement
that.



<!-------------------------------------------------------------------->
[intel]: https://en.wikipedia.org/wiki/Intel_HEX
[motorola]: https://en.wikipedia.org/wiki/SREC_(file_format)
[BSD checksum]: https://en.wikipedia.org/wiki/BSD_checksum

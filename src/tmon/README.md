tmon: A Monitor for Tiny Systems
================================

This monitor is intended to run on low-memory systems (requiring only a few
dozen bytes of RAM for work area) and be as small as reasonably possible
while providing a more convenient interface than traditional monitors.

The monitor is requires a terminal or display that has a non-destructive
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
This may be followed by spaces (which are printed but ignored), and command
_parameters,_ each of which must be followed by a _parameter value._

Parameter values come in two sizes: byte (two hex digits) or word (16 bits;
four hex digits), represented below by `x##` and `x####`. Missing leading
characters are assumed to be zero; extra leading characters are ignored.
Thus both `6` and `12340006` will be interpreted as $0006 for a word value.

During hexadecimal value input you may also type a single quote (`'`)
followed by any character, and the ASCII value of that character will be
taken as the next two digits of input. (This includes characters that are
otherwise treated specially, such as newline and cancel characters.)

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

This is a summary of the commands, in ASCII (alphabetical) order:

    '   ASCII character deposit at updating address
    /   calculate and display value
    <   hex byte deposit at updating address
    >   hex word deposit at updating address
    =   set updating address for associated deposit commands
    :   deposit Intel hex record
    b   copy `d` deposit address to updating address
    c   Copy memory
    d   Deposit to memory while examining it
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
    v   checksum (Verify) memory
    w   Write memory data to storage device

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
  Simulators will generally exit.

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

- `r` Examine/edit registers and flags. Execution with no parameters will
  display all registers and flags.
  - 8080/8085 parameters: `f##` (flags), `a##`, `b####` (BC pair),
    `d####` (DE pair), `h####` (HL pair), `s####` (stack pointer).
  - 6800 parameters: `f##` (flags), `a##`, `b##`, `x####`, `s####` (stack).
  - 6502 parameters: `f##` (flags), `a##`, `x##`, `y##`, `s##` (stack).

- `f` Find data in memory. This command is optional and may not exist in
  all implementations. The parameters are:
  - §`s####`: address at which to start the search.
  - §`e####`: address at which to terminate the search.
  - §`t####`: address of target data to find. I.e., the search will find a
    byte in the s/e range that matches the byte at `t####`, the next byte
    must match the byte at `t####`+1, and so on, up to the length of the
    target data.
  - §`l##`: The length of the search string at `t####`.

- `v` Checksum ("Verify") memory, starting at §`s####` up to (but not
  including) §`e####/`, and print the result. Both `s` and `e` parameter
  values are shared with the `c` (Copy) command below. The algorithm is
  selected with §`f##` (mnemonic "Format"), and is one of:
  - 0: [BSD checksum], as used by the Unix `sum` utility. A 16-bit checksum
    computed by, for each character, rotating right the accumulated 16-bit
    sum and then adding the character value to it.

- `p` Read from I/O port. The only parameter is §`p##` or §`p####` for the
  port number, depending on the size of the I/O address space. This applies
  to machines with a separate I/O address space only.

#### Depositing Data

- `d` Deposit/examine byte by byte, starting at §`s####`. After pressing
  Enter this will display the current start address and current value at
  that address in hex, `##`, which is then backspaced over. Pressing space
  will preserve the value at that location and skip to the next location;
  entering one or two hex digits followed by space will update the value at
  that location. Either way, it will then print a space and the next byte
  for similar skip/entry. Every eight bytes a new line will be started with
  the next address displayed again. Terminate the command by pressing
  Enter.

- `c` Copy memory from §`s####` up to (but not including) §`e####` to
  location §`t####` (target). The `s` and `e` parameters are shared with
  the `f` (Find) command above.

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

All of the following commands share a common current address, known as the
"updating address." Unlike most commands, the address is updated with each
byte or word of data entered. That is, where using `d` a second time will
start at the same address as `d` did the previous time, using `<` to enter
a byte followed by `'` to enter a character will place those values into
two consecutive addresses and the next use of any of these commands will
start at the address after that.

- `<` Hex byte entry at updating `=` address. The byte at the current
  address is displayed as two digits `##` and then backspaced over.
  Entering a space will skip to the next address, leaving that value intact
  in memory. Entering one or two digits followed by a space will replace
  that value in memory. Newline terminates entry.
- `>` Hex word entry at updating `=` address. Works as `>` but displaying
  two bytes in big-endian format, though read and written from memory in
  the machine's endianness. I.e., on Z80 two consective locations
  containing $CD and $AB will be displayed and entered as `ABCD`.
- `'` ASCII entry at updating `=` address. Similar to `>` but the value is
  displayed as an ASCII character, if printable, or a space otherwise.
  Typing a single letter or symbol (including space) immediately enters
  that value. (It is not possible to skip over locations in this mode.)

The common "current" address of the above commands may be set with:

- `=` Set updating address for hex/ASCII entry. This has no parameter
  letters, but immediately takes a non-optional §`####` address.
- `b` Copy `d` (deposit) start address to hex/ASCII entry address. This is
  essentially the same as `=` except that the address is optional, and the
  default value is the `s####` address memorised for `d`. (Mnemonic:
  reversed 'd'.)

#### External Storage

- `l`: Load data from device to memory. (Parameters TBD. `v##` for verify?)
- `w`: Write memory data to device. (Parameters TBD.)

#### Miscellaneous Commands

- `/` Calculate values. This command has two parameters, §`?####` and
  §`/####`. The `/` parameter value will be added to the `?` parameter
  value and the result will be displayed as hex, visible ASCII and a screen
  code. Additional the second may be subtracted from the first and
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

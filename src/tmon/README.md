tmon: The Tolerable Monitor
===========================

`tmon` is a monitor intended to be small and run on systems with minimal
memory, while providing a full-featured and convenient user interface. You
may think of the "t" as standing for "tolerable" and (moderately) "tiny."

The general goals are to have:
* Reasonably small code size: under 2 KB and ideally around 1 KB.
* Very minimal RAM usage: just 2-3 dozen bytes so it can run on e.g. a 6802
  with only its 128 bytes of internal RAM.
* Significantly better features than many home computers' built-in
  monitors, including properly handling the usercode stack (or working
  without a valid usercode stack).
* A user interface focused on convenience. For example, remembering
  recently used addresses so you need not continually re-type them and
  allowing you to intersperse hex and ASCII data input.
* Efficient use of the display, allowing you to display just what you need
  and minimise non-informational printing to reduce useful information
  scrolling off the screen.

The monitor requires a terminal or display that has a non-destructive
backspace character (i.e., moves the cursor back without erasing what's
underneath the cursor) and separate CR and LF (the former returning to the
start of the current line; the latter moving down a line). The only I/O
routines required are single character input and output. (The single
character input may be blocking.)

### Availability and Source Code

If you've received this README as part of a binary distribution, you can
find the current version of it and all tmon source code in the
[`0cjs/8bitdev`] repo on GitHub. The README and CPU-independent files are
be under `src/tmon/`, the source is under `src/CPU/` where _CPU_ is a CPU
identifier (e.g., `i8080`), and the top-level source files for specific
platforms are under `exe/` (e.g., `exe/cpm/tmon.i80`). The source includes
a full set of unit tests (written in [pytest]) and manual testing can be
done at a command-line CPU/system simulator.


Usage
-----

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
Commands marked with a superscript 1 (¹) are "single key" commands that
execute immediately. All other commands (including all that take
parameters) must be confirmed with a newline or cancelled with a cancel
character.

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

Though many commands have some sort of mnemonic value, a primary design
goal is to to have them placed conveniently on the keyboard, with examine
commands on the left hand and modification commands on the right.

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

    '  ¹ASCII character deposit
    ,   set deposit parameters (next to ",>" deposit key)
    .  ¹hex byte deposit
    /   calculate and display value
    :   deposit Intel hex record
    ;   modify (deposit to) registers
    >  ¹hex word deposit
    a   examine assembly code
    b  ¹examine memory Backwards (display previous page)
    d  ¹examine ("Display") memory at current location
    e   set Examine memory parameters
    f  ¹examine memory Forward (display next page)
    i   Interrupt return
    j   Jump to address
    k   call address
    m   copy ("Move") memory
    o   Output (write) to I/O port
    p   read from I/O Port
    q   Quit (exit) monitor
    r  ¹examine Registers
    S   deposit Motorola S-record
    t   Transfer memory To storage device
    v   checksum (Verify) memory
    w   find data in memory ("Where")
    y   read into memory from storage device ("yank")

    Unused letters: c g h l n u x z

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

- `q` Quit. Return to the program that called the monitor. Depending on the
  system and the tmon entry point used, this may return to a default system
  monitor, BASIC or similar. Simulators will generally exit. Though this
  takes no parameters, it still requires confirmation (a newline) to avoid
  accidental exits.

#### Examining Machine State

- °`r` Examine registers and flags. See the `;` command for details of what
  is displayed.

- `e` Set memory examine parameters. This does not display anything, but
  sets the parameters that will be used by the `d`, `f`, and `b` commands.
  - §`s####`: Start address.
  - §`l##`: number of Lines to print (default 4).
  - §`w##`: Width as number of bytes to examine.
  - §`m##`: display Mode. This is a bitfield with values listed below; all
    display modes that are enabled will be printed in sequence on the same line.
    - b0 ($01): hexadecimal values as bytes separated by spaces.
    - b1 ($02): ASCII characters in "visible" form, where control
      characters and those with bit 7 set are shown as printable characters
      that may be distinguished in a special way.
    - b2 ($04): screen codes, i.e., the character that is displayed if that
      value is deposited directly into the character buffer for the
      computer's display. (This generally produces just ASCII on systems
      without a built-in display.)
    - b3-7: ignored.

- °`d` Examine ("Display") memory. Displays the contents of memory using
  the location and format set by the `e` command.

- °`f` Examine Forward. The `e` command's start address `s####` will be
  updated to add the number of bytes that `d` would display (`l##` × `w##`)
  and the display (`d`) command will be executed. This can be used to
  examine forward through memory a block at a time, leaving the `e`
  command's start address at the start of the last examined range when
  you've found something of interest.

- °`b` Examine Backwards. As with `f`, but it subtracts the number of bytes
  that `d` would display to display the previous block of memory.

- `p` Read from I/O port. The only parameter is §`p##` or §`p####` for the
  port number, depending on the size of the I/O address space. The port is
  read and the value is displayed. This is available only on machines with
  a separate I/O address space.

- `w` Find data in memory ("Where"). (This command is optional and may not
  exist in all implementations.) The parameters are:
  - §`s####`: address at which to start the search.
  - §`e####`: address at which to terminate the search.
  - §`t####`: address of target data to find. I.e., the search will find a
    byte in the s/e range that matches the byte at `t####`, the next byte
    must match the byte at `t####`+1, and so on, up to the length of the
    target data. (This may be any length up to the size of memory.)
  - §`l##`: The length of the search string stored at `t####`.
  - §`u##`: Update the find, examine and/or deposit start addresses
    (bitfield).
    - b0 ($01): Update the find `s####` address to the address at which the
      data were found.
    - b1 ($02): Update the examine `s####` address to the address at which
      the data were found.
    - b2 ($04): Update the deposit `s####` address to the address at which
      the data were found.

- `v` Checksum ("Verify") memory, starting at §`s####` up to (but not
  including) §`e####/`, and print the result. Both `s` and `e` parameter
  values are shared with the `c` (Copy) command below. The CRC-16-CCITT
  checksum algorithm is always available; in some implementations an `m##`
  parameter (mnemonic "Mode") can select other algorithms. If available,
  they are:
  - $00: [CRC-16-CCITT][] (x¹⁶+x¹²+x⁵+1), used by Xmodem and many other
    tools.
  - $01: [BSD checksum], as used by the Unix `sum` utility. A 16-bit
    checksum computed by, for each character, rotating right the
    accumulated 16-bit sum and then adding the character value to it.

#### Modifying Machine State (Depositing Data)

- `;` Edit and examine registers and flags. Execution will display all
  registers and flags. To save space, the register values display does not
  display the names of registers, but the order is the same as the order of
  parameters given below. You can always enter a command parameter to
  confirm the current value of a register. Flags are entered as a byte
  value, but displayed as capital letters for set flags and `-` for cleared
  flags.
  - All platforms:  `p####` (program counter),  `s####` (stack pointer, may
    be `s##` on some systems), `f##` (flags).
  - 8080/8085 parameters: 
    - Byte-width registers `a##`, `b##`, `c##`, `d##`, `e##`, `h##`, `l##`.
    - Word-width register pairs `i##` (BC, "Index counter") `t##` (DE,
      "Target address"), `m##` (HL, "Memory access register"),
  - 6800 parameters: `a##`, `b##`, `x####`.
  - 6502 parameters: `s##` (stack pointer), `a##`, `x##`, `y##`,

- `,` Set deposit options for `.`, `>` and `'` commands.
  - §`s####`: The address at which the next deposit will start.
  - `e##`: Copy examine start address to deposit start address. `##` must
    be any non-zero value. This is executed _after_ the command is
    confirmed and so will override any `s####` values given as parameters
    to the command. If set accidentally, it may be disabled with `e0`.
  - §`n##`: advance to Next mode. This may be:
    - $00: After executing a deposit command the §`s####` start address for
      the next deposit command will remain the same.
    - $01: After executing a deposit command, the §`s####` start address
      will be updated to the next address after the last deposited, so the
      deposited will start filling memory after the last deposited byte.
  - §`q##`: Deposit data echo/quiet (optional).

- °`.` Hex byte entry. The byte at the current address is displayed as two
  digits `##` and then backspaced over. Entering a space will skip to the
  next address, leaving that value intact in memory. Entering one or two
  digits followed by a space will replace that value in memory. Newline
  terminates entry and, if advance mode is set, updates the deposit start
  address to the address after the one where you terminated this command.

- °`>` Hex word entry. Works as `>` but displaying two bytes in big-endian
  format, though read and written from memory in the machine's endianness.
  I.e., on i8080 or 6502 two consecutive locations containing $CD and $AB
  will be displayed and entered as `ABCD`.

- °`'` ASCII entry. Works as to `>` but the value is displayed as an ASCII
  character using the same visible print routine as the examine commands'
  ASCII option. Typing a single letter or symbol (including space)
  immediately enters that value. Enter Ctrl-N to skip over locations,
  preserving the previous value.

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
  and §`v##` for the data to write. This applies only to machines with a
  separate I/O address space.

- `m` Copy ("Move") memory from §`s####` up to (but not including) §`e####`
  to location §`t####` (target). The `s` and `e` parameters are shared with
  the `w` (Find/Where) command above.

#### External Storage

- `y`: Load data from device to memory. (Parameters TBD. `v##` for verify?)
- `t`: Transfer data from memory to device (mnemonic, "To").
  (Parameters TBD.)

#### Miscellaneous Commands

- Ctrl-M: Print a newline.

- `/` Calculate values. This command has two parameters, the left value
  §`?####` and the right value §`/####`. It displays the values of
  left/`?`, right/`/`, the sum of the two (left + right) .in hex, the
  character and screen code of the LSB of that result, and the same again
  for the difference (left - right).



<!-------------------------------------------------------------------->
[`0cjs/8bitdev`]: https://github.com/0cjs/8bitdev/
[intel]: https://en.wikipedia.org/wiki/Intel_HEX
[motorola]: https://en.wikipedia.org/wiki/SREC_(file_format)
[pytest]: https://pytest.org/

<!-- checksum algorithms -->
[BSD checksum]: https://en.wikipedia.org/wiki/BSD_checksum
[CRC-16-CCITT]: https://en.wikipedia.org/wiki/Cyclic_redundancy_check#Polynomial_representations

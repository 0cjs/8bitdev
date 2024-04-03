tmon: A Monitor for Tiny Systems
================================

This monitor is intended to run on low-memory systems (requiring only a few
dozen bytes of RAM for work area) and be as small as reasonably possible
while providing a more convenient interface than traditional monitors.

The monitor is requires a terminal or display that has a non-destructive
backspace character (i.e., moves the cursor back without erasing what's
underneath the cursor); the only I/O routines required are single character
input and output.

Where "Enter" is used below this refers to either a `CR` (Ctrl-M) or `LF`
(Ctrl-J) ASCII character, or the Enter key on a system with built-in
keyboard and display. Where "rubout" is used below this refers to either a
`BS` (Ctrl-H) or `DEL` ASCII character, or a backspace/delete/rubout or
similar key.

The user is prompted with a `.` or similar small dot. Input is case
insensitive, and consists of _input items_ that are single characters
representing commands or options and hexadecimal numbers. Entering rubout
will erase only the most recent input item; after erasing one item it is
not possible to erase any previous items. (This reduces the size of the
input buffer.) Spaces are generally printed but ignored. A command is
executed with Enter or is cancelled with `NAK` (Ctrl-U) or `CAN` (Ctrl-X).

When entering hexadecimal values, either a two- or a four-digit item will
be accepted, depending on the command or option. Digit input is terminated
by a space, which starts a new item, or Enter to execute the command. On
reaching the maximum number of digits any further digits will be rejected
and a `BEL` will be output. Entering rubout erases the entire sequence of
digits so far entered and, where a previous value has been memorised,
redisplays that previous value.


Commands
--------

Most commands accept optional parameters that are single characters
followed by a hex digits item, written as `##` for eight-bit values and and
`####` for 16-bit. Most parameters have a remembered value that will be
printed and then backspaced over; a new value can be typed over top of this
or just a space may be entered to keep the current remembered value
unchanged.

Optional parameters common to several commands are as follows. (The
remembered value is not shared between commands except where marked.)
- `s####`, a start address.

#### Execution

- `i` Interrupt return. This sets the stack to the saved value and executes
  an `RTI` or similar instruction. Useful for continuing after a `BRK`,
  `SWI` or similar instruction, or an NMI or other user-generated
  interrupt.

- `j` Jump to address. This reloads the saved registers and then jumps
  directly to the start address (i.e., `RTS` or `RET` will not return to
  the monitor). (XXX implement as a `JMP` instruction before the remembered
  value.) Memorised parameter `s####` shared with `k`.

- `k` Call address. This reloads the saved registers and loads the monitor
  entry point on the stack before executing at the start address, so that a
  `RTS` or `RET` will save the registers and return to the monitor.
  Memorised parameter `s####` shared with `j`.

- `q` Quit: execute an RTS instruction, returning to the program that
  called the monitor (if present).

#### Examining Machine State

- `e` Examine. Display memory in hex. Parameters:
  - `s####`: Start address.
  - `l##`: Number of lines to print (default 4).
  - `w##`: Width as number of bytes to examine.
  - XXX Add ASCII and screen code options
  - XXX Add memory space option?

- `r` Examine/edit registers and flags. Entry with no parameters will
  display all registers and flags.
  - Z80 parameters: `f##` (flags), `a##`, `b####` (BC pair),
    `d####` (DE pair), `h####` (HL pair), `s####` (stack pointer).
  - 6502 parameters: `f##` (flags), `a##`, `x##`, `y##`, `s##` (stack).
  - 6800 parameters: `f##` (flags), `a##`, `b##`, `x####`, `s####` (stack).

#### Depositing Data

- `d` Deposit/examine byte by byte. After pressing Enter this will display
  the current start address and current value at that address in hex, `##`,
  which is then backspaced over. Pressing space will preserve the value at
  that location and skip to the next location; entering one or two hex
  digits followed by space will update the value at that location. Either
  way, it will then print a space and the next byte for similar skip/entry.
  Every eight bytes a new line will be started with the next address
  displayed again. Terminate the command by pressing Enter.
  - Parameters: `s####`.

All of the following commands share a common "current" address that, unlike
most commands, is updated with each byte or word of data entered. That is,
where using `d` a second time will start at the same address as `d` did the
previous time, using `>` to enter a word followed by `'` to enter a
character will place those values into two consecutive addresses and the
next use of any command will start at the address after that.

- `>` Hex byte entry at updating `a` address. The byte at the current
  address is displayed as two digits `##` and then backspaced over.
  Entering a space will skip to the next address, leaving that value intact
  in memory. Entering one or two digits followed by a space will replace
  that value in memory. Newline terminates entry.
- `<` Hex word entry at updating `a` address. Works as `>` but displaying
  two bytes in big-endian format, though read and written from memory in
  the machine's endianness. I.e., on Z80 two consective locations
  containing $CD and $AB will be displayed and entered as `ABCD`.
- `'` ASCII entry at updating `a` address. Similar to `>` but the value is
  displayed as an ASCII character, if printable, or a space otherwise.
  Typing a single letter or symbol (including space) immediately enters
  that value. (It is not possible to skip over locations in this mode.)

The common "current" address of the above commands may be set with:

- `a` Set address for hex/ASCII entry. This has no parameter letters,
  but immediately prints/takes a non-optional `####` address.
- `b` Copy `d` (deposit) start address to hex/ASCII entry address.
  This is essentially the same as `a` except that the default adddress
  is the `s####` address memorised for `d`. (Mnemonic: reversed 'd'.)

#### Load/Save

- `:` Load Intel hex record.
- `S` Load Motorola S-record.

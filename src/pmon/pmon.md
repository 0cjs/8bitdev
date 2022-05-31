pmon Monitor
============

Features:
- Designed for interactive exploration of the machine.
- No input buffer required, just a minimal amount of memory for building
  byte and word values from hex input. (However, this means that each
  command is executed immediately after you've finished specifying its
  parameters.)
- Minimises typing by keeping track of recently used command parameters and
  allowing command execution without specifying them again. (We're working
  on ways to and options for reducing the amount of memory this uses.)
- Parsimonious with screen area on small terminals and video displays to
  help delay information scrolling off the screen. Input is (usually)
  cleared and written over by command output. Display commands have
  parameters to help display just what you need as compactly as possible.


Supported Hardware
------------------

pmon is designed for use on "glass TTY" terminals with the following
capabilities:
- Input is not echoed by the terminal (i.e., it relies on the computer to
  echo characters when appropriate).
- ASCII backspace (BS, $08) moves the cursor one character position left
  without erasing the character underneath the new cursor position.
- ASCII carriage return (CR, $0D) moves the cursor to the beginning of the
  current line without erasing any characters.
- ASCII newline (NL, $0A) moves the cursor down to the next line, with or
  without an implicit return to the start of the line. (A CR will always
  be sent before an NL.)

There is limited support for printing terminals (e.g., Flexowriter,
Teletype, DECwriter); set the `p` global parameter (with `$p1`) to enable
this. This will not eliminate all overprinting, however.

The Apple 1 supports only CR, which moves to the beginning of the next
line. (Neither BS nor any other control characters are supported.) On
systems such as this the `$p` parameter will not be supported, only CR will
be used and backspace (where it's valid input) will instead print `*` to
indicate that the character(s) before the asterisk(s) have been rubbed out.

### Lower and Upper Case

Input and output are always lower case by default.
- Systems without a shift key that normally generate upper case from the
  keyboard will instead generate lower case. Typing Ctrl-A will make the
  next input character upper case.
- Systems without lower-case display show lower-case characters as upper
  case and upper-case characters as inverted upper case or, if inverse is
  not available, may use a `^` prefix in front of upper case letters. (The
  prefix will not be used in block output, such as ASCII output from the
  e)xamine command; for these you need to check the hex display to see if
  the value is lower or upper case.


Command Entry
-------------

At the `.` prompt you may enter a single-character command optionally
followed by parameters that determine the behaviour of the command. After
entering the command character, a single character identifies a particular
parameter; this may be followed by by an parameter value such as an
address. Unrecognised command and parameter characters will print the
character, backspace over it and generate an error beep.

Backspace just after a command or parameter character will clear that
command/parameter character (unless the parameter takes no value, in which
case it has already updated the command parameters), leaving you ready to
enter another one. Backspace at any other time (including after a space
that followed a command character, parameter character or parameter value) will
generate an error beep.

Return/Enter will terminate command/parameter input, print a CR (leaving
the cursor on the same line) and execute the command. Space will terminate
ongoing parameter value input input for an option which allows you to enter
less than the full number of digits for things like numeric option
parameters.

### Command Parameters

Parameters not specified use their previously remembered value or, in some
cases, a default value. Parameter value input directly follows the
parameter character:
- Space will print the currently remembered value.
- Hex digits will set the value. Type either all required nybbles or end
  with a space, whereupon the most significant unspecified nybbles will be
  assumed to be 0. (I.e., for a word value, `E ` will be taken to mean
  $000E.) A space will not be printed after the parameter value unless the
  user typed it to terminate parameter value input before typing the full
  number of digits.

- `/A`, where _A_ is any letter, will use the value from user variable _A._
- `@AB`, where _A_ is a command character and _B_ is a valid parameter
  character for that command, will use the remembered value for that
  parameter to that command. (E.g., `es1234 ` followed by `l@xs` will
  examine memory starting at $1234 and then disassemble memory starting at
  that same location.)
- Invalid characters and invalid values will print a `?` and beep to
  indicate an error and you will be left in value input mode for that
  parameter. (XXX or in parameter input mode?)
- XXX should we support backspace during value input, or just leave it as
  an error that clear all value input to that point?

Parameters specified more than once will use the most recently specified
value. Thus during parameter input you can type `p p0 ` to show the current
value and then change it to a new value.

Parameter letters are followed by values are of the following types:
- No value (`x`): an "immediate" parameter immediately takes effect without
  waiting for any further input.
- Boolean (`x1`): follow the parameter letter with `0`, `1` or `.`. `0`
  sets the parameter to false, `1` to true, and `.` prints and sets the
  inverse of the current value.
- Nybble (`xF`): 1 hex digit.
- Byte (`x00`): 1-2 hex digits.
- Word (`x0000`): 1-4 hex digits.
- Letter (`xA`): 1 ASCII letter. (XXX case-insensitive? Probably not.)

For all of the above that accept a number, the value may be of the form
`/A` to enter the value currently in user variable _A._ The least
significant bits corresponding to the length of the parameter value will be
used: bit 0 for boolean, bits 4-0 for nybble, bits 7-0 for byte, and all
bits for word.

`$` is a special parameter character for all commands with the following
subfunctions:
- `$$`: terminate command input and print `=`, the command character, and
  all parameters and their current values.
- `$=`: As with `$$`, but after that it resets all parameters to their
  default values and again prints out the current values.

XXX Add `.` as a byte/word parameter value to increment the currently
remembered value by a command-specific amount? Would this be useful for
anything but start address?


Commands
--------

Parameter letters below are followed by further characters to indicate the
type of their value; see the parameter value types list above.

The following are some standard parameters common to multiple commands.
(Commands using these note them with "SP" below.) Not all commands using
parameters with these letters will be using these standard parameters,
however. All parameters are remembered separately for every command.
- `a0000`: Primary address (start address for data display, etc.).
- `n`, `p`: Next and previous primary address. Increments or decrements `a`
  address by a command-specific amount.
- `e0000`: End address (1 past the last address used by the command).

### Command Summary

    $   set ("$et") monitor global parameters
    &   execute via return from interrupt
    /   display/set user variables
    :   deposit data into memory†
    ?   calculate/display values
    c   call (execute via JSR; RTS returns to monitor)
    e   examine memory
    f   fill memory
    g   goto (execute via JMP)
    i   input from device
    l   disassemble ("list")
    n   single-step ("next instruction")
    o   output to device
    x   exit monitor
    q   display/set status flags (condition codes)
    r   display/set registers
    s   transfer/compare data from/to offline storage
    t   copy ("transfer") memory
    v   compare ("verify") memory

### Memory/Data Display Commands

- `e`: Examine memory. SP `a0000`, `n`, `p`, `e0000`, and:
  - `l00`: Number of lines to display. 0 means display to end address.
  - `w0`: Number of values to display per line ("width"). 1-F; 0=16.
  - `h1`: enable hex display of each value.
  - `t1`: enable ASCII ("text") display of each value.
  - `s1`: enable screen code display of each value (video systems only)
  - `c1`: compact display format: displays only part of the address and
    removes most spaces.

- `i`: Input from device. This command reads just one address and is
  guaranteed to read it only once. SP `a0000`, `n`, `p`, and:
  - `m1`: Use memory mapped I/O. `1` is the standard memory address space
    on all machines. `0` uses I/O address space on Intel/Zilog CPUs (the
    MSB is ignored) and may use a system-specific MSB or bank on systems
    without an I/O address space (Motorola, MOS).

- `l`: Disassemble ("list") instructions. (Not yet implemented.)
  SP `a0000`, `n`, `p`.

- `v`: Compare ("verify") memory. Parameters and behaviour same as `t`/copy:
  SP `a0000` and `e0000` for the source; target address is `t0000`.

### Memory/Data Display/Change Commands

- `r`: Display/set registers. Each parameter character corresponds to a register.
  Registers can be individually displayed during parameter entry by typing the
  register letter followed by a space, and set with register letter
  followed by a value (and optional space). The entire set of registers
  will be displayed after pressing Return/Enter to terminate parameter entry.
  - Parameters common to all CPUs are `p` (program counter), `s` (stack),
    and `f` (flags, status, condition codes or program status register).
  - 8080: `p0000`, `s0000`, `f00`, `a00`,
          `b0000`, `c00`, `d0000`, `e00`, `h0000`, `l00`
  - Z80: as 8080, plus `x0000`, `y0000` `i00` `r00`; `z1` for alternate regs.
  - 6800: `p0000`, `s0000`, `f00`, `a00` `b00` `x0000`
  - 6502: `p0000`, `s00`,   `f00`, `a00` `x00` `y00`

- `q`: Display/set status flags. This command makes flags easier to read
  and set than directly using the flags register with `r`.
  (XXX work this out.)

### Deposit Command and Modes

The `:` command starts deposit of data into memory.† Unlike the other
commands, this command starts execution with space entered while input of a
new parameter character is pending. (I.e., `: ` or `:s1234  ` will start
accepting data for deposit, `:s123 ` will wait for another parameter
character or space. The only parameters are those to set the start address:
SP `a0000`, `n`, `p`.

When deposit starts, the cursor is returned to the start of the line, the
current address and the following 8 bytes of data are printed, and the
cursor is returned to the first byte of data. At this point you are in hex
input mode and can type:
- Space to leave the current value as is and move forward to the next value.
- Two hex digits (optionally followed by a space) to deposit a new value to
  that location and move on to the next.
- `'a` to deposit ASCII character _a._ (`$'` will switch to ASCII mode
  until turned off; see below for more on ASCII mode.)
- `/a` to deposit the contents of the LSB of user variable _a._
- `//a` to deposit the 16-bit contents of user variable _a_ into the
  current and following address. (This will be done in the machine's normal
  endian order.)
- Return/Enter to terminate the deposit command.

Entering `'` during hex deposit switches to ASCII mode for the next
character: the next character you type is read, deposited and its hex
representation printed over the previous value at that location. Entering
`$'` during deposit switches to ASCII mode for all subsequent characters
until turned off. During this mode `$nn` will enter a byte using
hexadecimal, `$$` will enter an ASCII dollar sign, and `$.` will return to
hex input mode.

Deposited values are immediately read back and, if the read value is not
the same as the deposited value, the read value is printed over the deposit
value that was typed in and an error beep is sounded. (Note that this can
cause problem for I/O to devices; for those use the `i` (input) and `o`
(output) commands instead.)

XXX Add `v1` param to turn on/off deposit verification?

### Memory/Data Change Commands

- `f`: Fill memory. SP `a0000`, `e0000`. `v0000` specifies the fill value.

- `t`: copy ("move") memory. SP `a0000` and `e0000` for the source; `t0000`
  gives the target address. If the target address is between the start and
  end addresses the copy will start at the end address - 1 and work down to
  the start address, otherwise it will start at the start address and work
  up.
  - If parameter `v1` is set, each byte will be read after it's written and
    the copy will be aborted if the byte fails to read back correctly.

- `o`: Output to device. This command writes just one address and (unlike
  the deposit command) is guaranteed both never to read the address and to
  write it only once. SP `a0000`, `n`, `p`, and:
  - `v00`: The value to write.
  - `m1`: Use memory mapped I/O. `1` is the standard memory address space
    on all machines. `0` uses I/O address space on Intel/Zilog CPUs (the
    MSB is ignored) and may use a system-specific MSB or bank on systems
    without an I/O address space (Motorola, MOS).

- `s`: Load/save/verify data from/to offline storage (tape, serial port in
  S-record or Intel hex format, xmodem upload/download, read or write
  programmable ROMs, etc.). Starting/ending/entrypoint addresses will be
  printed after load. SP `a0000` (start address), `e0000` (end address + 1),
  and:
  - `a0000` specifies the address at which to load or save data; `aFFFF`
    indicates that the load address(es) should be taken from the file.
  - If the file format includes an entrypoint or execution address, user
    variable _x_ will be set to that on load, or written to the file on
    save.
  - XXX work out the details of device selection, etc. Maybe addresses of
    I/O routines? Probably very system-specific.

### Code Execution Commands

All commands below load all registers from the saved values (dispalyed/set
with `r`) before executing. For `c` and `g` the program counter is excepted
from this; it's loaded from the remembered value of the `a0000` parameter.

- `c`: Call (execute via JSR). Pushes return to monitor address on stack.
  SP `a0000`.
- `g`: Goto (execute via JMP). RTS will use ???. (XXX figure this out.)
  SP `a0000`.
- `&`: Continue execuction via return from interrupt. This allows
  "breakpoints by hand" by inserting `BRK`, `SWI` or similar instructions
  into your code.
- `n`: Single step ("next instruction"). Not yet implemented.
  XXX Maybe give it a count or breakpoint address or something to print a
  trace of several instructions? Also a delay between instructions when
  tracing mulitple instructions.

### Other Commands

- `x`: Exit monitor. Exits in a system-specific way. This may return to the
  caller, execute the system monitor or BASIC, or exit the simulator or
  emulator.

- `$`: set ("$et") monitor global parameters.
  - `p1`: Printing terminal flag. If `1`, avoid overprinting where possible
    by printing CR NL where CR would normally be used. (XXX Also handle
    backspace differently?)

- `?`: Calculate/display a word value. On execution this prints a newline
  followed by `=`, the current remembered value in hex, in decimal, as a
  pair of ASCII characters and as a pair of screen codes on systems with
  text video displays. (As a special case, this command's user typing is
  left on the terminal so she can see what operations she performed.) All
  the following parameters operate immediately, rather than waiting for an
  Enter/Return to signal command execution/termination.
  - `v0000`: set the current remembered value to the given parameter value.
  - Binary operations on remembered value and parameter value, setting the
    remembered value to the result:
    - `+0000`, `p0000`: unsigned add ("plus")
    - `-0000`, `m0000`:  unsigned subtract ("minus")
    - `a0000`: logical AND
    - `o0000`: logical OR
    - `x0000`: logical exclusive OR ("XOR")
    - `<F`: shift left 0 to 15 bits
    - `>F`: arithmetic shift right 0-15 bits
    - XXX Add 8- and 16-bit rotates?
  - `wA`: write the remembered value to user variable _A._

- `/`: Set/display user variables. Parameters `a` through `z` represent
  each user variable. (XXX figure out the details of this. Probably all
  user variables are words, with inapplicable most significant nybbles
  ignored at use. How do we unset/clear a variable to free its storage?)


Command and Parameter Tables
----------------------------

Commands and their parameters (including parameter character, value type
and the location where the value is stored) are stored in and read from a
table that may be replaced by the user. The table is scanned in order from
start to finish and the first matching entry is used.

      Addrs Description
      ──────────────────────────────────────────────────────────
            End of Table
      00    $00 value
      ──────────────────────────────────────────────────────────
            Continue With Another Table
      00    $01 value
      01-02 address of next table
      ──────────────────────────────────────────────────────────
            Command Entry
      00    command character ($02-$FF)
      01-02 address of code to execute command
      03-04 start address of parameter value storage
      ..-.. parameters list (two bytes per parameter)
      ..    $00 value indicating end of entry
      ──────────────────────────────────────────────────────────

Parameter values are stored starting at the address given in $03-$04 above
in the same order as listed in the parameters list, each using only on the
amount of storage required for that parameter.

Each entry in the parameter list is two or four bytes. The first two are
always the parameter and byte specifying the type. "Immediate" parameters
will be followed by two more bytes specifying the address to be called
(JSR) by the parser read and process subsequent input from the user. (The
command character and parameter character will be placed in registers
before the call.) On return from the immediate parameter read routine the
cursor may have moved but the user will still be in parameter input mode
for the current command.

The types are as follows; `Stg` indicates the number of bytes of storage
used in the parameter value storage area.

      Type Stg  Description
      ──────────────────────────────────────────────────────────
      $00   0   immediate parse; address follows in next word
      $FF   2   word value
      $FE   1   byte value
      $FD   1   letter value
      $FE   1   nybble value
      ≤$80 1/0  boolean value (type has any single bit set; see below)

Boolean valued parameters are indicated by a type byte of $80 or less that
has a single bit set, indicating the bit that stores the value in that byte
of storage. (Type bytes ≤$80 that have more than one bit set are invalid.)
Any boolean valued parameter that is preceeded by another boolean valued
parameter will use the same storage location as the preceeding parameter.
(Commands that have more than eight boolean parameters must separate them
into two sets with a non-boolean parameter between them in the list.)

### Reduced RAM Parameter Value Storage

XXX It would be nice to be able to reduce the storage used for parameter
values on very small (~128b RAM) systems.

Possibly we could do this by reserving a small area of RAM for parameter
values for the "current" command, copy defaults from ROM to that after the
command is typed, and then parse the user-supplied parameter values.

It might also make sense to reserve two or more areas particular to groups
of commands such as display commands (`x`, `l`, etc.) and execution
commands (`c`, `g`, `$`). This would allow looping through
deposit-call-examine cycles while maintaining remembered values.


Examples
--------

XXX write me.


Design Notes
------------

Sections above may use † to indicate that their design is discussed further
in this section.

- We use `:` instead of `d` for deposit because this is a destructive
  operation and we don't want it accidentally initiated by someone who
  remembers `d` as "display/dump memory" or "disassemble" from (many) other
  monitors.
- `m` is reserved for a "safe" (non-modifying) command as it's "memory
  dump" in CBM monitors. (It's "modify memory" in others, but in those it
  prints a prompt that makes it very obvious what it's doing.)


To-do
-----

- Consider allowing base 2 and base 10 input. There are several issues we
  need to deal with:
  - Prefixes that shift mode. These probably want to be characters we're
    not using as parameter characters so as to avoid confusion, especially
    in the face of typos (such as forgetting to type the parameter
    character before trying to enter a number).
  - Prefixes could potentially be invisible (Ctrl-B for binary, Ctrl-T for
    base 10?) but that would probably be far too confusing.
  - `%` for binary and `#` for base-10 would probably work well.
  - Since these would produce longer numbers we need to deal with
    write-over in deposits, e.g., `0123: 45 67 89` depositing on the first
    byte could end up as `0123: #1237 89` at or just before terminating
    input for that character, so we need to rewrite the values ahead, as
    well.

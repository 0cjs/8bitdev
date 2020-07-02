Monitor Ideas
=============

XXX digraphs: OS=□, Vs=␣,


Input
-----

Characters are case-insensitive (except in text expressions) and divide
into three groups:
- Numeric literals: `0-9`, `A-F`.
- Variable evaluations, either single-character punctuation symbols that
  are special variables or `$` or `%` to evaluate a user variable.
- Commands: letters `G-Z` and single-character punctuation symbols that are
  not special variables.

### Word Expressions

Entering a _word expression_ at the prompt will set the _cur_ and _end_
variables. A word expression is a word atom optionally followed by `+` or
`-` and another word expression to be added to or subtracted from the
previous value. Any other charcter terminates the word expression and is
parsed as the start of a new word expression or command.

A word atom is one of:
- A numeric literal of four hex digits.
- A numeric literal of less than four hex digits, terminated upon
  encountering any non-hex-digit character.
- A special variable, always a single-character punctuation symbol, that is
  evaluated to its value.
- `$` followed immediately by a user variable letter, evaluated to the
  word value of that user variable.

### Byte Expressions

Some commands take a list of _byte expressions_ which can always be
terminated by a CR and for some commands an alternate termination
character. A list of byte expressions is one of the following, optionally
followed by another list of byte expressions:
- A `"` followed by any characters except `"` or CR; each is evaluated as
  the ASCII value of that character. `"` again terminates the character
  list without terminating the byte expression list.
- A special variable punctuation symbol or `$` followed by a user variable
  letter, which starts parsing as a word expression. When parsing of the
  word expression is complete the result is treated as two bytes in the
  machine's native word order. (See below for an example.)
- A byte expression.

A byte expression is a byte atom optionally followed by `+` or `-` and
another byte expression to be added to or subtracted from the previous
value.

A byte atom is one of:
- A numeric literal of two hex digits.
- A numeric literal of a single hex digit terminated by a space. The space
  does not terminate a list of byte expressions.
- A `%` followed by a user variable letter, evaluating to the LSB of that
  user variable.
- A `&` followed by a user variable letter, evaluating to the contents
  of the address in that variable.

Word expressions embedded in byte expression lists must be treated with
care. E.g., if _cur_ is 2:

    expression          big-endian parse        little-endian parse
    00AA.+100 BBCC      00 AA 01 02 BB CC       00 AA 02 01 BB CC
    00AA.+100BBCC       00 AA 10 0D BC 0C       00 AA 0D 10 BC 0C

### Commands

A command with no arguments is self-terminating; a word expression or
another command may be entered immediately after it. A command with
arguments can always be terminated by a CR; some commands also offer an
alternate argument termination character.


Variables
---------

### User Variables

User variables are letters `A-Z`, and are evaluated by preceeding them with
`$` for their (16-bit) word value or `%` for the (8-bit) value of the LSB.
E.g., if user variable `A`'s value is 0x1234, entering `$A` is the same as
entering `1234`, and entering `%A` is the same as entering `34`.

Note that when evaluated in contexts requring a list of byte values, such
as in `:` entry, a 16-bit value will be split into two bytes in native
endian order. E.g., if `A` is 0x1234, `:$A:` will deposit bytes `12 34` on
an 6800, but bytes `34 12` on a 6502.

XXX `&v` for getting the contents of location in user variable _v_.

### Special Variables

Special variables are punctuation symbols evaluated when they are entered
alone. E.g., if _cur_ is 0x1234, entering `.` is the same as entering
`1234`. Evaluating a special variable may have a side effect.

Configuration:
* `@` _defsize_, the default size of a range; used when variables are set
  by address entry.

Command parameters:
* `*`: _cur_, the starting location for reads from memory.
* `/`: _end_, the end location of reads from memory.
* `;`: _next_, starting deposit location for memory modifcation commands.

Calculations and saved values:
* `,`: _cur_ + _defsize_ (cannot be set)
* `_`: _prev_, previous location; set by address entry.
* `.`: _contents_ (byte), contents of _next_; updated during deposit.
  Convenient to "skip over" values in deposit byte lists. XXX perhaps eval
  as word instead in word list context? Otherwise more of a pain than
  useful at command prompt.

Stack:
* `)`: Stack pointer register value.
* `(`: Word currently at top of stack. (Stack pointer unchanged.)
* `<`: Word popped from stack.
* `>`: Push _cur_ on to stack and evaluate to _cur_. (Usable only in word
  expression parsing mode; in command mode the `>` command, which does the
  same thing, will be interpreted instead.)

Punctuation usage summary (special variables and commands):

      Used   !"#$%& ()*+,-./  :;< >?      _     
     Notes    ¹
    Unused         '             =    [\]^  {|}~

    ¹ Byte data entry only, but using it elsewhere would be confusing.


Commands
--------

Command summary:

    !   Assemble
    #   Set variable
    :   Deposit
    <   Pop from stack
    >   Push _cur_ on stack
    ?   Evaluate expression
    G   JSR ("gosub")
    J   JMP
    L   List disassembly
    M   Move memory
    N   Compare memory ("not-equal")
    O   Fill memory ("overwrite")
    R   Read from device into memory
    S   Examine screen codes
    T   Examine text
    V   Print CRC-16 of current block, and set $V ("verify")
    W   Write memory to device
    X   Examine hex
    Z   User command

CR will always terminate parsing.

Space is a do-nothing comand. It can be useful to terminate parsing (e.g.,
`FF00` is a single address, but `FF 00` is two addresses, 0xFF and 0x00) or
to make things easier to read.

### Setting and Printing Variables

- Address entry: Entering an address instead of a command will set _cur_
  and _next_ to that address, _end_ to that address plus _defsize_, and
  _prev_ to the prevous value of _cur_.
- `#ve` (_wordexpr_): Set variable _v_'s value to the evaluation of word
  expression _e_. _v_ may be a letter indicating a user variable or a
  punctuation symbol indicating a special variable. Spaces are not allowed
  in the expression; the expression is terminated by a CR, space or
  command. (XXX Use `=` instead? `#` as the advantage of being in the same
  place on Selectric and TTY keyboard layouts.)
- `?` (_wordlist_): Evaluate a list of word expressions and print each
  result separated by a space.

### Memory Reads

These read from _cur_ up to (but not including) _end_. When _end_ is not
_cur_ + _defsize_, it's idiomatic to set _end_ explictly after setting
_cur_ with, e.g., `80 #/100 X` or `80#/100X`.

- `X`: Examine as hexadecimal. May also include text output on the right if
  the screen is wide enough.
- `T`: Examine as text, displaying non-printable chars in a
  system-dependent way.
- `S`: Examine screen (frame buffer) codes.
- `L`: List disassembly; froom _cur_ print _defsize_ / ??? bytes of
  instructions.
- `N`: Compare memory. (Menmonic: not-equal?)
- `W` (_bytelist_): Write memory from _cur_ to _end_-1 to currently
  selected device. Argument is name to write (may be blank), terminated by
  CR; typically given in `"name"` form.
- `V`: Calculate CRC-16 of memory from _cur_ to _end_-1, printing it and
  setting `$v` to that value.

### Memory Writes

- `:` (_bytelist_): Deposit data starting at _next_ and leaving _next_ at
  the last address deposited + 1. The following characters are the data to
  deposit; see _byte list_ above for details. A byte value in the list that
  is just the special variable `.`, meaning the contents of the location
  about to be deposited, is guaranteed not to write to that location at
  all, rather than rewriting the existing value. As well as CR, the byte
  list may additionally be terminated by `:`; any other invalid character
  will terminate entry and generate an error.
- ???: Fill data.
- `!`: Assemble following args as instruction and deposit at _next_, then
  set _next_ to the last location deposited + 1.
- `M`:  Move memory.
- `>`: Push _cur_ on to the stack. Equivalant to `#>*` except it does not
  generate a value. (Typically used with `<` and `(` special variables.)
- `<`: Pop a word from the stack and set _cur_ and _next_ to that word.
  (Not actually a real command; it's just evaluating the special variable
  and interpreting the word as normal.)
- `RD` (_bytelist_): "Read Default" from current device into memory
  starting at the default load location saved in the file, if present. If a
  default load location is not present, generate an error. The file
  determines the data length.
- `RN` (_bytelist_): "Read to _Next_" from current device into memory
  starting at _next_. The file determines the data length.
- `RS` (_bytelist_): "Read Specified Size" from the current device into
  memory starting at _next_ up to (but not including) _end_, or until file
  data runs out.

All `R` commands leave _cur_ and _end_ pointing to the start of the data
read and one past the end of the data read, respectively. _end_ may be
reset to the current block size by entering _cur_, `*`.

### Registers and Execution

- `G`: Gosub (`JSR`) to _cur_.
- `J`: Jump (`JMP`) to _cur_.

XXX how to display and set registers?
- Maybe use vars for it (making some vars 8-bit):
  - common: `$p` saved program counter, `)` stack register, `$s` status
    register (flags).
  - 6502: `$a $x $y`
  - 6800: `$a $b $x`
  - 8080: `$a`, `$b`=BC, `$d`=DE, `$h`=HL `$m`=\[HL] (kinda special)
  - Set LSB of 16-bit reg with `#h$h-%h+FF`?
- Special var prefix, but running out of chars and how to set?
- Ctrl-R:
  - displays as special char, prints regs/flags in nice format
  - inserts `? $a $x $y $s $p` into input buffer
  - how to display saved program counter?

### Misc. Commands

- `Zv`: Execute user command at address in user variable _v_. The user code
  may continue parsing if necessary. Need to define the API for this.


### Todo XXX

- Radix conversions.
- Display and set registers.
- Step/trace commands
- Size multiplier for commands so `X` etc. doesn't need args? How about we
  have _end_ as well, set automatically to _cur_ + _defsize_ unless changed
  separately?
- Ctrl-commands available?


Devices and Reading/Writing
---------------------------

The `R` and `W` commands make use of a "currently selected device." These
are handled by routines with a common interface (see below).
- `W`: _cur_, _end_ for the memory area to read.
- `RD`: Contents of file determine start and length.
- `RN`: Write memory starting at _next_, file contents determine length.
- `RS`: _next_, _end_ for the memory area to write.
  - XXX but review this; `7000 #/77FF RD` is an ideomatic way to read 2 KB,
    but what if someone inserts a bit before reading,  `7000 #/7FFF :1234
    ABCD: RD` would read only 2KB - 4 bytes immediately after the deposited
    data. But that does seem sensible.

The currently selected device is determined by a word in memory. (Should we
have two words, for separate read/write?) If it's a small value, e.g. $0000
or $0002, it will be used as an index into a table of I/O routines supplied
by the monitor. If it's larger it will be used as a pointer to a
user-supplied I/O routine. (Possibly the address pointed to should be
checked for a valid starting byte?)

The interface could be:
- X points to the command argument _bytelist_.
- Start/end address are taken from the usual variables, where necessary.
- Simplest thing: enter with a flag clear or set to indicate read or write.
  But how to handle "read full file" vs. "read only this much"?
- Magic cookie (to let monitor error-check pointers) followed by entry
  offsets for start of read/write/whatever routines? (Could be used to make
  driver supply separate `RD`, `RN`, `RS`.)
- Maybe have an APIs count in the magic cookie so that additional ones
  could be added to display a directory or whatever.


Use Cases / Sample Session
--------------------------

An initial `.` on a line is the prompt. These assume 40-column output
format; 32 column format would drop text shown to the right of hex dumps
and 80 column format would show more data per line. Where inverse or
similar chars are available, text dumps could use that to show control
characters and/or chars with the high bit set. Screen codes shown here are
from the CBM graphics set, with all inverse chars shown as `█`.

    ---------1---------2---------3---------4

Start with _cur_ = _next_ = 0x0400.

Set _defsize_ to 16 bytes. Examine _defsize_ bytes at _cur_ as hex, then
text, then screen codes (CBM lower-case set, in this case).

    .#@10
    .xts
    0400: 0001 0203 0405 0607 ........
    0408: 2021 3031 4041 6061  !01@A`a
    0400" .... ....  !01 @A`a
    0400' @ABC DEFG  !01 ━♣▒▌

Examine _defsize_ bytes starting at _cur_+_defsize_ as hex.
(_cur_ = _next_ = 0x410.)

    .,x
    0410: 00FF 00FF 00FF 00FF ........
    0418: 00FF 00FF 00FF 00FF ........

Examine _defsize_ bytes starting at _cur_, replace bytes starting at _next_,
and examine result. (_next_ = 0x041A.)

    .x :0d0a: "Hi there" :d a: x
    0410: 00FF 00FF 00FF 00FF ........
    0418: 00FF 00FF 00FF 00FF ........
    0410: 0D0A 4869 2074 6865 ..Hi the
    0418: 7265 00FF 00FF 00FF re......

Save _cur_ on stack. Set _cur_ and _next_ to 0x41A and deposit, maintaining
current values for some bytes. Restore _cur_ and _next_ from stack and
examine.

    .> 41a:21 . . 11 . 22:<x
    0410: 0D0A 4869 2074 6865 ..Hi the
    0418: 7265 21FF 0011 0022 re!.....

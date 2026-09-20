CLIC Console/Terminal: Keyboard and Display
===========================================

CLIC always operates in mixed case mode, with standard library names and
conventionally most everything else in lower case, but occasional use of
upper case in symbols as well. It uses the full printable ASCII character
set and requires that the input device driver be capable of generating all
characters.

Certain systems do not provide for input and/or output of all ASCII
characters and will usually need custom I/O routines (replacing the
standard BIOS routines) to compensate for this.


Keyboard Input
--------------

### Ctrl (Control) Key

Keyboards without a Ctrl key will somehow need to define a way to indicate
control characters. Note that on keyboards without ESC, that character can
be entered as Ctrl+`[`.

For scanned keyboards this is typically done with a new scanner that
redefines one of the keys as Ctrl. These include:
* __PET 2001 Chiclet:__ OFF/RVS (right of the LShift key).
* __PET Graphics Keyboard:__ OFF/RVS (left of the `Q` key)
* __PET Business:__  ESC left of SHIFT LOCK, or OFF/RVS left of LShift.
* __TRS-80 Model I/III:__ `↓` (down arrow) key left of `A`.
* __Sharp MZ-80K:__ CLR/HOME right of LShift.
* __Sharp MZ-80C:__ INST/DEL left of `A`.
* __Sinclair ZX80/ZX81:__ TBD.
* __TRS-80 Color Computer 1/2:__ `↓` (down arrow) key left of `A`.
* __Dragon 32/64:__ `↓` (down arrow) key left of `A`.
* __Jupiter Ace:__ TBD.
* __Sinclair Spectrum 16K/48K/+:__ TBD.

Early systems known to have a Ctrl key include:
- Teletype ASR-33. Most ASCII "professional" computer terminals.
- SWTPC CT-1024 terminal (TV Typewriter).
- Apple II and clones. Atari 400/800. Acorn Atom, BBC Micro, Electron.
- TI-99/4A (but probably not the /4).
- Oric-1 and Atmos.
- VIC-20 and later Commodore systems.
- TRS-80 MC-10 Micro Color Computer. Matra Alice.

Systems that _typically_ have a Ctrl key, but where they may not because
the keyboard was often user-supplied.
- TV Typewriter. Apple 1.

### Sending Full ASCII Charset / Prefix Keys

Keyboards not capable of sending the full ASCII character set ($00-$7F,
including all non-printing characters) must define a prefix key that will
be used to send otherwise inaccessible characters. Ctrl-A is suggested.
(Keyboards are not expected to be able to send non-ASCII codes in the range
$80-$FF.)

Keyboard letters should be read as lower case when an unmodified letter key
is pressed. Keyboards without working Shift keys should use the prefix key
followed by a letter to send that letter in upper case. E.g., the 'X' key
sends `x` and Ctrl-A followed by the 'X' key sends `X`. (Use prefix-prefix,
e.g., Ctrl-A Ctrl-A to send the prefix key itself.)

Upper case/kana keyboards may change the kana key to a shift key.

Many keyboards do not have the full set of ASCII punctuation characters.
Missing ones are usually not in the number/punctuation sticks ($20-2F
and $30-$3F) but those in the upper and lower case letter sticks:

    $40 @   $5B [   $5C \   $5D ]   $5E ^   $5F _       (upper case stick)
    $60 `   $7B {   $7C |   $7D }   $7E ~   $7F DEL     (lower case stick)

These should be entered with the prefix character plus another appropriate
punctuation character, or digraph where necessary.

Here's a list of the punctuation chars available on some popular keyboards
and suggested second chars after the prefix to produce the missing ones. In
cases where the suggested second char is shifted, the shift is generally
optional (e.g. you can use prefix-`,` instead of prefix-`<` to get `[` on
the Apple II).

     @[\]^_`{|}~ │ Full set                       │ @[\]^_`{|}~ DEL
    ─────────────┼────────────────────────────────┼────────────────
      [ ]  `{ }~ │ SWTPC CT-1024 (TV Typewriter)  │
     @[\]↑←`     │ PET 2001 (chiclet/graphics)    │
     @  ]^       │ Apple II¹                      │  </>&-'(:)!  @
                 │                                │  ,/.6-78:91  2 (unshifted)
     @           │ TRS-80 Model I                 │  </>&-'(:)!  @

Notes:
- ¹ Apple II produces `]` on Shift-M, but this is unmarked on the keyboard.


Display Output
--------------

Note that input is _not_ symmetric with output; typing in the sequences
displayed below does not re-create the internal representations that
generated them, though entering them via a screen editor where text is left
unchanged may do so.

### Upper-case-only Displays

For displays not capable of displaying lower case, lower case characters
should be displayed as upper case and upper case characters should be
specially marked.
- On video displays we suggest reverse video or bold video, when available.
- On "glass TTYs" and printing terminals we suggest prefixing capital
  letters with a `\` (backslash). That character itself will also need to
  be prefixed in this way as `\\`. (This follows the traditional Unix `stty
  olcuc xcase` output convention.)

### Non-standard and Missing Glyphs

Some systems display non-standard glyphs for standard ASCII characters.
E.g. (some glyphs are approximations, `␣` indicates missing glyphs):

                        HEX │ 5B 5C 5D 5E 5F 60 7B 7C 7D 7E 7F
                      ASCII │  [  \  ]  ^  _  `  {  |  }  ~ DEL
    ────────────────────────┼───────────────────────────────────────────
            TRS-80 Model I¹ │  ↑  ↓  ←  →     ␣              ±
                  Apple II  │                 ␣  ␣  ␣  ␣  ␣  ␣
     PETSCII (PET/VIC/C64)² │     £     ↑  ←  ━  ╋  ░  ┃  ▒  ▧

Notes:
- ¹ All but the latest (mostly overseas) TRS-80 Model Is needed a VRAM
    upgrade to display lower case, or a modification that swapped the
    graphics chars for lower case. The Model III supported lower case
    display from the start and also standard ASCII for all characters.
- ² PETSCII also needs further conversion to swap upper/lower case etc.
    unless the intent is to run in native PETSCII.

Use the best substitutes you can find for custom output routines. Where
characters are entirely missing, here are the suggested digraph
substitutes, which are the same as traditional Unix `stty xcase` output:

         ASCII │  `  {  |  }  ~
    ───────────┼────────────────
    Substitute │ \' \( \! \) \^

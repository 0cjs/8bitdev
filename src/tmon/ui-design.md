tmon UI Design Notes
====================

### Keyboard Layout and Command Assignments

The most important factor for chosing commands is key location (on both
western and Japanese keyboards). The most frequently used commands are as
near the home row as possible, with:
- Examination commands on the left (thus `r`egister examine).
  - But there are a few exceptions to this: `q`uit, `t`ransfer.
- Modification and execution commands on the right (thus `;` to modify
  registers, `k` to call a subroutine).

Here is the current diagram of the key layout with unused keys marked
with broken vertical bars on each side, `┊x┊`.

    ┊TAB┊ q  w  e  r  t  y ┊u┊ i  o  p ┊[┊┊]┊
           a  s  d  f ┊g┊┊h┊ j  k  l  ;  ' ┊"┊
           ┊z┊ x ┊c┊ v  b ┊n┊ m  ,  .  /

Also, searching for `  [qwertasdfgzxcvb]  ` (note the two spaces on either
side) in the [README](./README.md) will highlight the commands on the left
side of the keyboard.

The next factor is mnemonic value, though this is often stretched somewhat
(e.g. `y`ank to memory from storage). Due to the layout differences between
Western and Japanese keyboards, this occasionally causes us to give up good
key location on the Japanese keyboards in favour of good key location on
Western keyboards and mnemonic value (e.g `'` for ASCII deposit; on the
unshifted home row on Western keyboards but Shift-2 on Japanese keyboards).

A few commands are chosen because they're the start character for data
formats, these being `:` for Intel hex records and `S` for Motorola hex
records. (We do not support `;`  for MOS hex records because that key is
just too useful for the register modification command to give up.) Possibly
we could work around this with an entry mode (perhaps a subcommand of
`y`ank to memory from storage).

### Display

The display is designed to be as compact as reasonably possible so that the
maximum amount of information is seen on small (typically 24 line)
microcomputer displays before it scrolls off.

The most common technique used for this is to overwrite the prompt line and
user input with the first line of output, where reasonsable. Thus, e.g.,
the `e`xamine memory with parameters first line of output will overwrite
the parameters the user typed in because the current parameters are fairly
obvious from the display itself.

The main exceptions are:
- Commands that execute user code (`i`, `j`, `k`) because this makes it
  more clear where output from the user code starts.
- Commands that execute user code (`i`, `j`, `k`) because this makes it
  more clear where output from the user code starts.
- Deposit commands, so that the data deposited remains on the screen.
- `m`emory copy, so that the parameters remain on the screen.

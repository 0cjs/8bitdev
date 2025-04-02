tmon TODO List
==============

Bug Fixes
---------


General TODO
------------

- See `src/i8080/tmon.i80` head comments for a list of commands
  yet to be implmented.

- Add ability to use a clear-to-EOL function if the terminal supports it.

- Add a byte/word switch mode in word/byte deposit mode. Perhaps Ctrl-D
  ("digits change") to match the Ctrl-D in ASCII entry mode?

- During `,` deposit parameter input, we should allow `.`/`>`/`'` to
  immediately start deposit, rather than making the user press Return
  first. This is not only faster but also avoids using an extra line.

  However, implementing this without using too much code is a bit tricky.
  Perhaps we can designate one of the temporary bytes as an "auto-return"
  byte, storing 0 in it at the start, and if that address is matched in the
  ptab, immediately store the char that triggered it in there and return,
  letting the caller check to see if it's non-zero and know the character
  that triggered it. (Then print CR, 19 spaces to clear and execute the
  desired command; we don't want to do more because e.g. Epson HC-20 has
  only a 20-chars/line LCD display.)

- Bank switching: Add `m`emory bank (source) and `n`ext memory bank
  (target) parameters to read/write/copy commands. Probably we want to use
  $FF as the "use current bank" parameter, as in many systems (e.g. MSX)
  that will not interfere with banks given specific numbers starting at 0.
  The Sharp MZ-700 is probably a good platform to start on.

  It's not clear how we might determine the user memory bank configuration
  and restore it on monitor exit on systems that do not provide the ability
  to read configuration registers. Perhaps we could checksum the memory
  area on entry and, on exit, switch through the banks to find one that
  matches that checksum. This wouldn't work if we are changing data in the
  banks, though perhaps we could re-checksum after a change in that area.

  Systems such as MSX introduce an extra complication: we can do the
  primary slots (0–3) for all four pages in one byte, but then $FF refers
  to a specific mapping (bank 3 for each of the four pages) and cannot be
  used as "current mapping." Even extending this to 16 bits doesn't help if
  we introduce expansion slot mappings (0–3), as all 16-bit values are
  valid for the combination of primary and expansion slots. (Plus, while
  we can read the primary slot mappings, we cannot read the expansion
  slot mappings.)


Platform-specific TODO
----------------------

### Kyocera-85

- Get it running on PC-8201, or TRS-80 Model 100.

### CP/M

- Initial version, `TMONLVT.COM`, loads like a normal CP/M program into the
  TPA at $100.
- A better version would work like DDT, relocating itself to the top of
  memory. Possibly this could be set up as a (temporary?) CCP replacement.
- Once that's set up, device load/save can set up an FCB and load to/save
  from the TPA.

### PC-8001 / PC-8001mkII

- Add CMT load/save.


Not TODO
--------

- We considered adding Ctrl-J in input mode (hex or ASCII) to start a new
  line displaying the current address and then continuing with input, in
  case one is getting lost in long streams of input. However, it's only a
  single extra keystroke to hit Enter followed by the deposit command
  again. This is not _quite_ as easy as Ctrl-J, since you need to remember
  which deposit command you were using, but it's still not worth the extra
  code space, and this is somewhat dificult to implement.

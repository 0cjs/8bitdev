tmon TODO List
==============

Bug Fixes
---------


General TODO
------------

- While entering params for `e` command, we should be able to type `d` and
  have it immediately do a dump, rather than having to Enter then do `d` on
  a new line to get the dump. (Saves both typing and a display line on
  screen.)

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

- Burn into 8K expansion ROM ($6000-$7FFF), with the pre-init setting up
  extra BASIC command to enter tmon.
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

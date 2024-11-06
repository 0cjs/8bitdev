tmon TODO List
==============

- Print an extra space between every group of 8 hex digits being examined,
  so that it's easier to read in width=$10 mode.

- Get rid of `t0w` and `t2w` and have users of a temporary word just
  use `t0b` and `t1b` instead. This will make it easier to check (via
  searches) what temporary storage is being used by various routines.

- `intentry` should probably print the registers on entry. Not clear if we
  also should print something to indicate this is the result of `intentry`
  rather than `r`.

- Ctrl-N should probably advance without changing in hex input mode, too.

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

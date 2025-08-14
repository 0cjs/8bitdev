This `exe/` subdirectory contains the "top-level" source for executable
programs for various platforms.

- `a1/`: Apple 1. Typically loaded by generating WozMon data deposit lines
  with `bin/wozmon-deposit` or using `bin/a1term` which generates those
  lines and sends them to the serial port.
- `a2/`: Apple II. Typically loaded by using `bin/p2a2bin` to generate
  a DOS 3.3 disk image containing a file (type `B`) with the object code.
  The `a2exebuild()` function in `Test` does this.

This directory also has a `hello.data` file that can be used to test for
dropped characters on serial connections. `t8t … send -f cr exe/hello.data`
should show all the columns lining up nicely on a 80-column terminal; if it
doesn't, characters are being dropped on the connection. (Typically this is
fixed with `--char-delay 1` or a larger number.)

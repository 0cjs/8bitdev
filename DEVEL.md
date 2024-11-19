8bitdev Development Notes
=========================

Packages needed for old Python builds of third party software:

    sudo apt install build-essential \
      libsdl2-dev libcurl4-openssl-dev libsdl-image1.2-dev libsdl1.2-dev \
      libzip-dev liblz4-dev imagemagick

To-do List
----------

#### Bugs

- Once the `dw` being wrong-endian for big-endian machines bug is fixed
  (still present in ASL build 280), add `N dup XXXX` test for `dw`.
- We should probably be checking the assembler version in `std.CPU` files
  because our code makes assumptions about various newer features being
  available. (Possibly t8dev should be doing this too.)

#### Cleanup

- scr/tmc68/biocode: use `ds prchar-$` (current PC) to org routine locations
- Make a better `repr()`/`str()` for `testmc.generic.Machine` so that
  `assert R(...) = m.regs` looks nicer (and maybe provides useful info).
- testmc.generic.machine.Machine.load_memimage() currently sets the
  PC to `None` if there's no entrypoint in the file it's loading. It
  should probably instead set the PC to the reset vector, or the first
  address loaded, or something like that.

#### Build/Test System Fixes

- extract src/mc68/{hello,cjsmon} loadbios() to test framework
- remove more `  cpu 6502` from files and put in unit test framework?
- Rewrite Test in Python and replace UNIT_TESTING symbol per comments.

#### Features

- Add the `testmc.generic.IOMem` interface to `testmc.mos65`.
- Add "hexadecimal integers" to framework with `__repr__()`s that
  print as `$EA` or `$FFFF`. Construct perhaps with `A(0xFFFF)`
  (address) and `B(0xFF)` (byte)?
- "Omniscient debugging"; dump initial memory and symbol table to a
  file, followed by a trace of full execution (instruction, resulting
  register values and the memory change for each step) of a call.
  Probably also want a tool that can dump arbitrary memory at any step.

#### Third-party Tool Support

- Figure out a convenient but quiet way to somehow inform the user of
  which tools he's using, particularly system-supplied vs. .build/.
- Allow configuring tools as "dontuse," w/no build or install, and
  code that needs the tools simply not being built.

#### Third-party Tools to Consider Using

- Use [omni8bit](https://github.com/robmcmullen/omni8bit) (`pip
  install omni8bit`) front end for emulator startup/run here?
- Look into [Omnivore](https://github.com/robmcmullen/omnivore) (`pip
  install omnivore`), a visual tool providing tools and front-ends for
  other tools: various emulators w/debuggers; binary editor;
  disassemblers; ATasm 6502 cross-assembler; graphics and map editors.
- [CLK] emulator, which covers a dozen different systems we use.

[CLK]: https://github.com/TomHarte/CLK


Other Notes
-----------

#### pytest-xdist performance

8bitdev, t8dev and r8format together have some 2500 unit tests virtually
all over which are extremely short. On cjs's Ryzen 7 7735HS (mini-desktop),
workers (`-n#`) vs. performance is as follows. `0` indicates pytest-xdist
not used (`-n0`), and the figures are wall clock and test run time averaged
over three runs.

        Workers     Wall        Test
            4        4.3         2.0
            8        4.5         2.3
           16        4.8         2.6
            2        4.8         2.6
            0        6.1         3.9
            1        6.7         4.5

Thus in `pyproject.toml` we set `-n4` as the default. This adds about 0.2
seconds overhead to pytest  to the shortest possible run of a single test
using the 6502 simulator, but given that there's over 2s over overhead,
this moves the shortest case from 2.2s → 2.4s, and with more tests being
run very quickly the cost of starting workers starts to pay off.

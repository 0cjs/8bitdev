To-do List
==========

#### Cleanup

- Make a better `repr()`/`str()` for `testmc.generic.Machine` so that
  `assert R(...) = m.regs` looks nicer (and maybe provides useful info).
- testmc.generic.machine.Machine.load_memimage() currently sets the
  PC to `None` if there's no entrypoint in the file it's loading. It
  should probably instead set the PC to the reset vector, or the first
  address loaded, or something like that.

#### Features

- Add the `testmc.generic.IOMem` interface to `testmc.m6502`.
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
  toher tools: various emulators w/debuggers; binary editor;
  disassemblers; ATasm 6502 cross-assembler; graphics and map editors.

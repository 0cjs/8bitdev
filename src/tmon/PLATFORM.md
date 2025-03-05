tmon Platform Notes
===================

8080
----


Z80
---

tmon runs on Z80 platforms, but does not support any Z80-specific features.
In particular it doesn't save (or touch in any way) the Z80-specific
registers (IX, IY) or the alternate register set (A', B', etc.).

### NEC PC-8001 Series

A single PC-8001 build is part of PC-8001 expansion ROM #1. (Source code:
[`exe/nec/pc8001/exprom1.i80`]; release in the `pc8001` subdirectory of the
release archive.) This runs only on the original PC-8001 (tested) and
probably an 8001mkII in N-BASIC mode (but not N₈₀-BASIC as of yet).

- As with all control characters, backspace prints a `␈`; as normal for
  tmon this always an invalid character.
- tmon is invoked with `MON`.
- The `q`uit command takes a parameter (default 0):
  - `t0` or any other value not below will return to BASIC.
  - `t1` will call the original monitor; Ctrl-B there will return to tmon
    as that's less invasive (returning to BASIC probably resets all sorts
    of variables) and generally more convenient.
- The `user_rst30` vector is set to `intentry` so that `RST $30` will enter
  tmon. (This can be used to set breakpoints in code in RAM.)

See the [exprom1 README][exprom1-rm] for more information on other contents
of that ROM.

### CP/M

The `TMONLVT.COM` version resides in "low" memory, starting at $0100
at the start of the TPA. This means that it can't be used to examine
or debug other CP/M programs, but it's still useful for experimentation
and getting a feel for how tmon works. It's also hard-coded for a VT100
terminal, which affects the ASCII display when examining memory. (It
uses inverse for high-bit set, and underlines control characters.)

Both these issues will be fixed in a future release of CP/M tmon better
suited for use in that environment. In the short term there will be an easy
patch method to change the terminal codes, and in the long term it will
relocate itself into high memory so that it can be used like `DDT` (or
perhaps even as a sort of weird CCP replacement).

Bugs:
- There appears to be an issue with the `K` (call) command under CP/M;
  calling a `ret` does not return to the monitor and it seems that the
  return address to the monitor is not being pushed on the user stack.


Other CPUs
----------

Currently the 8080 version of tmon is the only CPU available. (This runs
on 8085 and Z80 as well, but supports no 8085/Z80-specific features.)

Support is planned for 6800, 6502, and perhaps 6809 and 68000.



<!-------------------------------------------------------------------->
[`exe/nec/pc8001/exprom1.i80`]: https://github.com/0cjs/8bitdev/blob/main/exe/nec/pc8001/exprom1.i80
[exprom1-rm]: https://github.com/0cjs/8bitdev/blob/main/exe/nec/pc8001/README.md

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

See the [exprom1 README][exprom1-rm] for more information on other contents
of that ROM.


Other CPUs
----------

Currently the 8080 version of tmon is the only CPU available. (This runs
on 8085 and Z80 as well, but supports no 8085/Z80-specific features.)

Support is planned for 6800, 6502, and perhaps 6809 and 68000.



<!-------------------------------------------------------------------->
[`exe/nec/pc8001/exprom1.i80`]: https://github.com/0cjs/8bitdev/blob/main/exe/nec/pc8001/exprom1.i80
[exprom1-rm]: https://github.com/0cjs/8bitdev/blob/main/exe/nec/pc8001/README.md

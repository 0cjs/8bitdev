NEC PC-8001 Binaries
====================


8bitdev Expansion ROM #1
------------------------

`exprom1.bin` is a ROM image to be burned into an 8K 2764 EPROM for
the expansion ROM socket in the PC-8001 and PC-8001mkII. On startup
it will hook the Disk BASIC `CMD` command to provide the following
additional functionality.

- All Disk BASIC commands enter the monitor for debugging purposes
  (see below).
- `CMD HELP`: Print the available parameters that can be used with `CMD`.
- `CMD HELLO`: A "Hello, world" program that demonstrates keyboard input
  and screen output.
- `CMD TMON`: The [TMON] "Tolerable Monitor."

`HELLO` prints a prompt and echos whatever you type after it. Pressing
RETURN twice or Ctrl-C will return to BASIC.

`TMON` is generally working, but has some issues. In particular, it's using
the top of the BASIC memory space to store its workspace, and this is
usually overwritten when you return to BASIC, so any changes you make to
the default command parameters are not saved. (If you have any thoughts
on a better place to put this, or way to preserve this, I'm all ears.)

### Disk BASIC Command Debugging

All Disk BASIC commands that normally return a `Disk BASIC feature` error
now enter the monitor via the `intentry` point, which saves all registers
and sets the next PC to the return address on the stack. This is useful for
working out what the system sets up and gives to the command, and you can
execute any code you like to simulate an actual command routine. The `i`
command will return back to the BASIC code that called the statement
vector.

### Execution in an Emulator

[`8bitdev`] builds and makes available the CSCP project Japanese
microcomputer emulators. To build and use this ROM in the `pc8001`
emulator, use the following command:

    ./Test -E .build/obj/exe/nec/pc8001/exprom1.bin src/i8080/

(The `src/i8080/` at the end just limits the unit tests to those under
that directory, which speeds startup.)



<!-------------------------------------------------------------------->
[tmon]: https://github.com/0cjs/8bitdev/tree/main/src/tmon
[`8bitdev`]: https://github.com/0cjs/8bitdev/

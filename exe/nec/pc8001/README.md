NEC PC-8001 Binaries
====================


8bitdev Expansion ROM #1
------------------------

`exprom1.bin` is a ROM image to be burned into an 8K 2764 EPROM for
the expansion ROM socket in the PC-8001 and PC-8001mkII. On startup
it will hook the Disk BASIC `CMD` command to provide the following
additional functionality.

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


[tmon]: https://github.com/0cjs/8bitdev/tree/main/src/tmon

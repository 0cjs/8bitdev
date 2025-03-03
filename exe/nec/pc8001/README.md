NEC PC-8001 Binaries
====================


8bitdev Expansion ROM #1
------------------------

`exprom1.bin` is a ROM image to be burned into an 8K 2364 ROM for the
expansion ROM socket in the PC-8001 and PC-8001mkII. On startup it will
take over the `MON` command and hook the Disk BASIC `CMD` command to
provide the following additional functionality.

- The `MON` command enters [tmon]. To enter the original system monitor,
  enter tmon and type `qt1`. More details are in the tmon platform
  information file at the link above.
- `CMD HELP`: Print the available parameters that can be used with `CMD`.
- `CMD HELLO`: A "Hello, world" program that demonstrates keyboard input
  and screen output. This prints a prompt and echos whatever you type after
  it. Pressing RETURN twice or Ctrl-C will return to BASIC.
- `CMD TMON`: Alternate way of entering tmon.
- All other Disk BASIC commands enter the monitor for debugging purposes
  (see below).

#### Disk BASIC Command Debugging

All Disk BASIC commands that normally return a `Disk BASIC feature` error
now enter the monitor via the `intentry` point, which saves all registers
and sets the next PC to the return address on the stack. This is useful for
working out what the system sets up and gives to the command, and you can
execute any code you like to simulate an actual command routine. The `i`
command will return back to the BASIC code that called the statement
vector.

### ROM/EPROM Hardware

It's unlikely that you will be able to contract to have actual 2364 ROMs
burned, so most likely you will want to use an adapter board that does the
pinout conversion to let you use a 2764 (or larger) EPROM. There are [many
of these][gh-2364-adapter]; the one we like is the [RetroStack 2332/2364
ROM Adapter][gh-rs-23xx].

An issue you're likely to encounter with any adapter is that the ROM
sockets on the PC-8001 and PC-8001mkII have very narrow pin holes, and the
machine pins usually used on adapters will not fit. There are special pins
one can buy that match the dimensions of the pins on actual ICs, but we've
not seen a source for these in some time. There is also, espeically on the
mkII, little space above the ROM socket for a stack of adapter board,
socket and EPROM.

One option is to use a [DIP IDC connector][dk-dipidc] to bring the socket
out via ribbon cable to another location. We're looking at a project to
bring it out the back of the machine (the ribbon cable coming out through
the printer connector slot, which is taller than the expansion connector
slot) to an external adapter board with a ZIF connector, allowing easy
changes to the EPROM without opening the machine. (More will be reported
here as the project proceeds.)

### Execution in an Emulator

[`8bitdev`] builds and makes available the CSCP project Japanese
microcomputer emulators. To build and use this ROM in the `pc8001`
emulator, use the following command:

    ./Test -E .build/obj/exe/nec/pc8001/exprom1.bin src/i8080/

(The `src/i8080/` at the end just limits the unit tests to those under
that directory, which speeds startup.)



<!-------------------------------------------------------------------->
[`8bitdev`]: https://github.com/0cjs/8bitdev/
[tmon]: https://github.com/0cjs/8bitdev/tree/main/src/tmon

<!-- ROM/EPROM Hardware -->
[dk-dipidc]: https://www.digikey.jp/en/products/filter/rectangular-connectors/board-in-direct-wire-to-board/317?s=N4IgjCBcoBw1oDGUBmBDANgZwKYBoQB7KAbXAFYwBOAJipAF0CAHAFyhAGVWAnASwB2AcxABfAuQBsAZgQhkkdNnxFSIGnEnwmINh279hY0aKA
[gh-2364-adapter]: https://github.com/search?q=+2364+adapter&ref=opensearch&type=repositories
[gh-rs-23xx]: https://github.com/RetroStack/2332_2364-ROM_Adapter

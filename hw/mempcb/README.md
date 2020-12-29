RC6502 / 50-pin Bus Reconfigurable Memory Board
===============================================

Overview
--------

This board is designed for prototyping and experimenting with JEDEC DIP-24,
DIP-28 and DIP-32 RAM, EEPROM and EPROM/PROM memory devices on the [RC6502
bus] and any system with an expansion bus connector taking a 50-pin ribbon
cable (e.g., the National/Panasonic JR-200 or some MSX computers).

The general idea is that it makes for you the common connections that will
be the same with any board: power/ground, data lines and lower address
lines. For the rest you can wire-wrap between .1" header pins bringing out
the signals from the bus connectors and sockets.

Design
------

It's a 100 mm × 100 mm board with the following:
- 39-pin RC6502 bus connector (right-angle .1" header) on one edge.
- 2×25 pin .1" header for use with a 50-pin IDC connector, for connection
  to microcomputer expansion bus connectors.
- DIP-32 footprint for a RAM socket. There is sufficient space around it to
  use a ZIF socket, though the release arm will stick out over the edge of
  the board.
- Two DIP-16 sockets for address space decode and other logic.
- Four each of Vcc, pull-up, pull-down and GND sources. (Pull-ups and
  pull-downs connect to Vcc and GND, respectively, through your choice of
  resistor value. 1 kΩ would be typical.
- A jumper to connect or disconnect the board to RC6502 bus Vcc.
- Two pad pairs at 2.50 mm pitch for connecting JST XH or similar
  connectors for supplying power to or taking power from the board.

The hardwired connections are:
- GND to the standard pins on all three sockets: pin 16 on the DIP-32 and
  pin 8 on each DIP-16.
- Vcc to the standard pins on all three sockets: pin 32 on the DIP-32 and
  pin 16 on each DIP-16. (pins 16/32 on the DIP-32, and pins 8/
- Data bus D0-D7 to the standard JEDEC pins on the DIP-32.
- Address bus A0-A10 to the standard JEDEC pins on the DIP-32.

All bus connector and IC pin signals are available on .1" headers next to
the connector/socket. These are intended to be used for wire-wrap
connections appropriate to the configuration and purpose of the board. The
connections to be made are:
- Vcc, address and control pins on the DIP-32 appropriate to the particular
  memory chip you're using. (DIP-24, DIP-28 or DIP-32, and SRAM/EEPROM or
  EPROM/PROM/ROM pin assignments.)
- Logic pins on the DIP-16s appropriate to their decoding and other
  functions. Typically a 74'138 will be used for address decoding and a
  gate package (74'00 quad NAND, 74'32 quad OR, etc.) for additional
  processing such as qualification of select and read/write lines.
- Logic and additional address pins from the RC6502 bus connector.
- All pins needed from the 2×25 microcomputer bus connector. This is left
  entirely unwired since there is no common standard for any signals on
  these expansion bus connectors.


TODO
----

- Fix page size to be A4 instead of US-Letter?

- ssjjnn mentioned that the grid seems to be offset for him. Go back and
  figure out where we really want the grid origin to be. (Currently upper
  left of page?

- The two component-side traces to bring power across to the left logic
  socket and the memory socket break up the ground plane on top. There are
  two possible solutions to this, though both still require vias between
  top and bottom layer. (But then, so do all the components!)
  - Replace these with jumper wires. These would be like a third layer on
    the board, on the opposite side of the ground plane from the solder
    side of the board. However, jumpers cannot go under sockets because ZIF
    sockets are flat to the board and even standard sockets may not have
    enough clear area inside for a jumper, even if soldered after the
    socket is soldered.
  - Run a power trace on the component side around the edges of the board
    (excepting the RC6502 bus edge). All components will reside inside the
    power trace, and so ground plane will be maintained.



<!-------------------------------------------------------------------->
[RC6502 bus]: https://github.com/tebl/RC6502-Apple-1-Replica/blob/master/Bus.md


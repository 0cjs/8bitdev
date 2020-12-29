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


Design and Layout Notes
-----------------------

- Though this is a two-layer board, all traces are on the back (solder)
  side, allowing the entire top (component) side to be a pseudo ground
  plane. (It's interrupted by through-holes for components and headers, but
  this should cause minimal disruption of return paths.
- It's not clear if wire-wrap will also be able to take advantage of this
  pseudo ground plane, but at least it will be no worse than wire wrap
  would normally be.
- The "power strip" around the edges of the board (on the back side) allows
  Vcc access from pretty much any point on the board without jumper wires
  or vias and topside traces. This helps preserve the pseudo ground plane.

For more on this, see Wilson Mines' [Avoiding AC-Performance Problems][wm
ac] and perhaps [Techniques for reliable high-speed digital circuits] on
forum.6502.org.


TODO
----

- Add prototype area.
- Pin functions on silk screen.



<!-------------------------------------------------------------------->
[RC6502 bus]: https://github.com/tebl/RC6502-Apple-1-Replica/blob/master/Bus.md
[f65 2029]: http://forum.6502.org/viewtopic.php?f=4&t=2029
[wm ac]: https://wilsonminesco.com/6502primer/construction.html

SD SBC-200
==========

These are programs for the SDSystems [SBC-200 Single Board Computer][man].
This is a 5"×10" compatible SBC with a 4 MHz Z80, 4× 1K-8K EPROM, 1K RAM,
an 8251 serial port with RS-232 interface (DTE or DCE), parallel I/O, and
compatibility with the S-100 bus.

### Technical Notes

See [the manual][man] for full details, but key points are:
- On-board RAM/EPROM is always enabled on reset; it may be disabled.
- Jumpers X17 and X18 determine the reset start location, which can be set
  to any 4K boundary. See below.
- The onboard 1K RAM, if used, is mirrored in its bank based on the size of
  the EPROMs used (e.g., 8K EPROMs give an 8K RAM bank with the 1K mirrored
  in it).
- The UART is a standard 8251, but the CTC (counter/timer circuit) used to
  generate the baud rate clock is a Mostek MK3882.
- The Mostek 3882 CTC has vectored interrupt capability.
- The parallel I/O is an 8-bit output latch and an 8-bit input latch, along
  with handshake lines.

#### Memory Configuration

There are 4 EPROM sockets which, as a group, may be jumpered to use 1K, 2K,
4K or 8K devices. There is also 1K of onboard RAM which may be disabled
through software.

The address space that can be configured for the EPROM and RAM depends on
the EPROM size jumpering:
- 1K: an 8K block at $0000, $2000, …, $E000.
- 2K: a 16K block at $0000, $4000, $8000, or $C000.
- 4K: a 32K block at $0000 or $8000.
- 8K: a 64K block at $0000.

Each block ("bank" in the user manual) is twice the size of the total EPROM
size and split into two areas, the lower half and upper half. EPROMs 0-2
can be jumpered to appear in either half; EPROM 3 always appears in the
lower half because what would be its address space in the upper half is
reserved for RAM.

Most of the code here is built for ROM starting at $E000 and RAM at
$FC00-$FCFF. The code does not rely on RAM below this being mirrored, so
external RAM may be used if the internal RAM is disabled. The following
configurations will work, with the first EPROM going in socket 0 for the 1K
and 2K configurations or socket 2 for the 4K configuration.

    Size Block  Side  │ ROM 0  ROM 1  ROM 2  ROM 3  RAM
    ──────────────────┼────────────────────────────────────────────────
     1K  $E000  low   │ $E000  $E400  $E800  $EC00  $FC00
     2K  $C000  high  │ $E000  $E800  $F000  $D800  $F800,$FC00
     4K  $8000  high  │ $C000  $D000  $E000  $B000  $F000,$F400,…,$FC00

#### Reset / Startup

When the reset start is jumped to a a non-zero location via the X17/X18
jumpers, the following instructions must be the first ones executed:

    jp   x003       ; replace X with the actual start address MSnybble
    in   A,($7F)    ; reset non-zero boot location hardware

#### I/O Addresses

    $78  ??     MK3882 CTC channel 0
    $79  ??     MK3882 CTC channel 1
    $7A  ??     MK3882 CTC channel 2
    $7B  ??     MK3882 CTC channel 3
    $7C  rw     8251 data port
    $7D  rw     8251 status/control port
    $7E  rw     parallel input data latch and output data latch
    $7F  rw     parallel output handshake (2 lines), memory control
                  b7-2: ¿unused?
                  b1:   on-board RAM/ROM control: 1=disable, 0=enable
                  b0:   handshake control



<!-------------------------------------------------------------------->
[man]: https://deramp.com/downloads/sd_systems/manuals/SDS_SBC-200.pdf
[vcf]: https://forum.vcfed.org.

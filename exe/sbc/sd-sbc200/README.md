SD SBC-200 
==========

These are programs for the SDSystems [SBC-200 Single Board Computer][man].
This is a 5"×10" compatible SBC with a 4 MHz Z80, 4× 1K-8K EPROM, 1K RAM,
an 8251 serial port with RS-232 interface (DTE or DCE), parallel I/O, and
compatibility with the S-100 bus.

### Programs

* `SD-SBC200_serial_echo.asm`: A serial port read/echo program written
  by n1jbq on the [VCF Forums][vcf].

### Technical Notes

See [the manual][man] for full details, but key points are:
- On-board RAM/ROM is always enabled on reset; it may be disabled.
- Jumpers X17 and X18 determine the reset start location, which can be set
  to any 4K boundary. See below.
- The onboard 1K RAM, if used, is mirrored in its bank based on the size of
  the ROMs used (e.g., 8K ROMs give an 8K RAM bank with the 1K mirrored in
  it).
- The UART is a standard 8251, but the CTC (counter/timer circuit) used to
  generate the baud rate clock is a Mostek MK3882.
- The Mostek 3882 CTC has vectored interrupt capability.
- The parallel I/O is an 8-bit output latch and an 8-bit input latch, along
  with handshake lines.

When the reset start is jumped to a a non-zero location via the X17/X18
jumpers, the following instructions must be the first ones executed:

    jp   x003       ; replace X with the actual start address MSnybble
    in   A,($7F)    ; reset non-zero boot location hardware

I/O Addresses:

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

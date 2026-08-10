;   Sord M5 Hardware Definitions

;---------------------------------------------------------------------
;   Devices

;   Z80 CTC
CTC_CH0         equ  $00    ; EXINT (47K pullup, cart slot) (N/C)
CTC_CH1         equ  $01    ; GND                           (N/C)
CTC_CH2         equ  $02    ; † TCK, 9918 GROMCLK           EXCLK (cart slot)
CTC_CH3         equ  $03    ; TMS9918 INT output (vblank)   (no pin)
;   https://github.com/0cjs/sedoc/blob/main/EE/periph/z80.md#ctc
;   • Read: downcounter
;   • Write b0=0: interrupt vector word in b7-3 w/low bits 0. (mode 2 response)
;   • Write b0=1: control word; see docs above for details
;   See ctc_initdata for details of BIOS initialisation.
;                           ; Source: CLK/TRGn              Output: ZC/TOn
;   † TCK = GROMCLK = crystal÷24:
;       NTSC 10.738635 MHz → 447.443 kHz; PAL 10.6875 → 445.3125 kHz.

;   TMS9918 (NTSC) or TMS9929 (PAL) VDP.
VDP_VRAM        equ  $10
;   VRAM data port: read/write current addr and increment current addr.
VDP_CTRL        equ  $11
VDP_STATUS      equ  VDP_CTRL
;   Read: sole status register. Write (always two bytes, LSB then MSB):
;   sets curaddr or writes registers. Write format, LSB first:
;   • aaaaaaaa 00aaaaaa: Setup VRAM and current addr for read.
;   • aaaaaaaa 01aaaaaa: Setup VRAM and current addr for write.
;   • dddddddd 10000rrr: Write data to register rrr.
;     • 0: 7=ext input; 6=mode bit 3
;     • 1: 7=sprite-mag 6=sprite-size 5=reserved 4,3=mode 2=interrupt-enable
;          1=display blank (0=blank 1=active); 0=1 for 16K RAM
;          • modes M3,M2,M1:  000 Graphics I,  001 Graphics II
;                             010 Multicolor,  001 Text
;     • 2: (0-15)  Name Table base addr
;     • 3: (0-255) Color Table addr
;     • 4: (0-7)   Pattern/Text/Multicolor Generator addr
;     • 5: (0-127) Sprite Attribute Table addr
;     • 6: (0-7)   Sprite Pattern Generator addr
;     • 7: 7-4:text color 1; 3-0:text color 0, BG in all modes
;   Notes:
;   • If you write a data byte and want to abort (rather than follow with
;     a register byte), read the status register to reset things.

;   TMS76489 sound chip.
SOUND           equ  $20
;   The chip is clocked from the ~3.58 MHz CPU clock, which is ÷16 for timers
;   that count a half waveform. Thus (per data sheet f=clock/32×ctr):
;   f = 111861/ctr and f = 6991/ctrMSbits (BIOS sets just counter MSbits).
;   • 1cc0ffff 0xffffff: frequency data (2 byte xfer), c=channel 0-2, f=freq.
;                        (1st byte latched; can send 2nd byte only for update)
;   • 1cc1aaaa:          update attenuator: c=channel 0-2/noise, a=attenuator
;                        attn bits: 3=2dB  2=4dB  1=8dB  0=16dB  all-set=off
;   • 1110xfnn:          noise source

KEYBOARD        equ  $30
;   Keyboard rows 0-6 are $30-$36; joysticks on $37

;   Parallel printer output. Latched on 74LS374, /OE always low.
PRINTER         equ  $40        ; output latch only

;   CMT (cassette tape) port.
CMT             equ  $50
PTR_STROBE      equ  $50
;   • Read:   7=RESET key  1=busy        0=CMT-input
;   • Write:               1=CMT-remote  0=cmt-out,ptr-strobe
;   ULA PSTB inverted to printer port P1 /PSTB, so 1=strobe, 0=no-strobe

;   External I/O lines on cartridge port.
EXTIOA          equ  $60
EXTIOB          equ  $70


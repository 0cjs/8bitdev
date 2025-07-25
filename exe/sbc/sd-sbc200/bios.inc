;   sd-sbc200/bios.inc: BIOS definitions for the SDSystems SBC-200.
;
;   This has extension .inc so it's not built standalone by the automatic
;   build system; it's usable only included in a source file that sets up
;   the CPU definitions etc. properly.
;
;   Requires: std.i80

; ----------------------------------------------------------------------
;   IO Devices

MK3882_ch0  equ  $78    ; CTC channel 0
I8251_data  equ  $7C    ; UART data port
I8251_stat  equ  $7D    ; UART status/control port
SYS_stat    equ  $7F    ; memory control, parallel I/O handshake

; ----------------------------------------------------------------------
;   Reset code.
;
;   The SBC-200 can be jumpered to start at an address other than $0000.
;   If you do this, you need to define ROM_BASE to the address you've
;   selected for this (via jumpers X17/X18) and execute the following
;   macro at the beginning of the ROM.

RESET_INIT  macro
            org  ROM_BASE
            jp   ROM_BASE+3     ; switch from "faked 0" addr
                                ;   to actual address of ROM
            in   a,(SYS_stat)   ; reset non-zero boot location circuitry
            endm

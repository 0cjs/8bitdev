;   sd-sbc200/bioscode.inc: A small "BIOS" for the SDSystems SBC-200.
;
;   This has extension .inc so it's not built standalone by the automatic
;   build system; it's usable only included in a source file that sets up
;   the CPU definitions etc. properly.
;
;   Requires: sd-sbc200/bios.inc

; ----------------------------------------------------------------------
;   Serial I/O

;   ♣A ♡* ┃ Initialise the serial port to 9600 bps.
bios_init   ld   a,$4E
            out  (I8251_stat),a
            ld   a,$37
            out  (I8251_stat),a
            ld   a,$45
            out  (MK3882_ch0),a
            ld   a,$0D          ; 9600 baud
            out  (MK3882_ch0),a
            ret

;   ♢A ♡* ┃ Send char in a out the serial port when it's ready.
prchar      push af             ; save char to send
.wait       in   a,(I8251_stat)
            and  a,$01          ; TXRDY set?
            jp   Z,.wait        ;    no: wait on it
            pop  af             ; restore char to send
            out  (I8251_data),a
            ret

;   ♠A ♡* ┃ Wait for a char from the serial port and return it in A.
rdchar      in   a,(I8251_stat)
            and  a,$02          ; RXRDY set?
            jp   Z,rdchar       ;    no: wait on it
            in   a,(I8251_data)
            and  $7F            ; strip parity
            ret

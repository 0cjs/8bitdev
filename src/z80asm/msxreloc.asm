;   POC using z80asm to build relocated MSX code.
;
;   This is built with z80asm, a fairly minimal z80 assembler that's available
;   as a package in most Linux distros. Its original source seems to be:
;     http://download.savannah.nongnu.org/releases/z80asm/
;
;   z80asm produces straight binary output files with no location
;   information; the output is in exactly the order of the source file
;   directives, i.e., `org` directives affect only the address calculations
;   for labels done by the assembler.
;
;   (The one exception to this is the `seek` directive which changes the
;   current position in the output file. In combination with `incbin`
;   this is particularly handy for patching binaries; for an example see
;   `/usr/share/doc/z80asm/examples/seek.asm`.)

; ----------------------------------------------------------------------
;   BLOAD file header.
;
;   Possibly we should have a tool like bin/mz80asm from
;   gitlab.com/retroabandon/frieve-msxfan-re to create the BLOAD file
;   header for us. But in this case, for stand-alone simplicity, we just
;   define it right in this file.

            db   $FE        ; BLOAD magic number
            dw   start      ; starting location
            dw   end - 1    ; last location to load
            dw   entry      ; entry point

; ----------------------------------------------------------------------
;   MSX BIOS definitions

ENASLT:         equ $0024   ; DI and map A=slotdesc to page containing addr HL
EXPTBL:         equ $FCC1   ; slot 0 expansion mode / main BIOS ROM slot addr
RAMAD1:         equ $F342   ; slotdesc of RAM in page 1 (DOS)

; ----------------------------------------------------------------------
;   Main

            org $C000           ; initial BLOAD location
start:
entry:      ;   Relocate page 3 and page 1 code.

            di                  ; interrupts must be disabled when ROM switched out

            ;   After reset the MSX2 system ROM (or disk ROM?) will find
            ;   two pages of RAM to assign to page 0 ($0000) and 1 ($4000)
            ;   address space and store their slot descriptors (E000SSPP)
            ;   in RAMAD0 and RAMAD1. These are unused by BASIC so we can
            ;   store our music routines and data in the page 1 RAM so long
            ;   as we ensure we don't hand control to the BASIC interpreter
            ;   while it's mapped in.
            ld a,(RAMAD1)       ; slot descriptor for default page 1 RAM
            ld h,040h           ; page 1 start addr hi
            ld l,000h           ;   and lo
            call ENASLT         ; map page

            ;   Copy page 1 code from the BLOAD locations to page 1.
;   XXX how do we calculate where it was BLOADED?
;   guess swe need a symbol just before the code's `org`
            ld hl,p1dst_src     ; BLOADed data start address
            ld de,p1dst         ; destination address in page 1
            ld bc,p1dst_len     ; length
            ldir                ; copy

            ;   The routine to request playing a particular BGM track must be in
            ;   in BASIC RAM (pages 3 and 4) so it's available while the BASIC
            ;   interpreter is running and page 1 is mapped to BASIC ROM. Copy
            ;   it from the relatively low load location into higher memory.
            ;   Subsequent BASIC programs must immediately reserve this memory
            ;   using the CLEAR statement to avoid BASIC stomping on this.
            ld hl,usr3_src      ; BLOADed data start address
            ld de,usr3          ; destination address
            ld bc, p1dst_src - usr3_src ; length
            ldir                ; copy

            ;   Restore page 1 mapping to BASIC ROM and re-enable interrupts
            ;   before returning to BASIC interpreter.
            ld a,(EXPTBL)       ; slot descriptor for page 1 main BIOS/BASIC ROM
            ld h,040h           ; page 1 start addr hi
            ld l,000h           ;   and lo
            call ENASLT         ; map page
            ei
            ret

end:        end

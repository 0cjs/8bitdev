;   BIOS definitions for ROM routines in Sord M5 BIOS
;   See the disassembly bios-mame.z80 for details.
;
;   Register and flag usage:
;   • ♠ input and/or output; ♣ destroyed; ♡ preserved.
;   • Flags assumed destroyed except where specified otherwise.

zeromem     equ  $0860      ; ♠HLBC ♣ADE  At HL fill BC bytes with $00

;   Console routines; see the console context record in biosram.inc.
csrhide     equ  $0638      ; hide the cursor, restoring the char under it
csrshow     equ  $064E      ; show the cursor, saving the char under it
con_switch  equ  $0C62      ; switch to the other console context
con_setmode equ  $0DD8      ; set the screen up for the co_flags video mode
con_init    equ  $0E0B      ; init both console contexts and the screen
puts        equ  $1063      ; print the counted, NUL-terminated string at HL
dispatch    equ  $1076      ; jump to entry A of the word table at HL
puts6       equ  $105B      ; puts with the count preset to 6
putlit      equ  $1082      ; putchar but print (not interpret) control codes
putchar     equ  $1088      ; print the char in A at the cursor
newline     equ  $10ED      ; carriage return and line feed
clearscreen equ  $1393      ; clear the screen
csrhome     equ  $13B6      ; cursor to the top left of the window
;   The control-code handlers a cartridge may point its own ctltab at.
scrollup    equ  $12BF      ; scroll the window up
scrolldown  equ  $12B3      ; and down
linefeed    equ  $10F0      ; down a row, scrolling if need be
tab         equ  $1158      ; space out to the next tab stop
csrright    equ  $10FC      ; the four cursor movements, as the $1C-$1F
csrleft     equ  $10FF      ;   control codes reach them
csrup       equ  $10F9
csrdown     equ  $10F6
scr_rdchars equ  $0EEC      ; read a sequence of chars from the screen
scr_rdchar  equ  $0F00      ; read a character from the screen
ptrchar     equ  $1799      ; send one character to the printer
ptrstr      equ  $17C7      ; send a counted string, expanding tabs
setcursor   equ  $13DD      ; move the cursor to D = column, E = row
snd_freq    equ  $1176      ; play the co_bellfreq tone, i.e. ring the bell

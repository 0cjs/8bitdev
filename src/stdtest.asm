;   Generic test code for */std.aXX include files.
;   This covers the set of common functions, macros and pseudo-ops that
;   we use across all architectures.

;   LB() -     low byte (16-bit LSB) of a value
;   MB() - middle byte (16-bit MSB) of a value
;
T_LB_8          equ LB(8)
T_MB_8          equ MB(8)
T_LB_FEDC       equ LB($FEDC)
T_MB_FEDC       equ MB($FEDC)
T_LB_12340      equ LB($12340)
T_MB_12340      equ MB($12340)

;   ds - define (reserve) space
;   db - define byte
;   dw - define word (in machine address word order)
;
defalloctest
dstest0         ds  3
dstest1         ds  1


;   The dup() function doesn't work, probably because it produces a "real"
;   value which is inserted into the db/byt without further interpretation,
;   rather than text that would then be parsed again by db/byt argument
;   interpretation. We're still working out how to deal with this.
;dbtest         db  $00,"abc",dup(3,$FF),$00      ; attempt at generic
;dbtest         db  $00,"abc",3 dup $FF,$00       ; Intel syntax
;dbtest         db  $00,"abc",[3]$FF,$00          ; Motorola syntax
dbtest          db  $00,"abc",$FF,$FF,$FF,$00

dwtest          dw  $ABCD



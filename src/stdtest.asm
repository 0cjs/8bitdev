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

;   The dup() function doesn't work for reasons we don't understand; asl
;   always gives us "unknown function," though if we reduce the definition
;   to one parameter it finds the function and gives us a wrong number of
;   params error. So for the moment we stick with the Motorola syntax and
;   disable the Intel test of this.
;dbtest         db  $00,"abc",dup(2,$FF)
dbtest          db  $00,"abc",[2]$FF

dwtest          dw  $ABCD



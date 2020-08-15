;   Generic test code for */std.aXX include files.
;   This covers the set of common functions, macros and pseudo-ops that
;   we use across all architectures.

;   ds - define (reserve) space
;   db - define byte
;   dw - define word (in machine address word order)
;
defalloctest
dstest0         ds  3
dstest1         ds  1
dbtest          db  $00,"abc",[2]$FF
dwtest          dw  $ABCD

                              1 ;   narrow.a65: Generate test output for use with testmc.asxxxx
                              2 ;
                              3 ;   This produces "narrow" symbol tables with symbol names truncated
                              4 ;   to 14 (.lst, .sym) or 8 (.map) chars.
                              5 
                              6             .radix h
                              7 
   0000 6E 61 72 72 6F 77     8 local0:     .strz   'narrow local 0'
        20 6C 6F 63 61 6C
        20 30 00
   000F 01 02 FE FF           9             .db     01,02, 0FE, 0FF
                             10 
                             11             .globl  g_narrow
   0013 6E 61 72 72 6F 77    12 g_narrow:   .strz   'narrow global 0'
        20 67 6C 6F 62 61
        6C 20 30 00
                             13 
   0023 6E 61 72 72 6F 77    14 local1:     .strz   'narrow local 1'
        20 6C 6F 63 61 6C
        20 31 00
                             15 
                             16             .globl  c_narrow
   0032 AD FE FF      [ 4]   17 c_narrow:   lda     0FFFE
   0035 8D 3F 00      [ 4]   18             sta     c_vec
   0038 AD FF FF      [ 4]   19             lda     0FFFF
   003B 8D 40 00      [ 4]   20             sta     c_vec+1
   003E 60            [ 6]   21             rts
   003F                      22 c_vec:      .blkw   1
                             23 
                             24 ; note double-colon here so we don't need to write name again in .globl
   0041                      25 n_longsym_123456789_123456789_123456789_123456789_123456789_123456789_123456789:: .blkw   1
                             26 
   0043 74 68 69 73 20 6D    27 oddsym:     .str    'this makes total number of symbols odd'
        61 6B 65 73 20 74
        6F 74 61 6C 20 6E
        75 6D 62 65 72 20
        6F 66 20 73 79 6D
        62 6F 6C 73 20 6F
        64 64
ASxxxx Assembler V05.31  (Rockwell 6502/6510/65C02)                     Page 1
Hexadecimal [16-Bits]                                 Thu Oct 10 19:14:09 2019

Symbol Table

    .__.$$$.       =   2710 L   |     .__.ABS.       =   0000 G
    .__.CPU.       =   0000 L   |     .__.H$L.       =   0000 L
  0 c_narrow           0032 GR  |   0 c_vec              003F R
  0 g_narrow           0013 GR  |   0 local0             0000 R
  0 local1             0023 R   |   0 n_longsym_1234     0041 GR
  0 oddsym             0043 R

ASxxxx Assembler V05.31  (Rockwell 6502/6510/65C02)                     Page 2
Hexadecimal [16-Bits]                                 Thu Oct 10 19:14:09 2019

Area Table

[_CSEG]
   0 _CODE            size   69   flags C180
[_DSEG]
   1 _DATA            size    0   flags C0C0


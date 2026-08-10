;   BIOS definitions for RAM in Sord M5 BIOS
;   See the disassembly bios-mame.z80 for details.

;---------------------------------------------------------------------
;   RAM Configuration

;   $5D bytes initialized with init_ramstart.
ramstart        equ $7000       ; we _think_ it runs $7000-$7FFF
int2tab         equ $7000       ; start of mode 2 interrupt table
ivec_exclk      equ $7000       ; $7000 CTC cartridge port interrupt on falling edge
ivec_1khz       equ $7002       ; $7002 CTC 1 kHz counter interrupt
ivec_disabled   equ $7004       ; $7004 CTC channel does not interrupt
ivec_vblank     equ $7006       ; $7006 TMS9918 INT output on vertical blank interval
intrst30        equ $7008       ; jmp ????
intrst38        equ $700B       ; jmp ????
ctltab          equ $700E       ; word: control character dispatch table used
                                ;   by `ctlchar`; init'd to `ctltab_rom`, but
                                ;   a cartridge may point it at its own
rambase         equ $7010       ; tested lowest byte of RAM
ramtop          equ $7012       ; 1 past tested highest byte of RAM
stackbase       equ $7014       ; current base of stack which starts just below this
ramtop2         equ $7016       ; 1 past tested highest byte of RAM
x7018           equ $7018       ; XXX init to $00
                                ;   b1=1 selects con1 over con0
                                ;   b0=1 offsets the con VRAM tables (2nd page?)
                                ;   b3, b2 = XXX
cmt_period      equ $7019       ; CMT bit half-period: cmt_delay spins on
                                ;   it, so it sets the tape data rate
ptr701A         equ $701A       ; XXX init to $94; b1-0 = keyboard layout,
                                ;   set by keymode and read by keychar;
                                ;   b7 asks keyscan for the key click
keylayoutp      equ $701B       ; word: → keylayouts; keychar indexes it
;   The key click tone that snd_freq2 sounds, exactly as co_bellfreq and
;   co_belllen are snd_freq's. A cart wanting an audible keyboard has to
;   set them itself.
snd_ch2freq     equ $703A       ; MS 6 bits of the 10-bit divisor
snd_ch2len      equ $703B       ; duration, to be counted down in snd_ch2cnt
;   Joystick state, maintained by joyscan: two bytes per stick, the button
;   code and the direction code, each zeroed while the other is active. The
;   vectors are called on a change, if vblank_smask b4 allows it.
joy_state       equ $701D       ; 2 bytes each for joystick 1 then 2
joy_dirvec      equ $7021       ; word: called when a direction changes
joy_btnvec      equ $7023       ; word: called when a button changes

;   Time of day, advanced by clocktick once clk_pre has counted down a
;   second's worth of vblank interrupts.
clk_pre         equ $7049       ; vblanks left until the next second
clk_sec         equ $704A       ; 0-59
clk_min         equ $704B       ; 0-59
clk_hr          equ $704C       ; 0-23

;   Key buffer: a ring of codes filled by the keyboard scan and drained by
;   getkey. Control codes below $20 occupy two entries, the second being
;   the byte getkey hands back in B.
keybuf          equ $7031       ; word: base address of the ring
keybuf_hd       equ $7033       ; index the scan writes at
keybuf_tl       equ $7034       ; index getkey reads from
keybuf_msk      equ $7035       ; ring size less one, to wrap the indices

;   How long the input routines wait before giving up: armtimeout feeds
;   these to tmr_start, and keywait watches vblank_smask b7 for the result.
;   A zero count means wait for ever.
keytimeout      equ $7036       ; word: ticks to wait
keytimeout_pre  equ $7038       ; frames per tick

vblank_smask    equ $703C       ; which routines the vblank handler calls;
                                ; init=$23 = %0010.0011
                                ;   b0=vblank_user  b1=clocktickvb
                                ;   b2=sw_tick      b3=tmr_tick
                                ;   b4=joyscan      b5=keyscan
                                ;   b6=XXX $028F
                                ;   b7=tmr_count ran out: set by tmr_tick,
                                ;      read by keywait to give up waiting
                                ; snd_tick runs from the same place, but
                                ; unconditionally, with no mask bit.
;   The software timer table vbtimers walks: six bytes per slot, being a
;   16-bit countdown (b7 of the high byte parks it), a reload value, its
;   counter, and the address to call. set_vbtimers installs them.
vbtimer_n       equ $703D       ; how many slots
vbtimer_p       equ $703E       ; word: where they start
;               equ $703F
vblank_inproc   equ $7040       ; b0=1 if vblank irq is processing
;   Two vblank-driven counters, each with a prescaler so that they can tick
;   more slowly than the frame rate. sw_* counts up and is only ever read;
;   tmr_* counts down and, on reaching zero, sets vblank_smask b7 to say so
;   and switches its own handler off. keywait watches that bit to give up
;   waiting for a key.
sw_ivl          equ $7041       ; prescaler reload for sw_tick
sw_pre          equ $7042       ; and its countdown
sw_count        equ $7043       ; word: ticks since sw_start
tmr_ivl         equ $7045       ; prescaler reload for tmr_tick
tmr_pre         equ $7046       ; and its countdown
tmr_count       equ $7047       ; word: ticks left before b7 goes up
vblank_user     equ $7053       ; ¿user vblank subroutine?
vblank_ctrl     equ $7055       ; VDP status read on last vblank interrupt

;   Tone duration counters, aged by snd_tick every vblank; the channel is
;   silenced as its counter reaches zero.
snd_ch2cnt      equ $7058       ; loaded from snd_ch2len by snd_freq2
snd_ch1cnt      equ $7059       ; loaded from co_belllen  by snd_freq
ptr_flags       equ $705A       ; printer: b2=expand tabs b1=CR at the
                                ;   right margin b0=LF after every CR
ptr_width       equ $705B       ; printer: column to break the line at
ptr_col         equ $705C       ; printer: column the head is now at, reset
                                ;   by every CR that ptrchar sends
snd_uservec     equ $705D       ; word: called by count65k through JP_HL;
                                ;   init'd to `ret18`, i.e. do nothing
x705F           equ $705F       ; word: base of the volume envelopes the
                                ;   sound player uses; init'd to snd_envtab
snd_reload      equ $7061       ; count1k's reload value, init'd to $1F, so
                                ;   the 1 kHz tick divides down to ~32 Hz
cmt_len         equ $7090       ; length of the tape block being read
cmt_maxlen      equ $7091       ; largest 'F' block cmt_readblk will accept
x708E           equ $708E       ; XXX cassette mode: b1=verify not load,
                                ;   b0=VRAM not RAM
x7255           equ $7255       ; word: XXX threshold cmt_sync compares against
cmt_halfbit     equ $7257       ; half period cmt_sync measured off the
                                ;   lead-in, used by cmt_getbits

count1k         equ $7062       ; word decremented w/every 1 kHz tick

;---------------------------------------------------------------------
;   Console contexts
;
;   Two instances of a $24/36-byte record describing the state of a text
;   console: video mode, the VRAM addresses of the five VDP tables, the
;   text window within the screen, cursor position/appearance and the bell
;   tone. They are contiguous, con0 immediately followed by con1.
;
;   `load_con` (RST 08) points HL at con0 and loads its co_flags byte;
;   nearly all code works on con0. x7018 b1 selects which context
;   `set_vdpregs` reads, and the tail of `con_init` swaps the two records
;   wholesale, so the pair look like a current/alternate screen pair.
;   `con_setdefaults` reloads co_flags..co_colors from ROM.
;
;   Fields are bytes unless marked as words. The ROM defaults are in
;   `con_defaults_data`, which covers co_flags through co_sprsize; nothing
;   has yet been seen to use the remaining offsets $1C-$23.

con0            equ $7094       ; console context 0
con1            equ con0+CON_LEN ; $70B8 console context 1

CON_LEN         equ $24         ; 36
co_flags        equ $00         ; b7-5 = VDP M1-3 (VDP mode)
                                ; b4=cursor is outside the window, so is not
                                ;    drawn; maintained by `setcursor`
                                ; b3=cursor is currently displayed
                                ; b2,b1,b0 = XXX console options
co_name         equ $01         ; word: VDP name table addr
co_color        equ $03         ; word: VDP colour table addr
co_patgen       equ $05         ; word: VDP pattern generator addr
co_sprattr      equ $07         ; word: VDP sprite attribute table addr
co_sprgen       equ $09         ; word: VDP sprite pattern generator addr
co_colors       equ $0B         ; VDP r7: b7-4 = text colour 1, b3-0 = colour 0
;   Text window; the cursor position below is relative to it.
co_wtop         equ $0C         ; topmost screen row of the window
co_wleft        equ $0D         ; leftmost screen column of the window
co_wrows        equ $0E         ; window height in rows
co_wcols        equ $0F         ; window width in columns
;   Screen size, as opposed to that of the window above; `winreset` resets the
;   window to the full screen by copying this pair over co_wrows/co_wcols.
co_scrrows      equ $10         ; screen height in rows
co_scrcols      equ $11         ; screen width in columns, and so also the
                                ;   VRAM bytes per row ($28=40 or $20=32)
co_csrrow       equ $12         ; cursor row,    relative to the window
co_csrcol       equ $13         ; cursor column, relative to the window
                                ;   Both may go out of range, which is what
                                ;   co_flags b4 records; see `setcursor`.
co_csraddr      equ $14         ; word: VRAM addr of the cursor
co_csrsave      equ $16         ; char under the cursor, saved while it's shown
co_csron        equ $17         ; blink: ticks the cursor stays displayed
co_csroff       equ $18         ; blink: ticks the cursor stays hidden
co_bellfreq     equ $19         ; bell tone: MS 6 bits of the 10-bit divisor
co_belllen      equ $1A         ; bell tone: duration, counted down in snd_ch1cnt
co_sprsize      equ $1B         ; b7 = VDP sprite size, b6 = sprite magnify;
                                ;   b5-b3 also hold the resulting sprite
                                ;   size in pixels, which sprsetsize puts
                                ;   there from sprsizetab

worktop         equ $7262       ; (poss.) top of working mem, above is $9E/158 bytes stack
buf40           equ $7064       ; three 32-byte sound voice blocks, set up
                                ;   by INI_RAM61 from snd_voiceinit and
                                ;   walked by count65k through IX

;               equ $7262       ; max stack growth?
stackstart      equ $7300       ; initial stack location; grows down just below here


;
;   std.asm - Standard all-CPU definitions
;
;   These are some standard definitions (mainly macros) we commonly
;   use with source code assembled with the Macro Assembler AS.
;   These apply to all CPUs; the individual CPUs' std.i80 etc. files
;   include this.

;   In general, we use {NOEXPAND} on macros that do not generate code in
;   order to keep the listing clean. However, for macros that do generate
;   code we do not use it so that we can see the code that was generated;
;   without this one sees just a (MACRO) line followed by the address after
;   the macro, which can be a bit confusing.

;   Require that `sym` be defined by the file that included this or fail
;   the assembly. This is useful for better error messages when someone's
;   forgotten an external definition.
;
;   TODO: Possibly this could take a second parameter to add to the
;   error message to remind the developer what the setting means.
;
reqdef      macro sym,{NOEXPAND}
        if ~~symexist(sym)
            error '`sym` must be defined before including this file'
        endif
            endm


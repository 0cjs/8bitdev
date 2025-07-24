CLIC Standard Library
=====================

XXX After some work, it's seeming as if trying to have a cons-cell-only/
no-obdata version of CLIC with reasonable facilities may strain the library
definitions too much. Probably the "tiny" CLIC needs to just drop most
functions, focusing mainly on numerical processing as the early BASICs did.
(But keep the `m[rwc]` stuff?)

Notation:
- Parameters _x_ are in upper case in the definition: `(f X)`.
- Optional params are preceeded by an inverted question mark, `¿`.
- Ellipses `…` indicate previous parameters may be repeated.

#### Control Flow

- ★`(cond (PRED ¿FORM) …)` Conditional choice.

- ★`(if PRED TRUE ¿FALSE)`: Conditional choice.

- ★`(do ???)`: ???

- From R5RS §6.4: apply, map, for-each
- From R5RS §6.5: `eval`

#### Comparisons

- `(eq? X Y)`: Pointer equality.
- `(eql? X Y)`: Conceptual equality even if pointers are different.
- `(equal? X Y)`: Follows structure.

#### Arithmetic

- `(+ …)`, `(- N …)`, `(* N …)`, `(/ …)`: Basic arithmetic.

XXX See CL [-](https://novaspec.org/cl/f__minus) and adjacent for
how multiple arguments work.

- `(= …)`, `(/= …)`, `(< …)`, `(<= …)`, `(>= …)`, `(> …)`
  - On multiple nubmers, all equal, no two equal, monotonically decreasing,
    monotonically non-increasing, etc.

#### List Manipulation

* `(co ATOM LIST)` / `COns`: Construct a new list by prepending _atom_ to
  _list._ (Entries may be shared with other lists.)
* `(hd ATOM LIST)`
* `(tl LIST)`
* `(li …)` / `LIst`: Create list.
  - Each argument is evaluated and a list of their results returned.
  - Ex: `(li (+ 1 2) (+ 3 4))` → `'(3 7)`.
* `(le LIST)` / `length`

- R5RS §6.3.2: null, append, reverse, list-tail (drop), list-ref (index),
  member, assoc.
- `set-car!` vs. `setf`

#### Characters, Printing, Formatting, Input

* `*n` / `*nl*`: List of chars needed to be printed to generate a newline
  on the output terminal. (Typically `(list (ch 'cr) (ch 'lf))`
* `(ch SYM)` / `char`: Return sym1 of ASCII character corresponding to
  charname _sym._ Most charnames are taken from the ASCII standard, but
  some implementations may have additional names, e.g., `'up` for cursor
  up. (Replace with syntax `#\`?)
  - Ex: `(a 'sp)` gives a space (l$20).
  - Ex: `(a 'cr)` gives a carriage return ($0D).
* `(pr …)` / `PRint`: Print values.

* `(pl …)` / `PLine`: Print optional values and newline.
  - Same as `(pr … (a 'cr) (a 'lf))` or whatever platform needs for newline.

* `(fp F X …)` / `fprint`: Format and print value _x_ according to
  specification _f._
  - (Can't have format-only `f` on systems w/o strings.)

* `(rd)` / `read`

#### Machine Access

Below, _addr_ is either an integer [-32768,65535] or a list of byte values
LSB first, e.g. `'($03 $C0)` for address $C003. (We do LSB first to make
accessing multiple addresses in a single page easier.)

* `(mr ADDR)`: Machine address read ("peek").
  - Returns value in range 0–255.

* `(mw ADDR N)`: Machine address write ("poke")
  - Deposits _n_ at _addr._ Returns ???.
  - Signals overflow if _n_ not in range [-128,255].

* `(mc ADDR N M)`: Machine address call.
  - Load the A register (or equivalent) with _n_ (range [-128,255]) and the
    index register (HL, X, XY) with _m_ (range [-32768,65535]) and then
    call the code at _addr._
  - Returns ???.

#### "Compatibility"

These are functions and special forms (easily defined by the user? Perhaps
not, without macros) that duplicate functionality above, but in forms
more familiar to some programmers.



Examples of Use
---------------

    (df cr (a 'cr))
    (df lf (a 'lf))
    (df sp (a 'sp))
    (df (greet name)                    ; params actually (gr na)
        (pr 'Hi ', sp name cr lf))

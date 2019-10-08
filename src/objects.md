Objects for a Small Language
============================

This is just kicking around some ideas for the data types one would
want for a small language to run on an 8-bit microprocessor system.

Representation of Objects in Memory
-----------------------------------

Pointers are stored in 16-bit _words_ as _[tagged]_ values that in
some cases represent the object itself, rather than pointing to
storage for the object. A pointer will only ever actually reference
memory in the heap if it points to a _cons cell_ or a _heapdata
header_.

Objects are allocated on the heap with both address and size [aligned]
to a two word (four byte) boundry. Objects in the heap either:
- start with a heapdata header giving format and length information,
  followed object data, of arbitrary length; or
- are a cons cell of two pointer words, the _car_ followed by the
  _cdr_.

Unallocated heap elements must be initialized to "empty" cons cells of
`(nil,nil)`.

Given an arbitrary (properly aligned) address in the heap we cannot
tell if it points to a cons cell or a heapdata object because it might
point into the middle of a heapdata object; thus walking the entire
heap must be done by starting at its lowest location in memory.

This allows us to tag pointers in the following way:
- Heapdata headers are never pointers, because they must be
  distinguishable from pointers in order to determine that a heap
  object is not a cons cell.
- Values with the least siginificant bit set are one of two types: an
  unsigned byte (or char) or a small (14-bit) signed integer.
- Values with the least significant bit clear and a non-zero high
  address byte are pointers into the heap.
- Values with the LSB clear and a zero high address byte are fixed
  constant objects identified by their location so that no heap
  storage is necessary for them. (The first 256 bytes of memory cannot
  be used for heap storage; this isn't a problem since most 8-bit
  processors have other more important uses for this anyway: zero page
  on 6800/6502 and interrupt vectors on the 8080.)

The following table shows the details of tagging and determining
values. `x` represents a don't-care bit, but see below. Objects marked
`R` may contain pointers themselves and need to be recursively
followed by the GC.

    MSB LSB (binary) R  Description
    00   000000 x0      nil
    00   000001 x0      true, t
    00   ?????? x0      (other special values?)
    AA   aaaaaa x0   R  pointer into heap (except special values above)
    NN   000000 01      byte/char (unsigned) value NN
    LL   ffffff 01   R  heapdata header: length LL, format id ffffff (1-63)
    NN   nnnnnn 11      smallint: -8192 to 8191

The `x` bit on pointers into the heap is available for use by the
garbage collector. However, as an alternative a separate bit array
could be allocated for this (one bit for every possible address on
the heap, even those that may be in the middle of heapdata objects),
increasing heap overhead by about 12.5%. (This would not be necessary
for read-only heap areas.) A Schorr-Wait algorithm would require two
bits.

### Heapdata Formats

Note that these are "formats" rather than types: some data types (e.g.
symbol, float) have multiple formats for storage as heapdata objects.

A heapdata object starts with a two-byte header.

The LSB describes the format and always has its least significant two
bits set to `01`. The upper six bits are the format identifier
(ranging from 1-63); when shifted left two bits iwth the lowest two
bits set to the required `01` this whole byte is referred to as the
_format number_. (Format number `$01` is a `byte` with value in the
MSB and no additional data; in the heap this is recognized as the car
of a cons cell rather than as heapdata.)

The MSB indicates the length of the data after the header, in bytes.
(The actual storage used will be _len + 2_ rounded up to the next
longword boundary.) This allows determination of the exact size of any
object on the heap (and thus the location of the next object on the
heap) with no knowledge of the particular heapdata formats. (Storing
the length in longwords was also considered, allowing larger
individual objects, but then individual formats that did not entirely
fill the space would need additional length or termination bytes to
determine the actual length of their data.)

Following are the heapdata formats. The table gives the format number
in hexadecimal; the format identifier in binary and decimal; the size
on the heap and the length value when not variable; and the name of
the format and type using it. Following this are more detailed
descriptions of the individual formats.

    num   binary  id siz len descr
    $09  0000 10   2   8  6   env-header
    $0D  0000 11   3   8  6   env-entry
    $21  0010 00   8          symbol (string)
    $25  0010 01   9   8  4   symbol substring
    $61  0110 00  24          integer
    $69  0110 10  26          float, positive mantessa
    $79  0111 10  30   4  2   word
    $7D  0111 11  31   8  4   longword
    $E9  1110 10  58          float, negative mantessa

    Bit assignments:
      5     Sign bit: floats, ...
      4     Number, including modular
      3     Atomic (?)

- __env-header__: _len=6_. The header record for an environment. The
  data are as follows. All pointers may be `nil` for no value.
  - Pointer to first _env-entry_
  - Pointer to parent environment _env-header_
  - Pointer to symbol for environment name

- __env-entry__: _len=6_. An entry in an environment. The data are
  three pointers to the entry's symbol (name), entry's value, and next
  entry in the environment.

- __symbol__ (or __string__). Data are vector of _len_ bytes, usually
  interpreted as ASCII characters but they may be any byte values.
  Symbols are immutable once created in order to allow storage in ROM.
  Generally symbols would be unique, with new symbols being intern'd
  to maintain uniqueness.

- __symbol__ substring: _len=4_. Data are a pointer to a symbol, start
  point and length. Start point (0-based) plus length must not extend
  past the end of the data of the symbol this references. Not sure yet
  if this could also reference another substring. This is intended to
  make substring operations, particularly recursive `(car somesym)`
  more efficient, but we need to look at ways of turning these into
  symbols (and dealing with their references, if they exist) so that
  the original symbol can be GC'd if it's not directly referenced and
  much of it is no longer needed.

- __word__; __longword__: _len_=2; _len=4_. Data are unsigned 16-bit
  resp. 32-bit integers. Arithmetic is modular and overflow is
  ignored.

- __integer__: A signed integer value of arbitrary length (up to 255
  bytes). Data is a vector of _len_ bytes, LSB to MSB, with sign as
  the highest bit of the MSB. Arithmetic sign-extends the smaller
  value.

- __float__: Positive and negative floating point numbers with
  mantessa of _len_-1 bytes. (Storing the mantessa sign outside of the
  mantessa itself makes calculations easier.) The first byte of data
  is the (always 8-bit) exponent (2's complement with reversed sign;
  `$80` is zero) and the remaining bytes are the mantessa MSB to LSB.
  See below for more details.

#### Floating Point Format and Representation

Floating point values always consist of an 8-bit exponent in the first
byte, followed by however many bytes of mantessa. Negative and
positive numbers are separate heapdata formats; keeping the mantessa's
sign separate from the mantessa itself makes calculations easier. The
sign can be determined from the high bit of the format number.

The exponent is, in the usual way, offset by $80: 0 = $80, 1 = $81,
-1 = $79, etc.

The mantessa, when normalized, is assumed to have an implicit `1` bit
before it. For simplicity we may decide to disallow denormalized
mantessas (with one or more leading zeros) even though this slightly
reduces the range that can be represented by a floating point value.


Types and Literals
------------------

#### Special Constants

- __nil__
- __true__, __t__

#### Modular Numbers

Whenever a modular number is involved in an expression, the result is
always a modular number of the largest size involved; smaller sizes
are sign-extended. Integers are converted to a sign-extended modular
number of the smallest size able to hold the value and its sign bit,
or an overflow error is generated. Floats cannot be converted and
always generate an error. This is intended to make it easy to do
indexed addressing, e.g., `(+ $FF00 2)`.

- __byte__ (__char__): Unsigned 8-bit value; modular arithmetic.
  - Literal: `$xx` where _xx_ is a one- or two-digit hexadecimal value
  - Literal: `%n` where _n_ is a 1-8 digit binary value.
  - Literal: `:c` where _c_ is a character (potentially escaped; see below).
  - Uses: character; data for examine/deposit.

- __word__: Unsigned 16-bit value; modular arithmetic.
  - Literal: `$xxxx` where _xxxx_ is four hex digits (one alternative).
  - Literal: `$$n` where _n_ is a 1-4 hex digits (other alternative).
  - Literal: `%n.n` for high/low bytes where _n_ is 1-8 binary digits.
  - Uses: addresses for examine/deposit.

- __longword__: Unsigned 32-bit value; modular arithmetic. Probably
  won't be implemented, but would work like above. Could consider
  64-bit quadword, too, but large sizes seem wanted only for
  cryptogaphy functions which probably want even larger modular
  integers, maybe expressed as bitfields.

#### Numbers

An expression consisting solely of integers produces an integer of the
smallest size large enough to hold the value. (Or maybe larger, in
intermediate results?) Any float in an expression will cause all
integers to be converted to floats (generating error on overflow),
producing a float result. If modular numbers are involved, see that
section above.

- __smallint__: Signed 14-bit integer; fits into a tagged pointer. This
  would normally not be considered by the programmer as the system
  will automatically convert between these and integers as necessary.

- __integer__: Signed arbitrary-precision integer. For operations
  between two integers of different precisions, the smaller is
  sign-extended to the size of the larger. Overflow increases the size
  of the result; the size of a result will automatically be decreased
  when possible. (The actual maximum precision is 255 bytes, including
  sign, holding absolute values of >63e612; overflowing this results
  in an error.)
  - Literal: optional `+` or `-` followed by digits with no `.`.

- __float__: 8-bit exponent; arbitary precision. No infinity or NaN;
  operations that would produce these are an error. Overflow/underflow
  is an error? Literals are:
  - Optional `+` or `-`, followed by one or more digits `[0-9]` and
    then a decimal point. (This is how we recognize it's a float and
    not a integer.)
  - Zero or more digits after the decimal point.
  - optional `e` followed by optional `+` or `-` followed by digits
    for the exponent.

  A float literal will be given the minimum precision necessary to
  fully represent it. Operations between floats will produce results
  with the same precision as the highest-precision float.

#### Other

- __proc__: Executable code. Not sure about argument list
  specification; should it just take care of that (and checking of it)
  itself? Possibly need different versions for PROC vs. FPROC (the
  latter getting unevaluated arguments), and for interpreted (EXPR)
  vs. machine code (SUBR), à la LISP 1.5.

- __symbol__, __string__: Actually the same thing.
  - "Escaped chars" are `\c` combinations; see below.
  - Literal: `"…"`.
  - Literal: `'` followed by chars; any "auto-quoted" literal above is
    parsed as that type instead. Use `"…"` to create a symbol instead
    of a literal of another type. Terminated by space, `)`, maybe some
    other things (see what R²RS suggests).

- __environment__:

### Escaped Character Literals

`\` (`↓` on TRS-80, `£` on VIC) followed by a single character; any
chars not listed here generate a parse error. There are two sets.

The "double-quote" set is used with symbol/string literals using `"…"`:

    \               To escape itself
    0bfrn           The usual codes for non-printing chars.
    "               To escape closing quote.

The "quote" set is all of the above, plus

    '
    ␢               Space ("blank") character
    ()[]{}


Considerations and Alternatives
-------------------------------

### Representation

- To avoid duplicate symbols, and just for general symbol lookup, we
  need to be able to search through all symbols in memory. This
  happens only when parsing input, though. Options:
  - Search every object in the heap.
  - Add a "next" pointer to every symbol object. This could even allow
    us to keep them in sorted order, letting us shortcut a search,
    though it doesn't seem to allow binary searches even if we add a
    prev pointer as well.
  - Keep a separate binary tree index: speeds searches but adds space
    overhead and maybe "insert" time overhead. This could be optional,
    only for larger-memory systems?
  - Instead use a separate string heap. Probably would have to grow
    down from top, but seems doable. Makes GC more complex because we
    now have two heaps to collect when they collide?

- Use a [radix tree] to store the symbols?
  - How do we get a symbol name/string back from its pointer, then?
  - Probably not worth the effort; the overhead seems high for many
    short strings due to all the additional pointers, empty end nodes,
    etc.

- Add rational numbers type?

#### Keyboard Issues

Need to be careful having literals using punctuation chars from the
upper half of ASCII that are missing on popular keyboards. Perhaps we
can have control sequences enter some of these? Below, the full set
and what some popular keyboards have.

    @[\]^_`{|}~     Full set

     [ ]  `{ }~     SWTPC CT-1024 (TV Typewriter)
    @[\]↑←`         PET 2001 (calculator and typewriter)
    @  ]^           Apple II (]  on Shift-M is unmarked)
    @               TRS-80 Model I

#### Types and Literals

A basic decision to make is whether or not we want to recognize
non-symbol literals by the _initial chars_ of the literal, and
generate an error if the rest of the format is not correct. If we do
that certain strings such as `+123a` will be invalid; otherwise they
would be valid symbols. The former seems better in that it's likely to
catch programmer errors; using symbols like `12O` seems inadvisable.
(Also, the former gives us room for future expansion of parsing, such
as `1a0h` for hexadecimal, or `12cm` in a system with user-defined
unit suffixes.)

- __byte__: Other options considered for literal __char__ were:
  - `^`: Not available on TRS-80 keyboard. `↑` in PET and TRS-80 charset.
  - `&`: Looks bigger and more awkward than `:`.
  - Haven't investigated use of any of these symbols in earlier LISPs.

- __integer__: Making this a fixed size, rather than arbitrary
  precision, actually saves basically no effort since operations are
  done byte-wise, anyway. This may change if we decide to support
  vectors or arrays.

- __float__:
  - As with integers, making the mantessa a fixed size rather than
    arbitrary precision saves basically no effort. However, having
    more than one size of exponent would involve extra effort, so
    exponents are always 8 bits. (Again, this may change if we decide
    to support vectors or arrays.) It may be worth the effort of
    adding the option of 16-bit exponents at some point; there's
    probably no sense in going further than that since this is already
    considerably larger than an IEEE double-precision exponent (11
    bits).
  - Possibly we should allow dropping the decimal point if an exponent
    is supplied.
  - It's not clear on the best way to assign precision at initial
    allocation.


References
----------

#### Pre-1975

- [LISP 1.5 Programmer's Manual][lisp1.5] 2nd Ed. MIT Press, 1962. See
  §VII p.36 for internal data structures.
- David Moon, [_Maclisp Reference Manual_][moonual] revision 0.
  Project Mac, MIT. 1974-04.
- Warren Tietelman, [_Interlisp Reference Manual_][interlisp74]. Xeros
  Palo Alto Research Center. 1974. (Formerly BBN LISP; originally
  developed on PDP-1 at Bolt, Beranek and Newman in 1966.)

#### 1975-1985

- [_BYTE: LISP_ issue][byte7908]. Vol 04 No 08, August 1979.
- S Tucker Taft, ["The Design of an M6800 LISP Interpreter."][taft79]
  _BYTE_ magazine Vol 04 No 08, August
  1979. p.132.

#### Modern

- ["Memory Management Glossary"][mps-glos] from the Memory Pool System
  documentation. Ravenbrook. 1997-present. Very useful to find
  particular techniques and references from terms.
- [_Memory Management Reference_][mmr]. Site devoted to memory
  management.
- David Gries, ["Presentation of the Schorr-Waite graph marking
  algorithm"][gries2006]. 2006. GC w/o recursion. Algorithm appeared
  in 1968. Also attributed to Peter Deutsch.
- St-Amour and Feeley, ["PICOBIT: A Compact Scheme System for
  Microcontrollers"][picobit09]. Symposium on the Implementation of
  Functional Languages. 2009. Fits in 7 KB. Stack-based VM. First
  class continuations are 30 lines of Scheme compiling to 141 bytes of
  bytecode. Whole-program compilation and a treeshaker heavily
  optimize size.

#### Other Notes

[Maclisp][wp-maclisp] (1966-1980 or so), descendent of LISP 1.5:

> Maclisp began with a small, fixed number of data types: cons cell,
> atom (later termed symbol), integer, and floating-point number.
> Later additions included: arrays, which were never first-class data
> types; arbitrary-precision integers (bignums); strings; and tuples.
> All objects (except inums) were implemented as pointers, and their
> data type was determined by the block of memory into which it
> pointed, with a special case for small numbers (inums).



<!-------------------------------------------------------------------->
[aligned]: https://en.wikipedia.org/wiki/Data_structure_alignment
[radix tree]: https://en.wikipedia.org/wiki/Radix_tree
[tagged]: https://en.wikipedia.org/wiki/Tagged_pointer

<!-- Refs: Pre-1975 -->
[interlisp74]: https://archive.org/details/bitsavers_xeroxinterfMan_35779510
[lisp1.5]: http://web.cse.ohio-state.edu/~rountev.1/6341/pdf/Manual.pdf
[moonual]: https://en.wikipedia.org/wiki/David_A._Moon

<!-- Refs: 1975-1985 -->
[byte7908]: https://archive.org/details/BYTE_Vol_04-08_1979-08_Lisp
[taft79]: https://archive.org/details/BYTE_Vol_04-08_1979-08_Lisp/page/n133

<!-- Refs: Modern -->
[gries2006]: https://www.cs.cornell.edu/courses/cs312/2007fa/lectures/lec21-schorr-waite.pdf
[mmr]: https://www.memorymanagement.org
[mps-glos]: https://www.ravenbrook.com/project/mps/master/manual/html/glossary/index.html
[picobit09]: https://www.ccs.neu.edu/home/stamourv/papers/picobit.pdf

<!-- Refs: Other Notes -->
[wp-maclisp]: https://en.wikipedia.org/wiki/Maclisp

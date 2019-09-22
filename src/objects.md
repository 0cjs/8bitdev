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
- start with a heapdata header giving type and length information,
  followed object data, of arbitrary length; or
- are a cons cell of two pointer words, the _car_ followed by the
  _cdr_.

Given an arbitrary (properly aligned) address in the heap we cannot
tell if it points to a cons cell or a heapdata object because it might
point into the middle of a heapdata object; thus walking the entire
heap must be done by starting at its lowest location in memory.
(Unallocated heap elements must be initialized to "empty" cons cells
of `(nil,nil)`.)

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
    LL   tttttt 01   R  heapdata header: length LL, type tttttt (1-63)
    nn   nnnnnn 11      signed 14-bit int: -8192 to 8191

The `x` bit on pointers into the heap is available for use by the
garbage collector. However, as an alternative a separate bit array
could be allocated for this (one bit for every possible address on
the heap, even those that may be in the middle of heapdata objects),
increasing heap overhead by about 12.5%. (This would not be necessary
for read-only heap areas.) A Schorr-Wait algorithm would require two
bits.

### Heapdata Types

A heapdata object starts with a header having least significant bits
`01` with the type (1 through 63) in the most significant 6 bits of
the LSB and the length in the MSB. This is followed by the data
itself. (Type 0 is a `byte` with value in the MSB, and thus has no
additional data and is the car of a cons cell.)

To simplify determining the storage used by object, the length is
always given as the number of bytes after the header (0-255) and the
storage allocated is that rounded up to the next 2-word aligned
address. Thus it requires no knowledge of the types themselves to
determine the location of the next object after this one on the heap.
(Storing the length in longwords was also considered, allowing larger
individual objects, but then individual types that did not entirely
fill the space would need an additional length or termination bytes to
determine the actual length of their data.)

Following are the heapdata types, given as both the least significant
byte in hex (always having least significant bits set to `01`) and the
most significant six bits interpreted as a decimal number in
parentheses.

XXX These may want to be renumbered to make comparisons easier, once
we have enough of this worked out to see better ways of organizing
this.

- `$05` (1): __symbol__ (or __string__). Data is vector of _len_
  bytes, usually interpreted as ASCII characters but they may be any
  byte values. Symbols are immutable once created in order to allow
  storage in ROM.

- `$09` (2): __word__: _len_=2. Data is an unsigned 16-bit (two-byte)
  integer. Arithmetic is modular and overflow is ignored.

- `$0d` (3): __longword__: _len=4_. Data is an unsigned 32-bit
  (four-byte) integer. Arithmetic is modular and overflow is ignored.

- `$11` (4): __fixnum__: A signed integer value of arbitrary length
  (up to 255). Data is a vector of _len_ bytes, LSB to MSB, with sign
  as the highest bit of the MSB. Arithmetic sign-extends the smaller
  value.

- `$7d`,`$fd` (31,63): __flonum__: Positive and negative floating
  point numbers with mantessa of _len_-1 bytes. The first byte of data
  is the (always 8-bit) exponent (2's complement with reversed sign;
  `$80` is zero) and the remaining bytes are the mantessa MSB to LSB.
  See below for more details.

#### Floating Point Format and Representation

Floating point values always consist of an 8-bit exponent in the first
byte, followed by however many bytes of mantessa. The mantessa sign is
kept separately as part of the object type; i.e. negative and positive
mantessas are technically separate types.

The exponent is, in the usual way, offset by $80: 0 = $80, 1 = $81,
-1 = $79, etc.

The mantessa, when normalized, is assumed to have an implicit `1` bit
before it. For simplicity we may decide to disallow denormalized
mantessas (with one or more leading zeros) even though this slightly
reduces the range that can be represented by a floating point value.

The mantessa sign is kept separately as part of the type. This makes
computations easier.


Types and Literals
------------------

#### Special Constants

- __nil__
- __true__, __t__

#### Modular Numbers

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

#### Numbers

- __sfixnum__: Signed 14-bit integer; fits into a tagged pointer. This
  would normally not be considered by the programmer as the system
  will automatically convert between these and fixnums as necessary.

- __fixnum__: Signed arbitrary-precision integer. For operations
  between two integers of different precisions, the smaller is
  sign-extended to the size of the larger. Overflow increases the size
  of the result; the size of a result will automatically be decreased
  when possible. (The actual maximum precision is 255 bytes, including
  sign, holding absolute values of >63e612; overflowing this results
  in an error.)
  - Literal: optional `+` or `-` followed by digits with no `.`.

- __flonum__: 8-bit exponent; arbitary precision. No infinity or NaN;
  operations that would produce these are an error. Overflow/underflow
  is an error? Literals are:
  - Optional `+` or `-`, followed by one or more digits `[0-9]` and
    then a decimal point. (This is how we recognize it's a flonum and
    not a fixnum.)
  - Zero or more digits after the decimal point.
  - optional `e` followed by optional `+` or `-` followed by digits
    for the exponent.

  A flonum literal will be given the minimum precision necessary to
  fully represent it. Operations between flonums will produce results
  with the same precision as the highest-precision flonum.

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

#### Keyboard Issues

Need to be careful having literals using punctuation chars from the
upper half of ASCII that are missing on popular keyboards. Perhaps we
can have control sequences enter some of these? Below, the full set
and what some popular keyboards have.

    @[\]^_`{|}~     Full set

     [ ]  `{ }~     SWTPC CT-1024 (TV Typewriter)
    @[\]↑←`         PET 2001 (calculator and typewriter)
    @   ^           Apple II ( ] is on international kbd?)
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

- __fixnum__: Making this a fixed size, rather than arbitrary
  precision, actually saves basically no effort since operations are
  done byte-wise, anyway. This may change if we decide to support
  vectors or arrays.

- __flonum__:
  - As with fixnums, making the mantessa a fixed size rather than
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

- David Gries, ["Presentation of the Schorr-Waite graph marking
  algorithm"][gries2006]. 2006. GC w/o recursion. Algorithm appeared
  in 1968. Also attributed to Peter Deutsch.

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

<!-- Refs: Other Notes -->
[wp-maclisp]: https://en.wikipedia.org/wiki/Maclisp

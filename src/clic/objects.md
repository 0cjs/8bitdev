CLIC Objects and References
===========================

Document conventions:
- A _byte_ is eight bits; a _word_ is 16 bits; a _dword_ is 32 bits.
- Binary numbers are prefixed with `%`. For readability they may use
  punctuation to separate substrings of bits, e.g. `0101.1010`.
- Hexadecimal numbers are prefixed with `$`. Two digits generally reprsent
  a byte, four a word, with leading zeros where necessary.
- "MSB"/"LSB" mean most/least significant byte; "LSb"/"LSbit" means least
  significant bit.
- For print/read forms, `H` specifies a hex digit (e.g., `#pHHHH` for a
  pointer specified by four hex digits).


Representation of Object References and Data
--------------------------------------------

_Object references_ (or in short form _ref_) are 16-bit _words_ in native
byte order containing _[tagged]_ values that determine the type of the
reference. When the value of a reference is a _pointer_, it points to
either a _cons cell_ or object data _obdata_ in memory (but not necessarily
in a dynamically allocated _heap_). Otherwise the reference is _intrinsic_
(usually called "immediate" in other languages) and it alone contains all
information about the object itself. (Consts, smallints, sym1s and sym2s
are intrinsic references.)

In memory, cons cells and obdata are [aligned] to _dword_ (32-bit or
4-byte) addresses. They may be stored anywhere in the full address
space except for the first page (MSB=$00, address=$00nn). The storage
may be part of a dynamically allocated and freed _heap_ or may be static
data, possibly in ROM.

A cons cell is fixed size and consists of two references (words),
a _car_ followed by a _cdr_.

Obdata is variable length and starts with a header giving format and
length information, followed by further data that varies depending on
the obdata type and format. (A single object type may have multiple
storage formats.)

### Reference and Data Types and Tagging

The two least significant bits (LSbs) and in some cases the most
significant byte (MSB) of a reference, or the first two bytes of obdata,
determine the type.

     MSB  LSbs  Type
     $00  %00   'const'; type and value determined by bits 7-2
    ≠$00  %00   'pointer': to a cons cell or object data
     any  %01   'smallint': 14-bit signed integer
     any  %10   'sym1' or 'sym2'
     any  %11   'obdata' header; never an object reference

Notes:
- Because const (MS=$00 LSbs=%00) shares the format of pointer, addresses
  the lowest 256 memory locations ($00nn) cannot be used for object data
  storage. Most 8-bit processors have other more important uses for this
  page anyway (zero page for 6800/6502; interrupt vectors for 8080).
- A pointer may point to either a cons cell or obdata; the type of the
  pointer's target is determined by whether or not the first two bytes of
  the target are tagged as an obdata header.
- smallint has tag %01 for easier arithmetic; see the details below.

### Tag Format and Reference Data Types

The following table summarizes the details of tagging and determining
values. The most significant byte is given in hexadecimal; the least
significant byte in binary, with a separator before the two least
significant bits. `x` represents a don't-care bit, but see below.
Objects marked `R` may contain further references and must be
recursively followed by the GC.

    MSB   LSbits    R  Description
    00   000000-00     #n (Nil)
    00   000001-00     #t (True)
    00   110011-00     $CC = free cell: mnemonic 'clear cell'
    00   ??????-00     other consts; see below
    AA   aaaaaa-00  R  (AA≠00) pointer to object, address AAaaaaaa00.
    NN   nnnnnn-01     smallint: -8192 to 8191
    cc   100000-10     sym1 (1-char symbol)
    BB   bbbbbb-10     sym2 (2-char symbol)
    LL   ffffff-11  R  obdata header: length LL, format number ffffff


Object Reference Details
------------------------

All references can be printed and read as `#rHHHH`. This is not usually
done as all output routines know more specific forms, but can be useful for
debugging output and on input when doing systems hacking.

(XXX The places where we accept `#rHHHH` need to be thought out carefully
since misuse of this can result in quite random behaviour.)

### Const

Consts are typically printed a form specified for that particular constant,
e.g., `#n` for $0000 (nil) or `#t` for $0004 (true). Consts without a
specified form are printed as `#cHH`. `#cHH` is never accepted as input
(because we don't know what to do with one that has incorrect tag bits);
instead `#rHHHH` would be used.

There are 64 _const_ values available: $00, $04, $08, …, $FC. The lower 32
(LSB MSbit clear) are user-visible and generally have a `#…`
representation. The upper 32 (MSbit set) are for internal use and have no
user-visible representation, though debug print routines will give `#cHH`.

The defined user consts are (with reader and assembly language names):

- $00 `#n` `C_NIL`: 'Nil', empty list.
- $04 `#t` `C_TRUE`: True.

The defined system consts are:

- $CC `C_FREE`: Free cons cell. Mnemonic for hex dumps: 'clear cell.'

### Pointer

Printed as `#pHHHH`. This is used when pointers aren't being followed, but
typical output will follow the pointers instead. (E.g., `(a (b 3) 4)`
instead of `(a #p10AB 4)`.) Never read (because we don't know what to do
with one that has incorrect tag bits); `#rHHHH` would be used instead.

Pointers may point to any 4-byte-aligned address in memory. There is no
assumption about whether they point into a heap (see below), or a heap of
any particular kind (code following a pointer must be prepared to handle
obdata even in a "cons heap"). It's typical for pointers to point into
pre-defined data in ROM.

### Smallint

A smallint is a two's complement signed 14-bit value (range decimal -8192
to 8191) stored shifted left two bits: bits 13-6 in the MSB and bits 5-0 in
the LSB bits 7-2, followed by the two tag bits.

Because the tag bits are %01, this allows you to do additions and
subtractions of smallints with no preprocessing of the values.
- After addition the tag bits become %10;
  correct with `DEC` (or `OR #$01`, `AND $FD`).
- After subtraction the tag bits become %00;
  correct with `INC` (or `OR #$01`).

     ────────── LSB ──────────     ────────── MSB ──────────
    | 05 04 03 02 01 00  ₀  ₁ |   | 13 12 11 10 09 08 07 06 |

### Sym1/sym2

A sym1 or sym2 is a 1- or 2-character symbol packed into a tagged
reference. The two forms are:
- sym1: LSB = $82. Symbol of one eight bit character.
- sym2: LSB ≠ $82. Symbol of two seven bit characters.
- Using $82 as the sentinel means that the second char of a sym2 may not be
  space or backtick: those sym2 values cannot be distinguished from a sym1
  value. (These were picked as the pair of least-used chars.)

Below, `c7`-`c0` are the bits of the character of a sym1, and `c6`-`c0` and
`d6`-`d0` are the bits of the first and second characters of a sym2.

                LSB                           MSB
    |  7  6  5  4  3  2  1  0 |   |  7  6  5  4  3  2  1  0 |
    ---------------------------------------------------------
    |  1  0  0  0  0  0  1  0 |   | c7 c6 c5 c4 c3 c2 c1 c0 |  sym1
    | d5 d4 d3 d2 d1 d0  1  0 |   | d6 c6 c5 c4 c3 c2 c1 c0 |  sym2

A two-character symbol that contains disallowed chars must be stored as an
obdata symbol referenced by a standard pointer to it.

If necessary, this can be extended to store a separate 'char' data type as
well: use LSB = $02 for that which would add NUL and `@` as invalid second
chars. (Other possibilities are `[\]^_` and their corresponding control
characters or `?` and DEL.)


Heaps
-----

Though pointers may point to cons cells or obdata (almost) anywhere in
memory, typically a system will have one or more _heap_ areas in which
cons cells and obdata are dynamically allocated.

Unlike arbitrary areas of memory, every address in a heap is part of an
object. Space available for allocation in mixed and obdata heaps is
indicated by "free space" obdata objects (format `FBO`, see below).

All objects on the heap have an allocation size or _asize_, given in
bytes, that is a multiple of four and 256 bytes or less. The next
object is located at the address of the current object plus its asize.

Cons cells always are two words in size, thus always having an asize
of 4 bytes.

Obdata values (described in detail below) may have an _odsize_ that is not a
multiple of four bytes; in a heap they will always be padded out to have an
asize that's a multiple of 4. (This may not be the case for obdata values
stored outside of a heap where the immediately following unaligned bytes
may be used for other purposes.) The asize can always be determined from
the odsize by rounding odsize+2 (for the header) up to the next dword
boundary. A formula for this is `(odsize+5) ∧ $FC`.

Because obdata values have variable size, given an arbitrary (but
properly aligned) address in a heap we cannot tell if it points to an
object or not. Thus walking the entire heap must be done by starting
at its lowest location in memory or at a known-good pointer to an
object.

### Alternative Heaps

Described above is a single heap that mixes fixed-length cons cells and
variable-length obdata blocks. The following variations could be
investigated.

__Split heap:__ this is effectively two heaps of variable size with cons
cells in the top half and obdata in the bottom half. Each grows towards the
other and is GC'd separately. This should make allocation more efficient.

This does not entirely remove the need for separate tags to distinguish
obdata blocks from cons cells since either may be outside one of these
heaps (e.g. in ROM or a static "core" interpreter area). However it does
make the tag bits redundant within the obdata heap (though not the cons
cell heap); see below for how this might help GC.

Using separate heaps for cons cells and obdata values may speed up
allocation and GC because the former heap would contain only one size of
object (dword), thus lengths never need be read and that heap doesn't need
regular compaction if it maintains a free list. (This might be done with a
const in the car and pointer to next free entry in the cdr.) But note the
heap does need to be compacted before a load from external media. (And
probably save as well, for a compact save.)

__Tiny Heap__ for very small memory systems:
- This is intended to compete feature-wise with 4K BASICs.
- If necessary, restrict pointers to 32 KB (or even 16 KB?), freeing up the
  top bit to mark object header tags.
- Make all heap objects four bytes asize and remove length byte (length
  would be implicit in obdata type).
- Pare down the number of data types, possibly even having only FP or
  integer, not both.
- "Bigints" would be replaced by fixed 24 bit integers.
- Floating point is 24 bits; exponent/significand options could be 8/16
  (±127/4.8 digits), 6/18 (±32/5.4 digits), 5/19 (±16/5.7 digits), even
  4/20 (ٍ±8/6 digits).
- Symbols are limited to ASCII numeric/punctuation and one case of alpha
  sticks; symbols of up to 4 chars packed as 4×6-bit in 24 bits.
  Alternatively, limit symbols to two 7-bit chars each and all will be
  "packed" sym1 or sym2 references.

__Cons Heap Only__ for extremely small systems:
- Symbols limited to two letters; numbers limited to smallints.
- Possibly need to reconsider how we do environments.
- Unclear where/how we put machine code objects. (Const in car, pointer to
  special data structure in cdr?)

### Garbage Collection

Read-only data outside of heaps (e.g., ROM, the static core interpreter
loaded from tape or disk) do not need to be collected. (They cannot be
removed themselves, nor can they refer to data in dynamically allocated
heaps.)

If a heap can contain all object types, there is currently no room in the
heap object format for mark bits. Possibly a separate bit array could be
allocated for this: one bit for every possible object address on the heap,
even those that may be in the middle of obdata objects. This would increase
heap overhead by 1/(4× 8) = 3.125%. (Double that for a Schorr-Waite
algorithm requiring two bits.) It's also theoretically necessary only
during collection; one might re-use an input buffer for this.

If split heaps for cons cell and obdata are used, the obdata heap contains
only obdata objects (tag %11) and so the tag becomes redundant for those
objects within the heap, freeing the two bits to be borrowed during GC as
mark bits. (During such a GC nothing else may touch or follow anything in
that heap unless it also can ignore the tag bits.)

However, freeing up just the %11 tag does not help for the cons cell heap
because it frees up just one code point, only log₂(4/3) ≈ 0.4 bit of
information.


Obdata Types and Formats
------------------------

An obdata value always starts with a two-byte _obdata header_.

The LSB of the header describes the format. It always has its two LSbits
(the tag) set to `%11`. The upper six bits are the _format number_ (ranging
from 0-63); when shifted left two bits with the lowest two bits set to the
required `%11` this whole byte is referred to as the _format ID_.

The MSB contains the _odsize_ indicating the length of data following the
two-byte header. The odsize has no alignment restrictions, and so when
stored within a heap there may be padding at the end of the obdata value to
align the next object to a 4-byte boundary (as described in the "Heaps"
section above).

        byte || -------LSB------- || ------MSB------ ||
         bit || 7 6 5 4 3 2 | 1 0 || 7 6 5 4 3 2 1 0 ||
    contents || format num. | 1 1 ||     odsize      ||
             ||     format ID     ||                 ||

(Storing the odsize in dwords rather than bytes was also considered,
allowing larger individual objects, but then individual formats that
did not entirely fill the space would need additional length or
termination bytes to determine the actual length of their data.)

### Obdata Formats

Note that these are "formats" rather than types: some data types (e.g.
symbol, float) have multiple formats for storage as obdata values.

Format summary:

                  ID: format ID in hexadecimal
              format: format number (ID bits 7-2) in binary
                 num: format number in decimal
                 asz: asize (allocation size) on heap, if fixed
                 len: length, if fixed

     ID   format num  asz len  description
    $03  0000-00   0           free block object (FBO)
    $0B  0000-10   2   8   6   env-header
    $0F  0000-11   3   8   6   env-entry
    $23  0010-00   8           symbol (string)
    $27  0010-01   9   8   4   symbol substring
    $63  0110-00  24           integer
    $6B  0110-10  26           float, positive mantissa
    $7B  0111-10  30   4   2   word (16-bit unsigned int, modular arithmetic)
    $7F  0111-11  31   8   4   dword (32-bit unsigned int, modular arithmetic)
    $EB  1110-10  58           float, negative mantissa

    Bit assignments (type byte/format number):
      7 / 5     Sign bit: floats, ...
      6 / 4     Number, including modular
      5 / 3     Atomic (?)

Format details:

- __free block__: The header and the next _len_ bytes (always even,
  and always two less than a multiple of four) are space available to
  be allocated. _len_ ranges from $02 (4 bytes available) to $FE (256
  bytes available).

- __env-header__: _len=6_. The header record for an environment. The
  data are as follows. All pointers may be `nil` for no value.
  - Pointer to first _env-entry_
  - Pointer to parent environment _env-header_
  - Pointer to symbol for environment name

- __env-entry__: _len=6_. An entry in an environment. The data are
  three pointers to the entry's symbol (name), entry's value, and next
  entry in the environment.

- __symbol__ (or __string__). Data are vector of _len_ bytes, usually
  interpreted as ASCII characters but they may be any byte values
  (including $00). Symbols are immutable once created in order to allow
  storage in ROM. Generally symbols would be unique, with new symbols being
  intern'd to maintain uniqueness. (But strings should not be intern'd? And
  also they should self-evaluate: symbols should not.)

- __symbol__ substring: _len=4_. Data are a pointer to a symbol, start
  point and length. Start point (0-based) plus length must not extend
  past the end of the data of the symbol this references. Not sure yet
  if this could also reference another substring. This is intended to
  make substring operations, particularly recursive `(car somesym)`
  more efficient, but we need to look at ways of turning these into
  symbols (and dealing with their references, if they exist) so that
  the original symbol can be GC'd if it's not directly referenced and
  much of it is no longer needed.

- __word__; __dword__: _len_=2; _len=4_. Data are unsigned 16-bit
  resp. 32-bit integers. Arithmetic is modular and overflow is ignored.

- __integer__: A signed integer value of arbitrary length (up to 255
  bytes). Data is a vector of _len_ bytes, LSB to MSB, with sign as
  the highest bit of the MSB. Arithmetic sign-extends the smaller
  value.

- __float__: Positive and negative floating point numbers with
  mantissa of _len_-1 bytes. (Storing the mantissa sign outside of the
  mantissa itself makes calculations easier.) The first byte of data
  is the (always 8-bit) exponent (2's complement with reversed sign;
  `$80` is zero) and the remaining bytes are the mantissa MSB to LSB.
  See below for more details.

#### Floating Point Format and Representation

Floating point values always consist of an 8-bit exponent in the first
byte, followed by however many bytes of mantissa. Negative and
positive numbers are separate obdata formats; keeping the mantissa's
sign separate from the mantissa itself makes calculations easier. The
sign can be determined from the high bit (bit 7) of the format ID.

The exponent is, in the usual way, offset by $80: 0 = $80, 1 = $81,
-1 = $79, etc.

The mantissa, when normalized, is assumed to have an implicit `1` bit
before it. For simplicity we may decide to disallow denormalized
mantissa (with one or more leading zeros) even though this slightly
reduces the range that can be represented by a floating point value.


Types and Literals
------------------

#### Modular Numbers

Whenever a modular number is involved in an expression, the result is
always a modular number of the largest size involved; smaller sizes
are sign-extended. Integers are converted to a sign-extended modular
number of the smallest size able to hold the value and its sign bit,
or an overflow error is generated. Floats cannot be converted and
always generate an error. This is intended to make it easy to do
indexed addressing, e.g., `(+ $FF00 2)`.

- __byte__ (__char__): Unsigned 8-bit value; modular arithmetic.
  - OBSOLETE: sym1 now covers this, though we should still consider,
    the following notation for literals which should be added to that
    already in `Langauge.md`. §"Characters" if we decide to use it.
  - Literal: `$xx` where _xx_ is a one- or two-digit hexadecimal value
  - Literal: `%n` where _n_ is a 1-8 digit binary value.
  - Uses: character; data for examine/deposit.

- __word__: Unsigned 16-bit value; modular arithmetic.
  - Literal: `$xxxx` where _xxxx_ is four hex digits (one alternative).
  - Literal: `$$n` where _n_ is a 1-4 hex digits (other alternative).
  - Literal: `%n.n` for high/low bytes where _n_ is 1-8 binary digits.
  - Uses: addresses for examine/deposit.

- __dword__: Unsigned 32-bit value; modular arithmetic. Probably won't
  be implemented, but would work like above. Could consider 64-bit
  _quadword_ , too, but large sizes seem wanted only for cryptographic
  functions which probably want even larger modular integers, maybe
  expressed as bitfields.

#### Numbers

An expression consisting solely of integers produces an integer of the
smallest size large enough to hold the value. (Or maybe larger, in
intermediate results?) Any float in an expression will cause all
integers to be converted to floats (generating error on overflow),
producing a float result. If modular numbers are involved, see that
section above.

- __smallint__: Signed 14-bit integer; fits into a tagged pointer.
  These would normally not be considered by the programmer as the
  system will automatically convert between these and integers as
  necessary.

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
  - "Escaped chars" in literals are `\c` combinations; see below.
  - Literal: `"…"`.
  - Literal: `'` followed by chars; any "auto-quoted" literal above is
    parsed as that type instead. Use `"…"` to create a symbol instead
    of a literal of another type. Terminated by space, `)`, maybe some
    other things (see what R²RS suggests).

- __environment__:


Considerations and Alternatives
-------------------------------

### Representation

- Consider changing the "meaning bits" of the obdata type bytes to
  put the most important distinguishers in bits 7 and 6, because
  testing these comes "for free" when testing a third or more bits
  with the `BIT` instruction. (N=bit 7, V=bit 6, Z=all bits tested
  with the operand are zero.)

- Making the smallint tag just `1` in the LSbit (i.e., smallints use tags
  `%00` and `%01`) would allow them to be 15 bits instead of 14, expanding
  their range to -16384 to +16383.

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

#### Types

- __integer__: Making this a fixed size, rather than arbitrary
  precision, actually saves basically no effort since operations are
  done byte-wise, anyway. This may change if we decide to support
  vectors or arrays.

- __float__:
  - As with integers, making the mantissa a fixed size rather than
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

- ["Memory Management Glossary"][mps-glos] ([archived version][mps-glos-ar])
  from the Memory Pool System documentation. Ravenbrook. 1997-present. Very
  useful to find particular techniques and references from terms.
- [_Memory Management Reference_][mmr]. Site devoted to memory management.
- David Gries, ["Presentation of the Schorr-Waite graph marking
  algorithm"][gries2006]. 2006. GC w/o recursion. Algorithm appeared in
  1968. Also attributed to Peter Deutsch.
- St-Amour and Feeley, ["PICOBIT: A Compact Scheme System for
  Microcontrollers"][picobit09]. Symposium on the Implementation of
  Functional Languages. 2009. Fits in 7 KB. Stack-based VM. First class
  continuations are 30 lines of Scheme compiling to 141 bytes of bytecode.
  Whole-program compilation and a treeshaker heavily optimize size.

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
[mps-glos-ar]: https://web.archive.org/web/20211026061328/https://www.ravenbrook.com/project/mps/master/manual/html/glossary/index.html
[picobit09]: https://www.ccs.neu.edu/home/stamourv/papers/picobit.pdf

<!-- Refs: Other Notes -->
[wp-maclisp]: https://en.wikipedia.org/wiki/Maclisp

Objects for a Small Language
============================

This is just kicking around some ideas for the data types one would
want for a small language to run on an 8-bit microprocessor system.

Representation
--------------

Objects are allocated on the heap with both address and size [aligned]
to a word (two byte) boundry. Pointers are 16 bits but are _[tagged]_
so that some of their values instead represent type/length information
about the object in the following data or small numbers.

Values with the least significant bit clear are always pointers into
the heap. Values with the least siginificant bit set are one of three
types: an unsigned byte (or char), a small (14-bit) signed integer, or
a type and length information for the object, with the objects data
following it.

An exception is heap pointers pointing to one of the first few
addreses in memory: these are not actually stored in memory but
represent specific constant values (nil, true, etc.). This causes no
real issues since all 8-bit processors have a special use for the
lowest bytes of memory, anyway (zero page for 6800 and 6502, vectors
for the 8080).

    MSB LSB (binary)    Description
    00   000000 00      nil
    00   000001 00      true
    00   ?????? 00      (other special values?)
    AA   aaaaaa a0      pointer into heap (except special values above)
    NN   000000 01      byte/char (unsigned) value NN
    LL   tttttt 01      heap object header: length LL, type tttttt (1-63)
    nn   nnnnnn 11      signed 14-bit int: -8192 to 8191

The objects themselves do not include any bits for GC marking. These
are stored as a separate array for each heap area both because they're
not necessary for ROM heaps and because adding them to the objects
themselves would force adding another byte (word, when alignment is
taken into account) to each heap entry or reducing the pointer size.

### Considerations and Potential Adjustments

- It may make sense to align heap entries to 4 bytes rather than two.
  This would:
  - Free a bit to use for GC marking, thus saving 32 bytes (256 bits)
    per 256-byte page during GC. >11% space savings!
  - Int32 6→8 bytes, +33%. But maybe should be using bignum after 16 bits?
  - Strings now waste avg. 1.5 bytes instead of avg. 0.5.
  - Floating point probably wastes no space at all since len/type(2) +
    exp(1) + mantessa(4) (IEEE single prec.) = 7. If we go with
    9-digit instead of 7-digit precision (like MS BASIC) we waste
    nothing at all.

- Use a [radix tree] to store the symbols?
  - How do we get a symbol name/string back from its pointer, then?
  - Probably not worth the effort; the overhead seems high for many
    short strings due to all the additional pointers, empty end nodes,
    etc.

- Use words instead of bytes for the object length? This would allow
  us to have objects longer than 255 bytes, but then we'd need a
  terminator on strings, etc. Not worth it.

### Floating Point Format and Representation

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


Types and Literals
------------------

#### Keyboard Issues

Need to be careful having literals using punctuation chars from the
upper half of ASCII that are missing on popular keyboards. Perhaps we
can have control sequences enter some of these? Below, the full set
and what some popular keyboards have.

    @[\]^_`{|}~     Full set

     [ ]  `{ }~     SWTPC CT-1024 (TV Typewriter)
    @[\]^_`         PET 2001 (chicklet&typewriter) (↑=^ ←=_)
    @   ^           Apple II ( ] is on international kbd?)
    @               TRS-80 Model I

#### Modular (Unsigned) Integers

- __byte8__: Unsigned 8-bit value; modular arithmetic.
  - Literal: `$xx` where _xx_ is a one- or two-digit hexadecimal value
  - Literal: `%n` where _n_ is a 1-8 digit binary value.
  - Uses: data for examine/deposit.

- __char__: Unsigned 8-bit value. Different from byte8? Probably does
  not need to be if it's separate from the string type. Literals:
  - Not sure yet. Want to avoid `'`; we need that for quoting atoms.
    Maybe `^` or `:` or `&`

- __byte16__: Unsigned 16-bit value; modular arithmetic.
  - Literal: `$xxxx` where _xxxx_ is four hex digits (one alternative).
  - Literal: `$$n` where _n_ is a 1-4 hex digits (other alternative).
  - Literal: `%n.n` for high/low bytes where _n_ is 1-8 binary digits.
  - Uses: addresses for examine/deposit.

#### Signed Integers

- __smallint__: Signed value that fits into a tagged pointer.
  14 bits, `-8192` to `8191`.
- __int8__: Signed 8-bit value; grows to a larger type on arithemtic
  overflow. Literals are `-128` to `127`.
- __int16__: Signed 15-bit value; grows to a larger type on arithemtic
  overflow. Literals are `-16384` to `-129` and `128` to `16383`.
- __int32__: Signed 32-bit value. Not sure what to do about overflow:
  Error? Convert to floating point? Convert to bigint (if we have it)?

Potentially it's actually easier to replace all of the above (except
__smallint__) with an arbitrary-length __bigint__, since the addition
routines are a similar amount of work anyway.

#### Other

- __float__: See above for size. No infinity or NaN; operations that
  would produce these are an error. Overflow/underflow is an error?
  Literals are:
  - Optional `-`, followed by one or more digits `[0-9]`.
  - Required decimal point `.` (this is how we recognize it's an FP
    not an int)
  - Zero or more digits after the decimal point.
  - optional `e` followed by a negative or positive int for the
    exponent.

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

- __nil__, __true__: Special values.

- __environment__:

#### Escaped Character Literals

Backslash followed by a single character; any chars not listed here
generate a parse error. There are two sets.

The "double-quote" set is used with symbol/string literals using `"…"`:

    \               To escape itself
    0bfrn           The usual codes for non-printing chars.
    "               To escape closing quote.

The "quote" set is all of the above, plus

    '
    (space)
    ()[]{}


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

<!-- Refs: pre-1975 -->
[interlisp74]: https://archive.org/details/bitsavers_xeroxinterfMan_35779510
[lisp1.5]: http://web.cse.ohio-state.edu/~rountev.1/6341/pdf/Manual.pdf
[moonual]: https://en.wikipedia.org/wiki/David_A._Moon

<!-- Refs: 1975-1985 -->
[byte7908]: https://archive.org/details/BYTE_Vol_04-08_1979-08_Lisp
[taft79]: https://archive.org/details/BYTE_Vol_04-08_1979-08_Lisp/page/n133

<!-- Refs: Other Notes -->
[wp-maclisp]: https://en.wikipedia.org/wiki/Maclisp

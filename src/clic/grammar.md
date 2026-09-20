CLIC Grammar
============

Below the CLIC grammar you will find notes and references on how
[Scheme][R⁵RS] and [Common Lisp][cl] parse input.

CLIC
----

CLIC works internally in full 8-bit characters ($00–$7F ASCII and $80–$FF
machine-specific) with case-sensitive (CS) symbols and characters. Use on
case-insensitive (CI) systems (typically ones that support upper case only)
is [handled through the console drivers][`console.md`] that use an input
prefix character, alternate display modes and/or character substitutions to
allow both input and output of the full character set.

### The Reader

### General Notes

We are currently leaning toward the CL way of doing things: read and store
an entire token (which uses a little bit of memory, but no more than a
dozen or two bytes in most cases), determine if it's a valid format for a
number, and only then do the conversion. Unlike Scheme, where something
that starts out like a number fails to parse if it isn't one, we allow
tokens like `1+` or `30cm` and interpret them as symbols. This leaves
numeric parsing failures to be just overflows, it seems.

This gives us the following general parsing procedure:
1. Tokenizer (`rtok`): reads a token typed into a buffer.
2. Token parse (`qtok`): parses token buffer to an [object].
3. Form read (`rform`): repeatedly calls the above to read and parse tokens
   and generate the AST, storing it in the heap.
4. Something calls `rform`, gets back a pointer to the AST, and evals that
   in a given environment.

#### Tokenization

(XXX not all this is implemented yet.)

A token is read into a buffer until it is complete. Basic editing
(backspace, cancel entire token) will be made available at some point.
(How to deal with backing up further than the current token is TBD.)

The buffer space is of unspecified size (it may grow for large input) but
finite: on reaching the limit the tokenizer will beep and refuse further
input. The line editing facilities may be used to back up and change the
entry.

Token reading follows these rules:
- NUL is ignored everywhere, even mid-token.
- Whitespace is TAB, LF, VT, FF, CR and SPACE.
- All leading whitespace is read and discarded.
- `()` is a token standing for `#n` (nil).
  No whitespace is allowed between the opening and closing paren.
- `(` is a single token indicating the start of a form.
- `)` is a single token indicating the end of a form.
- `'` is a single token indicating a `(quote …)`. (Note that this is not a
  terminator below; `'` can be part of a token after the first char.)
- Any other character starts a token that continues with all subsequent
  characters until a termination character: whitespace, `(`, `)`.

The following are not dealt with yet, in particular because they don't
appear in tiny CLIC:
- Double-quoted (`"…"`) strings and the escape chars inside them.
- EOF.

XXX We don't mention comments (probably a large CLIC-only feature) here.
Traditional Lisp comments would usually be discarded by the tokenizer,
which is usless to us because we type in at the console and save the AST;
we have no source files. Consider:
- Docstrings (CL): `(df (f x) "x←x+1" (+ x 1))`, easily skipped on
  evaluating a function.
- Inline objects (Interlisp): `(+ 1 2 (# "comment") 3)`. More work to skip
  in various places and doesn't work in quoted lists.

#### Self-evaluating Objects

Numbers e.g. `12` are _self-evaluating:_ they do not need to be quoted.
Compare:

    (cons  12 '())
    (cons '12 '())
    (cons   x '())
    (cons  'x '())

#### Numbers

It would be interesting to take tokens like `30cm` and rewrite them as `(cm
30)`, giving a nice "units" functionality, but we need to investigate what
happens there when letters become a valid part of numbers. Consider
`314e-2`, etc.; how is `123e` interpreted? Might we even use the "extract
and apply a symbol" idea for this, turning `1.23e4` into `(e 1.23 4)`? What
kinds of symbol names do we disallow when we do this? Do we want to
disallow e.g. `2nd` as a function name? Is that getting more Scheme-like?

Note that the above doesn't work for things like hex input: `01ABx` would
be split into `01` and `ABx`. We're intending to use `$01AB`/`$0A` for
machine words/bytes (which are different from smallints and bigints), but
it would be nice to be able to enter smallints and bigints in hex and
binary as well.

#### Characters

Probably want to use the `#\c` syntax used by both CL and Scheme (giving a
sym1 if we have no real chars), but that's definitely heading towards
making `#` special, since we don't have two-char lookahead.

#### NIL vs. () vs. '()

Scheme has no `nil`, and `()` is not self-evaluating (self-quoting); you
must use `'()`. (And remember that `#f` is separate from these, `'()` is
true in a boolean context.) In CL `NIL`, `()` and `'()` are all equivalent.

In Scheme there's nothing structural to stop `()` from producing an empty
list when evaluated and in fact MIT scheme accepts this. Probably the
standards folks just thought it's not worth the extra parsing effort?

What do we want to do? Clearly `()` and the like is going to require some
special work from the tokenizer, and perhaps different work for
`'()`/`(quote ()`. (If we even have the `quote` macro--is it needed?)

#### Upper vs. Lower Case

Scheme symbols are case-insensitive. This seems awkward. CL symbols are
entirely upper-case (at least in the standard library). CL deals with this
by making the default [_readtable_][cl:readtable] case attribute to
`:upcase` and [`*print-case*`] to `:downcase`. Both these affect only
symbols.

Our situation is different. Like CL we'd like to have case, but go with
lower-case for everything by default. And we need to deal with systems that
cannot print lower case, so for string output we need to convert to upper
case on those. (Maybe print with the upper-case escapes, e.g., `"Hello"` →
`"\HELLO"`?.)

#### Miscellaneous

CL does not appear to allow variables ending in `'`, e.g., `f'`, maybe
because `'` is a terminating macro char? Scheme does. Let's allow this in
CLIC? Need to examine the Scheme identifier parsing on this. (Is CL `'`
terminating so you can say e.g. `(f ('a))`? I think not )


Scheme
------

References:
- Scheme: An Interpreter for the Extended Lambada Calculus [[R⁰RS]]
  (MIT AIM-349), 1975.
- Revised⁵ Report on the Algorithmic Language Scheme: [[R⁵RS]], 1998.

Naming conventions:
- `'()`, `#f`, `#t`. No `nil`. `'()` = empty list is truthy.
- `…?` predicates; `…!` mutators; `…->…` conversions.

Notes:
- Symbols are case-insensitive.
- Token delimters are just whitespace and `()"`.
- Symbols cannot start with chars that can start a number, excepting the
  symbols `+`, `-`, `...` (and `.` where valid). Valid symbol initial chars
  are letters and `!$%&*/:<=>?^_~`.
- `()` is not a valid expression (unlike many other Lisps).

The full list of uses of `#` parsing is:
- `#t`, `#f`: true and false.
- `#\x`: character constant _x_.
- `#(`: introduces vector constant terminated by `)`.
- `#b`, `#d`, `#o`, `#x`: binary, decimal, octal, hex.
- `#e`, `#i`: exact, inexact numbers.

#### Types

Each object satisfies no more than one of these predicates: `boolean?`,
`symbol?`, `char?`, `vector?`, `procedure?`, `pair?`, `number?`, `string?`,
`port?`. Empty list is a separate type that satisfies none of these.

But any type can be used as a boolean; all are true except `#f` (including
the empty list, `'()`.)

Objects may be immutable; it's an error to `set!` etc. these.

Character constants are `\#x` where _x_ (CS) is a printable character or
space (must be followed by a delimiter), or `\#name` where _name_ (CI) is
e.g. `space`, `newline`, etc.


Common Lisp
-----------

References:
- [Common LISP Specification][cl], 1994.
  - [§2 Syntax][cl§2], 1994.

Naming conventions:
- `nil`, `t`. (`()` and `'()` are also `nil`.)

The Common Lisp _reader_ reads a single character and then dispaches on its
_syntax type._ [cl§2.1.4] "Character Syntax"; [cl§2.2] "Reader Algorithm."

- _Invalid._ Error.
- _Whitespace:_ "newline", TAB, LF, VT, CR, space.
  Character is discarded; reader restarts.
- _Macro character:_ `#` non-terminating. `"'(),;` and backtick terminating.
  Associated macro function called; see below.
- _Single escape:_ `\` (preserves case of next char).
  Next char _c_ read; EOF is error. _c_ treated as a consituent and
  used to start a token.
- _Multiple escape:_ `|` (start/end of group of case-preserved chars).
  Starts a token.
- _Constituent:_ BS, DEL, `$%&*+-./:<=>@^_~`, `0-9A-Za-z`. `!?[]{}`✱.
  Starts a token.

Consituent characters additionaly have traits: alphabetic, digit, package
marker, plus sign, minus sign, dot, decimal point, ratio marker, exponent
marker, and invalid. Additionally some are _alphadigit,_ meaning digit if
the current input base is higher than the charactedr's value, otherwise
alphabetic.

> Whitespace characters serve as separators but are otherwise ignored.
> Constituent and escape characters are accumulated to make a token, which is
> then interpreted as a number or symbol. Macro characters trigger the
> invocation of functions (possibly user-supplied) that can perform arbitrary
> parsing actions. Macro characters are divided into two kinds, terminating
> and non-terminating, depending on whether or not they terminate a token.

Each macro character has an associated function, called by the reader on
encountering it, which returns the parsed object or nothing if the
following text is ignored. Non-terminating macro chars in the middle of a
token are not treated specially; terminating macro chars terminate the
token.

The [list of `#` parsers][cl§2.4.8] is large.
- Control chars are generally errors
- `#` followed by `!?[]{}`: all reserved for the user.
- `#(`: simple vector; `#*`: bit vector; `#a`: array.
- `#|`: balanced comment.
- `#c`: complex number.
- `#b`, `#o`, `#x`: binary, octal, hex.
- `#Nr`: radix _n_ number.
- `#s`: structure
- A bunch more.

#### Case in Common Lisp

In CL function names are case-sensitive, and the standard library names are
all upper-case. The [_readtable_][cl:readtable] has a case attribute that
can be set to `:upcase` (default), `:downcase`, `:preserve` or `:invert`.
[cl§23.1.2]. The default converts all symbol text to upper case except for
things that are escaped (i.e., `foo` → `FOO`, but `|foo|` → `foo`).

This also affects printing, along with [`*print-case*`], and in a somewhat
complex way. [cl§22.1.3.3.2] "Effect of Readtable Case on the Lisp
Printer."

Maybe we want to do something like this but in the other direction on
systems without lower-case input and/or output. (But what about those with
charsets actually missing lower-case characters?)

#### Types

Character constants are `\#x` where _x_ (CS) is a printable character or
space (macro chars ok) , or `\#name` where _name_ is `Space`, `Newline`,
(always supported), `Page` etc. (optional).


Other References
----------------

* McCarthy, ["History of Lisp"][mac79], 1979-02-12.  
  Information about early development of the initial key ideas (1956-58)
  and the first language implementation (1958-62).

* Steele, Gabriel, [The evolution of Lisp][ste96a].  
  Implementations and hardware. Specific langauge features.  
  Above link is uncut version; a slightly shorter version [[ste96b]] was
  published in a book derived from HOPL II.

* CHM Software Preservation Group, [History of Lisp][chm], ongoing.
  Web pages covering many specific Lisp systems in detail, including
  links to many papers and source code.



<!-------------------------------------------------------------------->
[`console.md`]: ./console.md
[object]: ./objects.md

<!-- Scheme -->
[R⁰RS]: https://dspace.mit.edu/bitstream/handle/1721.1/5794/AIM-349.pdf
[R⁰RS]: https://standards.scheme.org/official/r0rs.pdf
[R⁵RS]: https://standards.scheme.org/official/r5rs.pdf

<!-- Common Lisp -->
[`*print-case*`]: https://novaspec.org/cl/v_print-case
[cl:readtable]: https://novaspec.org/cl/t_readtable
[cl]: https://novaspec.org/cl
[cl§2.1.4]: https://novaspec.org/cl/2_1_Character_Syntax#sec_2_1_4
[cl§2.2]: https://novaspec.org/cl/2_2_Reader_Algorithm
[cl§2.4.8]: https://novaspec.org/cl/2_4_Standard_Macro_Characters#sec_2_4_8
[cl§22.1.3.3.2]: https://novaspec.org/cl/22_1_The_Lisp_Printer#sec_22_1_3_3_2
[cl§23.1.2]: https://novaspec.org/cl/23_1_Reader_Concepts#sec_23_1_2
[cl§2]: https://novaspec.org/cl/2_Syntax

<!-- Other -->
[chm]: https://www.softwarepreservation.org/projects/LISP/
[mac79]: http://jmc.stanford.edu/articles/lisp/lisp.pdf
[ste96a]: https://www.dreamsongs.com/Files/HOPL2-Uncut.pdf
[ste96b]: https://dl.acm.org/doi/10.1145/234286.1057818

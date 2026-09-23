CLIC Language
=============

See also:
- [`objects.md`][obj]: Core object types, including some constants.
- [`library.md`][lib]: CLIC Standard Library.
- [`console.md`][con]: Console I/O, case and special character handling.

General Notes
-------------

### Relationship to Other Lisps

While inspired particularly by Scheme (and being a Lisp-1 — functions and
variables are in the same namespace), CLIC has many Lisp 1.5/Common
Lisp-like features as well. Names are often utterly different; they've been
picked for ease of understanding and memory by new programmers; typical
users are expected to have no experience with any Lisp at all.

### Character Set

CLIC works internally in full 8-bit characters ($00–$7F ASCII and $80–$FF
machine-specific) with case-sensitive (CS) symbols and characters. Use on
case-insensitive (CI) systems (typically ones that support upper case only)
is [handled through the console drivers][con] that use an input prefix
character, alternate display modes and/or character substitutions to allow
both input and output of the full character set.

#### Upper vs. Lower Case

CLIC uses case-sensitive symbols. Standard library symbols (and user
symbols) are generally lower case but with upper case allowed where wanted.
The [console driver][con] handles using upper case for lower case, escaping
"true" upper case, as described above.

This is similar (in reverse) to Common Lisp's ability to use lower case I/O
for upper case symbols except that CL does this via its _readtable_ system
(see [`lisp.md`]) rather than outside of the language itself.


The Reader
----------

### Parsing Procedure

We are currently leaning toward the CL way of doing things: read and store
an entire token (which uses a little bit of memory, but no more than a
dozen or two bytes in most cases), determine if it's a valid format for a
number, and only then do the conversion. Unlike Scheme, where something
that starts out like a number fails to parse if it isn't one, we allow
tokens like `1+` or `30cm` and interpret them as symbols. This leaves
numeric parsing failures to be just overflows, it seems.

This gives us the following general parsing procedure:
1. Tokenizer (`rtok`): reads a token into a buffer, stopping read when the
   token is complete (1-char lookahead required).
2. Token parse (`qtok`): parses token buffer to an [object][obj].
3. Form read (`rform`): repeatedly calls both the above to read and parse
   tokens and generate the AST, storing it in the heap.
4. Something calls `rform`, gets back a pointer to the AST, and evals that
   in a given environment.

### Tokenization

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

Notes:
- These rules have been explicitly designed to allow using `'` as a 'prime'
  on symbols so you can have functions/variables `f'`, `x'`, etc. This is
  not allowed in CL (because `'` is a terminating macro character) or
  Scheme.
- The above means that, also unlike CL/Scheme, you must have a space before
  a quote: `(f'a)` is `(f (quote a))` in CL/scheme, but a single token in
  that list in CLIC.

### Numbers

If a whole token can parse properly as a number, it is parsed as a number.
Like CL and unlike Scheme, if it can't be parsed as a number it's a symbol,
regardless of how close to a number it gets: e.g., `+0123a` is a symbol.

This can be problematic. In CLIC variants with 2-char max symbols: `12O`
(letter O at the end) doesn't parse as a number and becomes the symbol `12`
which on output cannot be differentiated from the number `12`. Even in full
CLIC `12O` and `120` can be difficult to distinguish. Fixing this is
currently under consideration, but seems to be a lot of work. We ideally do
not want a system where, like Scheme, you can't have `1+` as a symbol for
increment.

XXX Valid formats for numbers need to be documented here.

### Characters

While some versions of CLIC will have strings and some will not, in all
versions of CLIC sym1 is re-used as the char type. This allows reading
standard `'c` syntax for printable characters. Non-printing chars use the
following escapes which are processed by the reader:

    \0      $00 NUL
    \a      $07 BEL terminal bell ("alert")
    \b      $08 BS  backspace
    \t      $09 TAB
    \n      $0A LF  linefeed
    \v      $0B VT  vertical tab
    \f      $0C FF  form feed
    \r      $0D CR  carriage return
    \e      $1B ESC escape
    \s      $20     space
    \"      $22 "   double quote
    \'      $27 '   single quote
    \p      $28 (   open parenthesis
    \q      $29 )   close parenthesis
    \\      $5C \   backslash
    \d      $7F DEL
    \xHH    $HH (any character by hex value; hex chars are case-insensitive)

Any unrecognised escape sequence (e.g., `\z`) is a parse error.

Note that none of the above include (and may not include) any of the
tokenizer's termination characters. This allows the tokenizer to know
nothing about character escaping.

(Adding a separate char type is possible and there's a note in
[`objects.md`][obj] §"Sym1/sym2" about how to do this, should it become
necessary.)


The Evaluator
-------------

### Self-evaluating Objects

A _self-evaluating_ object is one that, when passed to `eval`, comes back
as itself. For example, when the list `(list b 2 'b '2)` is read it becomes
a list of five objects in the heap; an `eval` of it will:
0. Look up the value of `list` in order to get the function code to apply.
1. Look up the value bound to `b` and use that.
2. Use `2` for `2` because it's self-evaluating.
3. Use `b` for `'b` because it's quoted.
4. Use `2` for `'2` because it's quoted (quoting doesn't care whether `2`
   is self-evaluating or not: `2` is never evaluated).

(Warning: the above steps should not be taken to imply an evaluation
_order,_ just that each step number is associated with the argument in that
position.)

In CLIC symbols and non-empty lists are evaluated; everything else is
self-evaluating. That includes empty lists (`#n` or `()`), consts (`#t`,
etc. as listed in [`objects.md`][obj]) and numbers.

Note that, unlike Scheme, `()` does not need to be quoted.


XXX TODO
--------

Summarise special reader forms?
- `#rHHHH` generic ref form.
- `#pHHHH` pointer form?


<!-------------------------------------------------------------------->
[`lisp.md`]: ./lisp.md
[con]: ./console.md
[lib]: ./library.md
[obj]: ./objects.md

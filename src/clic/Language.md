CLIC Language
=============

See also:
- [`objects.md`][obj]: Core object types, including some constants.
- [`library.md`][lib]: CLIC Standard Library.
- [`console.md`][con]: Console I/O, case and special character handling.

CLIC works internally in full 8-bit characters ($00–$7F ASCII and $80–$FF
machine-specific) with case-sensitive (CS) symbols and characters. Use on
case-insensitive (CI) systems (typically ones that support upper case only)
is [handled through the console drivers][con] that use an input prefix
character, alternate display modes and/or character substitutions to allow
both input and output of the full character set.

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
2. Token parse (`qtok`): parses token buffer to an [object][obj].
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



<!-------------------------------------------------------------------->
[con]: ./console.md
[lib]: ./library.md
[obj]: ./objects.md

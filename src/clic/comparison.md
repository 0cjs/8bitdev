Comparing CLIC to Other Languages
=================================

There's an excellent comparison of various BASICs (incuding original
Dartmouth, Tiny and MS) at [Dialects compared][comp] on the Wikipedia [Tiny
BASIC] page. It also shows the year of release for each one.

Tiny BASIC
----------

[Tiny BASIC] has several dialects; the classic one is [described][ddj1] in
_Dr. Dobb's Journal_ v1n1, though the Wikipedia [formal grammar][tb-bnf]
is easier to read.

- `PRINT str/expr,+`: takes strings as well as expressions.
- `IF exp relop exp THEN stmt`
- `GOTO expr`
- `INPUT var,+`
- `LET var = expr`
- `GOSUB expr`
- `RETURN`
- `CLEAR`
- `LIST`
- `RUN`
- `END`

Numbers are 16-bit (signed?) ints.
Relops: `<`, `<=`, `=`, `>=`, `>`, `<>`, `><`

String constants (usable with `PRINT` only) not defined in design note, but
consist of characters space ($20) through `Z` ($5A).

Other features typically added:
- `RND()`
- `:` to separate statements in a single line.
- In `PRINT`, `;` not to move cursor, `,` to move to next zone.
- Function to return memory size.
- `FOR` loop.
- Arrays.



<!-------------------------------------------------------------------->
<!--Tiny BASIC -->
[Tiny BASIC]: https://en.wikipedia.org/wiki/Tiny_BASIC
[ddj1]: https://archive.org/details/dr_dobbs_journal_vol_01/page/n10/mode/1up?view=theater
[tb-bnf]: https://en.wikipedia.org/wiki/Tiny_BASIC#Formal_grammar
[comp]: https://en.wikipedia.org/wiki/Tiny_BASIC#Dialects_compared

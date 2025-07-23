Comparing CLIC to Other Languages
=================================

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

Relops: `<`, `<=`, `=`, `>=`, `>`, `<>`, `><`

String not defined in design note, but space ($20) through `Z` ($5A).



<!-------------------------------------------------------------------->
<!--Tiny BASIC -->
[Tiny BASIC]: https://en.wikipedia.org/wiki/Tiny_BASIC
[ddj1]: https://archive.org/details/dr_dobbs_journal_vol_01/page/n10/mode/1up?view=theater
[tb-bnf]: https://en.wikipedia.org/wiki/Tiny_BASIC#Formal_grammar

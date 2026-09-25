Comparing CLIC to BASIC
=======================

There's an excellent comparison of various BASICs (including original
Dartmouth, Tiny and MS) at [Dialects compared][comp] on the Wikipedia [Tiny
BASIC] page. It also shows the year of release for each one.


Altair BASIC (Microsoft)
------------------------

Two 8080 versions:
* 4K RAM (790 bytes free): no string manip; some math missing.
* 8K RAM (??? free): string vars, math, peek/poke.

There was also Extended BASIC (`print using` and basic disk comands) and
Disk BASIC (raw disk I/O).

References:
- Wikipedia, [Altair BASIC]


Tiny BASIC
----------

1.8K (Palo Alto), 8080. Several dialects; the classic one is
[described][ddj1] in _Dr. Dobb's Journal_ v1n1, though the Wikipedia
[formal grammar][tb-bnf] is easier to read.

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

References:
- Wikipedia, [Tiny BASIC].


TRS-80 Level I BASIC
--------------------

4K, Z80. A variant of Palo Alto Tiny BASIC (1.77K) that added
floating-point, simple graphics and READ/DATA/RESTORE.


Sinclair BASIC
--------------

Two Z80 versions:
* ZX80: 4K ROM, 1K RAM. Integer arithmetic only.
* ZX81: 8K ROM, 2K RAM. Added floating point.

References:
- Wikipedia, [Sinclair BASIC].



<!-------------------------------------------------------------------->
<!-- Altair BASIC -->
[Altair BASIC]: https://en.wikipedia.org/wiki/Altair_BASIC

<!--Tiny BASIC -->
[Tiny BASIC]: https://en.wikipedia.org/wiki/Tiny_BASIC
[comp]: https://en.wikipedia.org/wiki/Tiny_BASIC#Dialects_compared
[ddj1]: https://archive.org/details/dr_dobbs_journal_vol_01/page/n10/mode/1up?view=theater
[tb-bnf]: https://en.wikipedia.org/wiki/Tiny_BASIC#Formal_grammar

<!-- Sinclair BASIC -->
[Sinclair BASIC]: https://en.wikipedia.org/wiki/Sinclair_BASIC

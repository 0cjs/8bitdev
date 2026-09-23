CLIC Language
=============

CLIC is a small Lisp-like language (dynamically typed and garbage-collected)
designed for microcomputers of the 1970s and early 1980s era. The general
characteristics are:

* Status:
  - Very early development; just an 8080 version with very little running yet.
* Language:
  - Simplicity and consistency are primary design goals, with source
    compatibility with Lisp or Scheme not at all a concern.
  - It tends to be influenced more by Scheme than by Common Lisp, but
    inspiration is taken from both.
  - It's a Lisp-1, i.e., functions and variables are in the same namespace.
  - It's intended to support compilation at some point.
* Environment:
  - Portable to systems of all sizes and CPUs.
  - The smallest versions require only a couple of kilobytes for the
    interpreter and a few hundred bytes of free RAM for user data.
  - Programs, when written with portability in mind, run on systems of all
    sizes. The language and implementations are subsettable.
  - Direct machine access (reading/writing/calling memory) is always
    available and use of user-supplied machine-language/binary components
    is fully supported.
  - Upper/lower case and full 8-bit character support are always available.
    Symbols are case-sensitive.
  - It's intended to be competitive with BASIC on systems of all sizes.

### Files and Directories

This directory, `src/clic/`, contains documentation and generic test support:
- [`Language.md`] is the CLIC language overview and starting point for
  further language documentation.
- `lisp.md` and `basic.md` document other languages for the purposes of
  comparison and stealing ideas.
- `objref.py` is machine-independent construction and reading of CLIC
  objects etc., mainly used by tests.

The code itself is contained in:
- [`src/i8080/clic/`]: 8080/Z80  version.



<!-------------------------------------------------------------------->
[`Language.md`]: ./Language.md
[`src/i8080/clic/`]: ../i8080/clic/

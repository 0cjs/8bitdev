Support Files for The Macroassembler AS
=======================================

This is support for projects that want to use
[The Macroassembler AS][asl] on Linux.

The `Setup` script in this directory will do nothing if the tool is
already available from the environment (e.g., an OS package for it has
been installed, or you have added it an external version to your
`$PATH`), otherwise it will fetch, configure and build a copy under
`$BUILDDIR` (default: `.build/` in the current working directory) and
emit configuration for the build environment to use that.

See the documentation in `Setup` for more details.



<!-------------------------------------------------------------------->
[asl]: https://github.com/KubaO/asl.git

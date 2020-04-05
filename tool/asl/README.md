Support Files for The Macroassembler AS
=======================================

This is support for projects that want to use
[The Macroassembler AS][asl] on Linux.

The `Build` script in this directory contains Bash functions to help a
master build script check for the presence of the `asl` command in the
path and fetch/build it if necessary. Use the Bash `.` or `source`
directive in your script to load those functions. See the script
itself for further details.

You may also run `Build` directly from the command line, in which case
it will always fetch and build AS into `.build/asl/` under the current
directory (or fail if the `.build/` directory doesn't exist).



<!-------------------------------------------------------------------->
[asl]: https://github.com/KubaO/asl.git

8bitdev
=======

This repo is used by cjs for development of programs in 8-bit assembly
languages (for a variety of platforms) and tools to aid this development.

If you wish to discuss any of the code here, the best way to reach me is to
contact `cjs_cynic` on Telegram or `0cjs` on Discord. You can also use the
e-mail address in the commit messages, but that's more likely to get lost
in the noise of all my e-mail and will always take longer to get a response.

### Contents

- (Top Section)
  - Contents
  - Introduction
- File and Directory Organization
  - ASL (The Macroassembler AS) Notes
  - ASxxxx Notes
- Third-party Development Tools
  - VICE: The Versatile Commodore Emulator
  - MAME Multi-system Emulators
- Additional Third-party Tools
  - VICE: The Versatile Commodore Emulator
  - MAME Multi-system Emulators
- Additional Tool Information
  - Playing CMT (Cassette Tape) Images
  - The py65 Monitor

### Introduction

This repo uses [`t8dev`][] (and its dependency, `r8format`) for downloading
and building various development tools, building the code itself, unit
testing it, building ROM and disk images, and running emulators. Here we
bring it in a Git submodule `t8dev/` in order to do development on it along
with code in this repo.

Run the top-level `Test` script build everything and run all the automated
tests. This script also accepts other options; see below.

Source `t8dev/t8dev/t8setup.bash` to activate the Python virtualenv
containing `t8dev`. You can also just export $T8_PROJDIR pointing to the
root of this repo and run programs directly from `.build/virtualenv/bin/`.

This currently has been tested only under Linux (Debian 9), but is likely
to work under MacOS and other Unices. It likely can be made to work under
Windows as well, if there's demand; contact me if you're interested in
getting support for this.


File and Directory Organization
-------------------------------

Here is an overview of the major files and directories in this repo.

Files:
- `README.md`: This file.
- [`Test`](./Test): Installs third-party tools where necessary, builds the
  code and runs the unit tests. (Bash.)
- [`requirements.txt`](./requirements.txt): t8dev and other Python
  requirements to be installed in the Python virtualenv.

Directories:
- [`src/`](./src/): Assembly source code, unit tests and documentation.
  These are generally modules used by full programs under `exe/`. Most of
  the code is built with [ASL]. See [`src/README.md`](./src/README.md) in
  the subdir for more on this.
- [`exe/`](./exe/): "Top-level" assembly files for full executable program
  builds, usually just doing configuration and including code from `src/`.
  See [`exe/README`](exe/README.md) for more on this.
- [`tmp/`](./tmp/): Ignored; used to keep developer's random files out of
  the way.


Third-party Development Tools
-----------------------------

#### py65 Notes

The [PyPI `py65`][py65pypi] sometimes falls out of date. You can also
update `requirements.txt` to the current version from GitHub:

    .build/virtualenv/bin/pip install -U \
        py65@git+https://github.com/mnaberez/py65.git

This will pull the head of the main branch; to use a release branch
append `@<branch-name>` to the URL.

#### ASL (The Macroassembler AS) Notes

Versions 1.42 builds 205 through at least 218 are broken for 8bitdev due to
the "Symbols in Segment NOTHING" section disappearing from the map file.
See [`t8dev.toolset.asl`] for more details.

#### ASxxxx Notes

The Linux binaries provided for ASxxxx are 32-bit, and on 64-bit systems
will error out with "No such file or directory" when run unless the 32-bit
dynamic linker (`ld-linux.so.2`) and libraries are installed.

For this reason, by default ASxxxx is not installed and used. Use `./Test
-A` to enable assembly and testing of code using ASxxxx. This is a
persistent flag (even across fully clean `./Test -C` builds); remove
`.all-tools` from the top level repository directory to disable it.

To install the 32-bit libraries on a 64-bit Debian 9 system:

    dpkg --add-architecture i386
    apt update
    apt install libc6-i386


Additional Third-party Tools
----------------------------

The following tools do not currently have any specific support in this
repo, but can be useful for testing.

### VICE: The Versatile Commodore Emulator

[VICE] is a suite of simulators for various CBM computers, including PET
models, the VIC-20 and the Commodore 64.

### MAME Multi-system Emulators

You can install or build the latest version from `mamedev.org` or just use
your system packages; on Debian 9 they'd be installed with:

    sudo apt-get install mame mame-tools mame-doc

The documentation installed by `mame-doc`, under
<file:///usr/share/doc/mame-doc/singlehtml/index.html>, is just an older
version of what's found at <https://docs.mamedev.org>


Additional Tool Information
---------------------------

### Playing CMT (Cassette Tape) Images

See [`r8format/doc/cmtconv.md`][cmtdoc].

### The py65 Monitor

py65 includes a monitor, `py65mon`, that can be run from the command
line. With no options it drops directly into the monitor on a
simulated 6502 with 64K RAM.

Options:
- `-l FILE`: Load file at address `$0000`.
- `-r FILE`: Load ROM image at top of address space and reset into it.
- `-g ADDR`: Goto _ADDR_ after loading files.
- `-i ADDR`: Location of TTY input register `getc` (default `0xf004`)
- `-o ADDR`: Location of TTY ouput register `putc` (default `0xf001`)

Addresses given on the command line use C/Python base notation (`10`,
`0xa`, `012`) rather than the `+$` notation used with monitor
commands.

__[Command][py65-cmds] summary__ (similar to [VICE monitor][vice-mon]):

General:
- Readline command line editing available.
- Prefix numbers w/`$+%` for hex/decimal/binary. `radix` shows/sets default.
- `help [CMD]` with for more details.
- `quit`
- `add_label ADDR NAME`, `show_labels`, `delete_label NAME`: _NAME_ can be
  used in place of _ADDR_ below, and arithmetic (`start+8`) may be used.

Display and input:
- `~ NUMBER`: Displays _NUMBER_ in all bases.
- `registers`: display `PC  AC XR YR SP NV-BDIZC`.
  Set regs with `NAME=VALUE`, comma-separated.
- `mem START:END`: Display memory. Show 16-byte lines with `width 70`.
- `fill ADDR[:END] BYTE ...`: Deposit byte(s) starting at _ADDR_.
   Repeats bytes to _END_ if given.
- `disassemble START:END`
- `assemble ADDR [STMT]`: Interactive if no stmt given. Labels may be used.
- `load "FNURL" ADDR`: Load file or URL (quotes optional) at given
  address (`top` for top of memory). (Warning: C64 files will have a
  two-byte load address at the start of the file that's treated as data.)
- `save FNAME START END`

Execution:
- `reset`: Reset CPU and clear memory.
- `goto ADDR`: Set PC and resume execution
- `return`: Execute, return to monitor just before next `RTS/RTI`.
- `step`: Executes instr, disassembles next instr.
- `add_breakpoint ADDR`, `show_breakpoints`, `delete_breakpoint ADDR`.
- `cycles`: Display number of cycles since last reset.



<!-------------------------------------------------------------------->
[`t8dev.toolset.asl`]: https://github.com/mc68-net/t8dev/blob/main/t8dev/psrc/t8dev/toolset/asl.py
[`t8dev`]: https://github.com/mc68-net/t8dev
[asl]: http://john.ccac.rwth-aachen.de:8000/as/
[cmtdoc]: https://github.com/mc68-net/t8dev/blob/main/r8format/doc/cmtconv.md
[py65pypi]: https://pypi.org/project/py65/#history

[VICE]: https://vice-emu.sourceforge.io/
[py65-cmds]: https://py65.readthedocs.io/en/latest/index.html#command-reference
[py65-src]: https://github.com/mnaberez/py65
[vice-mon]: http://vice-emu.sourceforge.net/vice_12.html

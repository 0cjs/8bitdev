#   This Makefile produces the assembler output files from program.a65
#   which are used by the test system for the testmc.asl module. These
#   files are committed, so you do not need to run this unless you've
#   modified the .a65 file(s), in which case you should commit the new
#   generated files along with your test framework changes.

PATH := ../../../../.build/asl:${PATH}
SHELL := bash
export PATH SHELL

ASMOPTS = -U -qxxx              # case sensitivity, quiet, error messages
ASMOUT  = -L -s -g map          # ouptut options

all: program.map program.lst program.p
.PHONY: all

program.map program.lst program.p: program.a65 program.inc
	asl </dev/null ${ASMOPTS} ${ASMOUT} $<

clean:
	rm -f *.{p,lst,map}


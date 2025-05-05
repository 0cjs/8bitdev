8bitdev/script/
===============

### Convenience Scripts

* `install-deb`: On Debian/Ubuntu systems, install most of the things that
  will be requested by `t8dev toolset ...` in this repo. This simply saves
  a bit of time over running `Test` to find out what's missing.

### Build Scripts

The build scripts in this directory are one-offs to handle build tasks that
t8dev cannot currently handle; eventually t8dev should be improved to be
able to take simpler build descriptions and do what's being done by these
scripts.

* `applesoft`: Build a disk image that auto-boots an Applesoft BASIC program.

### Other Scripts

There are also a few other scripts we've not yet found a proper home for.

* `dl-a1-rom`: Downloads Apple 1 ROM images. This should probably be a
  part of the external tools dependency system, like the OS images,
  downloading these under `.build/tool/` somewhere. The images are: …

8bitdev/make/
=============

### Build Scripts

The build scripts in this directory are one-offs to handle build tasks that
b8tool cannot currently handle itself; eventually b8tool should be improved
to be able to take simpler build descriptions and do what's being done by
these scripts.

### Other Scripts

There are also a few other scripts we've not yet found a proper home for.

- `dl-a1-rom`: Downloads Apple 1 ROM images. This should probably be a
  part of the external tools dependency system, like the OS images,
  downloading these under `.build/tool/` somewhere. The images are:

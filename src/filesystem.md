A Simple Filesystem for 8-bit Computers
=======================================

This is documenting an idea (that's certainly not yet fixed in stone)
for a filesystem and block device interface for original 8-bit
microcomputers (dating from 1975-1985 or thereabouts, and referred to
as "contemporary"), modern 8-bit computers, and contemporary
microcomputers interfaced with modern storage hardware.

This is currently a sketch and is almost certain to be changed and
updated in the future. See the last section for a list of problems and
changes that could be considered.

Design Criteria
---------------

- It should make reasonably efficient use of space and have the
  capability to be reasoanbly fast for sequential access on rotating
  media with seeking heads. Random access within files on rotating
  media need not be optimized, but should be possible.
- It should be optimal on devices storing around 100 KiB to 1 MiB, but
  should also support very small devices (e.g., RAM or ROM volumes of
  just a few kilotbytes) and larger devices up to some size reasonable
  for the 8-bit world.
- It should support varying block sizes, in particular at least all
  powers of two between 128 bytes and 4096 bytes, in order to support
  various floppy, HDD and optical media.
- It should have as much support as reasonable for recovering from
  data errors; trashing a single sector ideally should corrupt no more
  than one file or only file metadata without corrupting contents,
  though a recovery program may be necessary to recover from that
  situation.
- In order to reduce complexity, a hierarchical directory structure is
  not supported. However, up to 256 volumes may be simultaneously
  available, and volumes may have names, so this does give a sort of
  two-level hierarchy that can be used with multiple volumes on a
  single storage device.
- It should be fairly simple to write external tools for modern
  systems to read and write files using this filesystem.

The devices anticipated for use with this system are:

- RAM and ROM disks.
- Old floppy disk (and similar) systems, whether the disk controller
  is onboard (e.g., Apple II) or offboard via a separate
  communications interface (e.g., PET, C64, NEC PC-8001, Apple
  SmartPort).
- Old, small (<32 MB) hard drives, possibly partitioned into multiple
  devices.
- "Modern" block storage device interfaces talking directly to the
  media, such as HDDs and Compact Flash cards via ATA and SD cards via
  SPI.
- "Disk image" interfaces where the filesystem is stored as a file on
  external media (e.g., a FAT-32 filesystem on a flash memory device)
  and the block driver has an external means of selecting which
  file(s) to use.
- Generic "block" interfaces to external storage devices that may have
  their own interface logic.


Parameters and Limits
---------------------

The current design below has the following parameters and limits.

Each volume may have up to __65536 blocks__ and up to __254 files__. A
single file may be up to the full size of the volume, minus metadata.
The free block table is fixed in size, but the directory data will vary
depending on the number of entries; it's a minimum of one block.

The maximum sizes for some typical block sizes are given below. The
Volume size is the total number of bytes in the volume, including the
unused 0 block and the free block table.

    Block  Volume
    Size    Size    Notes
    -----------------------------------------------------
       32   2 MiB   Typically a small ROM- or RAM-disk
       64   4 MiB   "
      128   8 MiB   Typically a floppy disk or image
      256  16 MiB   "
      512  32 MiB   Small hard disk, flash storage or image
     4096 128 MiB   Optical disk, large hard disk, flash storage or image
    65536   4 GiB   Maximum block size

To reduce memory pressure, block sizes of 256 bytes or less are
preferred. Larger block sizes are here mainly to support media with
larger sector sizes in situations where it's not practical to have the
block driver subdivide sectors into multiple blocks.


System Layers
-------------

The system is divided into layers in order to allow mixing and
matching of hardware and software components. From the lowest to the
highest layer, these are:

1. Hardware using an interface specific to the block device interface
   layer above it.
2. A _block device_ interface for reads from and writes to block
   storage by block number. (This does not cover formatting and
   similar activities, which are external to this interface, whether
   done on the target microcomputer system itself or on other computer
   systems.)
3. A _filesystem_ layer which communicates with the block device layer
   on one side and presents an API for reading/writing/etc. files on
   the other side.
4. An _OS_ interface that is the client to the filesystem layer,
   allowing opening/closing/reading/writing of files and so on.

This document covers the API between the block device and filesystem
layers and an implementation of the filesystem layer itself. It's
intended that the block device interface be usable by other filesystem
layers as well.


Block Device Interface (BDI)
----------------------------

All block devices are represented as a sequential array of blocks of a
consistent (per-volume) size in bytes that is a power of two. Block
numbers are always 16 bits, ranging from 0 to 65535. However, block 0
is not required to exist; the filesystem later described, in order to
leave space for a boot block, does not use it. Whether block 0
actually exists and whether the driver gives access to read and write
it is driver-dependent. (This allows, e.g., ROM volumes to save the
space that would otherwise be allocated to an unused block.)

Block numbers and addresses are always in native byte order (little-
or big-endian depending on the CPU).

Blocks may consist of multiple sectors, but this is transparent to the
layers above. For example, floppy drives typically have 128 byte
sectors but for efficiency would typically have a BDI using 256 byte
blocks, reading and writing each block as a pair of sectors. But
different BDIs might be created, or BDIs might be parameterized, to
use different blocking for the same physical device.

### BDI Functions

The block device interface (BDI) has three main functions. In all
cases it should be assumed that an error can be returned to indicate
failure of some sort; how this is done is not yet defined.

On systems with multiple kinds of devices, there may be a higher-level
BDI that maps requests to several different lower-level BDIs. In any
case, the address of the BDI entry point to be used by higher layers
should be stored in RAM so that it can be replaced. (It might be
replaced with a completely different driver or perhaps a shim to allow
the use of multiple drivers).

#### Connect Device

_Connect Device_ is given an 8-bit _volume number_ and an optional
string serving as a device or volume name; on return the device or
volume name will be associated with that number for use in other calls
below, or an error indication will be returned to indicate that the
volume number is not available or no volume is available with that
name. This is intended to allow, e.g., opening a filesystem image
stored in a non-native filesystem on external media (e.g.,
`MYSTUFF.DSK` on a FAT filesystem on an SD card).

BDIs with fixed volume assignments may allow only certain volume
numbers (e.g., 0 and 1 for each of two floppy drives). In this case it
might accept any device/volume name so long as the volume number is
one of the valid fixed assignments, always returning success, and
always return error for any other device/volume number.

#### Get Volume Information

_Get Volume Information_ is given an 8-bit volume number (either fixed
by the driver or returned by the Connect Device function) and an
address at which to store the volume information. The following data
structure will be written starting at that address. Sizes are given in
bytes; multi-byte numbers are big-endian. (The caller is free to swap
bytes in the data structure after it's been written, if that's
convenient.)

    Name    Size    Description
    BLKSIZ    1     n, where the block size of the device is 2^n
    VOLLEN    2     The number of blocks (starting at 0) available on
                    the volume currently mounted.
    METASTART 2     The suggested block number at which filesystem
                    metadata should start.

`METASTART` is used on filesystems where seek time is dependent on
distance; it will point to the start of a track/cylinder somewhere in
the middle of the disk. Filesystems may (but do not have to) use this
as the location at which to start their metadata (catalogue
information or the like) in order to reduce average seek time between
metadata and other data on the disk.

It's possible that this also ought to include volume name and other
information as well. But given that can vary drastically in size,
possibly that should be a separate call, if it's even necessary.

#### Read Block, Write Block

These two functions are given a volume number, block number and
address in memory. The read function copies a block's worth of data
from memory to the given block/volume; the write function does the
reverse. There are no alignment constraints on the address, but a full
block is always read or written.

Anything here that can lessen the need for buffering (by supporting
no-copy transfers, streamed processing, or other means) is worth
bringing in here.

(It's possible that this should be extended to take a length for the
data in memory, reading/writing undefined data for the remainder of
the block if the data in memory are not a full block long, but I'm not
sure if this is would actually be useful.)


Filesystem Design and Layout
----------------------------

This is one filesystem intended to use the block interface described
above; others could be written or ported.

The filesystem blocks are organized as follows:
- A never-used block at offset 0. (This leaves room for a boot block).
- A free block map starting at METASTART. This is a sequential bitmap
  with a bit for each sector from 0 through VOLLEN, taking as many
  sectors as necessary for the bitmap.
- An initial directory block starting immediately after the free block map.
- All remaining blocks are directory or data blocks, allocated as
  necessary.

#### Free Block Map

The free block map is a convenience for efficiency and should not be
assumed always to be correct. Whenever allocation information in the
data blocks themselves conflicts with the free block map, the data
blocks should be assumed correct and the free block map updated
appropriately. It's possible that, for efficiency, free block map
updates will be delayed until long after data block updates, and due
to this the free block map updates do not happen at all. (This would
be the case if someone removes a floppy disk in the middle of a
write.)

The map is a sequence of bytes where the LSB to MSB (bits 0 to 7) of
the first byte represents the status of blocks 0 through 7, the next
byte's 0-7 bits the status of blocks 8-15, and so on. This continues
for as many device blocks as necessary to account for all blocks on
the device.

Each bit is `0` to indicate that the block is (likely) free, and `1`
to indicate that it is (likely) allocated.

Block 0 should always have a value of `1` in the free block map, but
even if it does not it will never be considered free space, regardless
of the contents of the block itself.

The first directory block (see below) also should always have a value
of `1` in the free block map; it is always considered allocated
regardless of the free block map value.

#### Data Blocks

Data blocks are all blocks outside of the free block map, including
directory blocks. For any block size _n_, the first _n-6_ bytes are
the data itself, followed by 6 bytes of metadata:

    n-5, n-4    Block number of previous block in chain for this file
    n-3, n-2    Block number of next block in chain for this file
         n-1    Length of used data in this block, starting at the first byte
         n-0    File number of file to which this block belongs

Every file on the volume is assigned an 8-bit _file number_ from 0 to
255. 0 and 1 are special file numbers; 0 indicates unallocated space
and 1 indicates the block belongs to the _directory_, a special "file"
containing the metadata for files (file numers, names, starting
blocks, and so on). File numbers of deleted files are not reused until
all subsequent file numbers have been used once (or once again); for
more on this see below.

When new data blocks are added to a file they are written first, and
only after they have been successfully written to the block device are
the preceeding and following (if any) blocks updated, followed by the
directory (if necessary) and the free block map. This ensures the best
chance of recovery should a sequence of writes be interrupted or a
block go bad.

The data length will typically be used only in the last block to
indicate a file with a length less than a multiple of BLKSIZ. However,
arbitrary amounts of data can be inserted in the middle of a file if
desired. (It's not clear if this filesystem would support writing in
this way, but reading should always take into account the data size
for every block.)

When reading data from or writing data to files, having the block data
above at the end of the block makes it easy for the filesystem to
read/write arbitrary amounts of data with minimal copying, assuming
the application can allocate sufficient space for a full block even
when it won't all be valid data. On a read, if the block interface
must write a full block of data from the disk to a location in memory,
the full _n_ bytes from the first block may be written to the starting
address, the next write address increased by _n-6_, and the next block
read in the same way, overwriting the six bytes of metadata from the
first block.

#### The Directory

The directory is always file 1 and its first block is the block
immediately after the free block map. Additional directory blocks may
be allocated as necessary anywhere on the disk.

The directory contains a header entry followed by a sequence of
entries for files and free space in the directory. All entries start
with a single _file number_ byte (some file numbers are special and
indicate information other than file metadata) followed by a length
byte giving the total length of the data for that entry, not including
the file number and length bytes themselves.

The first entry always has file number $00. The length is always 1
(for this version of the file system) and the sole byte of data is the
_next file number_ field (details below).

Subsequent entries are as follows, with offsets and sizes in bytes:

    Offset  Size    Description
       0     1      File number, or $00 for an unused entry in the directory.
       1     1      Total length (not including the file number and length
                    bytes) of the data in this entry.
       2     1      $01 or $02 to indicate a first block field. $01
                    indicates an allocated file; $02 a deleted file whose
                    blocks have not yet been deallocated.
       3     1      $02 for the length of the first block field.
       4     2      The block number of the first block containing the
                    contents of this file.
       6     2      $03 to indicate a filename field.
       7     1      The length of the filename, _m_.
       8     m      A filename as arbitrary bytes (usually printable ASCII).
       8+m   1      $00 to indicate the end of this directory entry, or any
                    other number (excepting $01, $02 or $03) to indicate
                    the type of additional metadata.
       8+m+1 1      Length of this additional metadata field, if present.
       8+m+2 ?      Additional metadata.
       ...

The directory entry always starts with a byte for the file number and
byte for the length of the remainder of the entry; a file number of 0
indicates unused space in the directory. (The unused space may be
consolidated from time to time by copying all used directory entries
downward.) Thus, files may easily be deleted merely by setting the
first byte of the directory entry to 0, though it would also be wise
to update the free block map at some point after that.

The remainder of the directory entry is a set of tagged fields
consisting of a type byte and length byte followed by data of that
length. For simplicity, the first two fields are always a first block
field indicating the block in which the file data starts and a name
field giving the filename. Further fields are system-dependent; any
fields not known to a particular implementation of the filesystem
should be ignored (but copied when a copy of a file is made).

The currently defined field types are as follows:

    0   Unused field. (This is useful for deleting fields.)
    1   Start block of file data; always length 2 with the two bytes
        of data being the starting block in big-endian form.
    2   Start block of file data for a deleted file whose blocks have
        not (yet) been deallocated.
    3   Name field; length is the length of the name in bytes. There
        is no terminator byte after the name.
    4   Approximate file size in blocks. len=2, value big-endian.
    5   Approximate file size in bytes. len=4, value big-endian.
    6   File creation timestamp.
    7   File modification timestamp.

The only required fields are the start block and name fields. All
implementations of this filesystem should handle directory entries
with only those two fields, and should ignore any fields whose type
they do not understand.

The approximate size fields are for convenience when listing directory
information; the actual size of the file (in blocks and bytes) will
always be determined by the data blocks of the file.

Type numbers have been assigned above for file creation and
modification timestamps, but the format has yet to be determined.

Types for "file type" information as used by various systems (e.g.,
"B"=binary, "I"=Integer BASIC, "A"=Applesoft Basic on the Apple II)
are likely to be system-specific, and need to be worked out if they're
required. It's reasonable that we might have several different types
for different platforms, with the presence of a particular filetype
type indicating it's a file for that platform.

#### File Number Assignment

File numbers are assigned starting at 2 and proceeding sequentially
for each new file to 255, wrapping around after that. This maximally
delays the time at which a file number for a deleted file will be
re-used, increasing the chances of recovery of corrupted disks and
making available both file "undeletion" and optimizations when
deleting files.

The next file number to attempt to use when assigning a new file
number is stored as the first data byte the first entry of the
directory, as described in the section above. I.e., a freshly
initialized filesystem image will contain $00 $01 $02 (type, length
and next file number) at the start of the directory. This number must
be read and it must be confirmed (by reading all other directory
entries) that it's not in use; if it is used the number should be
incremented and the procedure iterated until a free file number is
found.

When a file is deleted its start block field in the directory entry is
changed from type $01 to $02. At this point the data blocks of the
file are still allocated and the file can be undeleted by changing the
type back to $02. At any point in the future (either automatically,
when free space needs to be recovered for new files, or through user
request) the deletion can be made permanent by deallocating the
individual file blocks and the directory entry.


Filesystem API
--------------

The API the filesystem code provides to application code is to be
determined, but is probably heavily dependent on the particular system
in which it's running.


Related Work
------------

The Atari DOS filesystem uses a nearly identical technique of storing
file number, byte count and next sector information at the end of each
sector. [This was not known to me when I did this design --cjs] It's
described in detail in [Chapter 9, "The Disk Operating System"][dra9]
of _De Re Atari_.


Problems and Potential Design Changes
-------------------------------------

We should probably add load address (and perhaps entry point address)
tags for binary files, since this idea is common to many systems.

One thing that's not entirely clear is if clustering of sectors into
blocks should be handled by the block device interface, rather than
the filesystem. Currently it seems easier to do the former, but that
may introduce problems not documented here.

The filesystem currently can't deal with bad blocks, especially if the
initial directory block is bad. Perhaps there's a way to work out how
to do this, but it seems difficult. Potentially the driver should take
care of this, since the older HDDs that do not do transparent bad
block remapping may still have their own mechanisms to help with this.
For floppies, it may be reasonable just not to use media with bad
blocks. An alterative would be to make the first block at METASTART a
list of bad blocks, but that would add a complexity to the filesystem.



<!-------------------------------------------------------------------->
[dra9]: https://www.atariarchives.org/dere/chapt09.php


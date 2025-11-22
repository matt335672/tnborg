# Introduction
Borg backup is not supported natively by TrueNAS, as of version 25.04

There are a couple of possibilities to get the Borg backup executable
working on TrueNAS:-

1. The borg backup releases on github contain ‘one file’ executables
   built with `pyinstaller`. These executables are self-extracting archive
   files which contain the python bytecode for borg, bundled with all
   the shared objects used by the bytecode.
2. In addition to the one-file borg backup releases, borg backup
   releases on github contain ‘one dir’ executables, also built
   with `pyinstaller`. These are effectively the same as the one-file
   executables, but are already extracted.
3. With a bit of effort, a one-dir executable can be built which
   exactly matches the target machine.

All of these approaches are described below. You will also need to
use the `misc/borg.sh` script edited appropriately with all of these
approaches.

# One-file executable approach
The advantage of this approach is the executable is easily obtained. The
big disadvantage is the surprising difficulty in unpacking the executable
every time it is run. The archive uses the TMPDIR environment variable
to find a suitable unpack directory. This defaults to `/tmp`, which on
TrueNAS is mounted with the `noexec` attribute.

Trying to run the executable directly results in an error similar to
the following:

```
error while loading shared libraries: libz.so.1: failed to map segment from shared object
```

This can be worked around with suitable scripting. A naïve approach
would be to define TMPDIR as `/run/user/$(id -u)/borgtmp`. This will
work for an `ssh` session, but fails if the executable is run from `sudo`,
as `/run/user/$(id -u)` will not necessarily exist in this instance.

The script `misc/borg.sh` in this repository contains suitable
code to use a 'one-file' executable. This code will need to be uncommented
before use.

# One-folder executable approach
Using this approach avoids the unpacking issues with the on-file
executable, and also improves startup times by a small fraction.

## Getting the correct borg on-folder build for TrueNAS
### Finding the libc version for TrueNAS
On the TrueNAS release, use a command like the following to list all
the GLIBC symbols in the library:-
```
readelf -s /lib/x86_64-linux-gnu/libc.so.6 | sed -ns 's/.*@//p' | sort -u
```
Look through the result to find the highest numeric GLIBC_2.* symbol. For TrueNAS  25.04.2, this is GLIBC_2.36. 

### Downloading the borg build
Download the best matching .tgz tarball and signature from the borgbackup
github releases. For borgbackup 1.4.2, this is the glibc231 version:
```
URL= https://github.com/borgbackup/borg/releases/download/1.4.2/
wget $URL/borg-linux-glibc231-x86_64.tgz
wget $URL/borg-linux-glibc231-x86_64.tgz.asc
```

Verify the gpg signature. Check the key fingerprint below from the borg
backup support pages.

```
gpg --recv-keys "6D5B EF9A DD20 7580 5747 B70F 9F88 FB52 FAF7 B393"
gpg --verify borg-linux-glibc231-x86_64.tgz.asc
```
## Installing borg build on TrueNAS

1. Copy the .tgz file to the NAS, and unpack it in the home directory
   being used to host these scripts. Rename the directory borg-dir to
   borg-dir-1.4.2 (or whatever the borgbackup version is).

2. Copy the `misc/borg.sh` file from this repository to `~/bin` and edit
   it appropriately
3. Check that the binary works `borg -V`

# Building borg backup for TrueNAS
The borg build github CI uses Vagrant to build borg one-dir
executables. We can make use of this ourselves to build a version of
borg backup which exactly matches the operating system release.

The procedure is as follows. This assumes a development machine is
available running `libvirt`, but other Vagrant backends can be used by
editing `misc/build_borg.sh`:

- Find the Debian version that the TrueNAS target runs on.
- On a development machine with `libvirt`, install `vagrant` and
  `libvirt-dev` packages
- Edit `misc/build_borg.sh` on the development machine and set the
  variables listed under 'General parameters' appropriately.
- Run `misc/build_borg.sh`. if all is well, this will generate a file
  `borg-dir-$BORG_VERSION.tgz` in the current directory.

Installation is the same as for a generic one-dir executable.

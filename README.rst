Shell scripts
--------------------------------------------------------------------------------

.. contents::

finddups.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Allows to locate duplicated files (exact copies) in selected directories.
The programs tries to be smart: firstly it groups files by size, then
tries to compare a few first bytes of them and finally does full comparison.

The output is a list of path, so you decide what to do with duplicates.


cmpdirs.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare two directories; it either displays differences or prints
shell commands required to make mirror of the first directory inside
the second one.


listdir.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For each file in directory prints its size and control sum (md5 or sha1).

I use it for storing extra checksums of files when burning CD/DVDs.


cmplists.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compare two lists; list can be either 1) a custom file of strings or
2) directory for which a list of files will be created.

Lists are then treated as sets and we may computer:

- sum,
- differnce,
- common part,
- exclusive or (sum minus common part)


forcereadonly.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Revoke write rights of all files and directories in given directory.

I use it to protect my collections of files (photos, music, documents,
etc.) from accidental removal.


testjpeg.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check if all JPEG files from given directory are valid; it uses
standard ``jpeginfo`` tool.

I use it to check if backups of photos stored on CD/DVDs are OK.


beep.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For programmers: a simple Windows program that displays messages
sent via network.

I used it to show notifications about completion of long-running
processes executed on remote machines.


sample_statm.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For programmers: sample ``/proc/pid/statm`` of given program.

I use it to determine real usage of memory; tools like valgrind
massif does not consider everything.


waitfor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For programmers: wait until a program of given program is started,
then print its pid. I use it for attaching to a program when
I can't control when/how it starts; for instance::

    gdb -p `waitfor my-program`

#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-

#   Compare two directories, similar to diff
#
#   Prints textual information or shell script that does mirror
#
#   Wojciech Muła, 2010-01-08
#   $Id$

import sys
import os
import os.path

def walk_tree(rootdir, visitdir=None, onfile=None):
    from os import walk
    from os.path import join

    for dirpath, dirnames, filenames in walk(rootdir):
        if visitdir:
            i = 0
            while i < len(dirnames):
                if not visitdir(dirpath, dirnames[i]):
                    del dirnames[i]
                else:
                    i += 1
        if onfile:
            for dirname in dirnames:
                onfile(join(dirpath, dirname), 'd')

            for filename in filenames:
                onfile(join(dirpath, filename), 'f')
    #


class DirectoryList(object):

    def __init__(self, rootdir):
        self.rootdir = os.path.abspath(rootdir)
        if not self.rootdir.endswith(os.sep):
            self.rootdir += os.sep

        self.pathlen = len(self.rootdir)
        self.files   = {}


    def __visitdir(self, dirpath, dirname):
        return True


    def __onfile(self, path, kind):
        from os import stat
        s = os.stat(path)
        p = path[self.pathlen:]

        # path => (id, mtime, size, kind)
        self.files[p] = (len(self.files), s.st_mtime, s.st_size, kind)

    def scan(self):
        self.files = {}
        walk_tree(self.rootdir, self.__visitdir, self.__onfile)


class CompareBase(object):
    "compare two DirectoryListings"

    SAME        = 0
    SIZEDIFF    = 1
    YOUNGER     = 2
    OLDER       = 3
    MISSING1    = 4
    MISSING2    = 5

    def __init__(self, dir1, dir2):
        self.dir1 = dir1
        self.dir2 = dir2

    def on_compare(self, path, kind, result):
        "relative path and compare result (one of constants)"
        pass

    def on_compare_start(self):
        pass

    def on_compare_end(self):
        pass

    def compare(self):
        on_compare = self.on_compare

        self.on_compare_start()

        for path, (id, mtime, size, kind) in self.dir1.files.items():
            if kind == 'd': # directory
                if path not in self.dir2.files:
                    on_compare(path, kind, CompareBase.MISSING2)
                else:
                    on_compare(path, kind, CompareBase.SAME)
            elif kind == 'f':
                if path not in self.dir2.files:
                    on_compare(path, kind, CompareBase.MISSING2)
                else:
                    (_, mtime2, size2, _) = self.dir2.files[path]
                    if size != size2:
                        on_compare(path, kind, CompareBase.SIZEDIFF)
                    elif mtime < mtime2:
                        on_compare(path, kind, CompareBase.OLDER)
                    elif mtime > mtime2:
                        on_compare(path, kind, CompareBase.YOUNGER)
                    else:
                        on_compare(path, kind, CompareBase.SAME)
            else:
                raise AssertionError("Unknown kind of path ('%s')" % kind)
        #
        
        for path, (_, _, _, kind) in self.dir2.files.items():
            if path not in self.dir1.files:
                on_compare(path, kind, CompareBase.MISSING1)
        #

        self.on_compare_end()

class CompareDescription(CompareBase):
    "print simple description of changes"
    def __init__(self, listing1, listing2):
        CompareBase.__init__(self, listing1, listing2)
    
    def on_compare(self, path, kind, result):
        if result == CompareBase.SAME:
            return

        L = []

        if kind == 'd':
            L.append("directory")
        elif kind == 'f':
            L.append("file")
        else:
            raise AssertionError("Unknown kind of path ('%s')" % kind)

        L.append(path)
        if result == CompareBase.YOUNGER:
            L.append("is younger")
        elif result == CompareBase.OLDER:
            L.append("is older")
        elif result == CompareBase.SIZEDIFF:
            L.append("has different size")
        elif result == CompareBase.MISSING2:
            L.append("not exists in second dir")
        elif result == CompareBase.MISSING1:
            L.append("not exists in first dir")

        print(" ".join(L))


class CompareShell(CompareBase):
    "print shell script that makes perfect copy of first directory"
    def __init__(self, listing1, listing2):
        CompareBase.__init__(self, listing1, listing2)

    def on_compare_start(self):
        self.mkdirs = []
        self.rmdirs = []
        self.cpfiles = []
        self.rmfiles = []


    def on_compare_end(self):
        if self.mkdirs:
            print("\n".join(self.mkdirs))

        if self.cpfiles:
            print("\n".join(self.cpfiles))

        if self.rmfiles:
            print("\n".join(self.rmfiles))

        if self.rmdirs:
            print("\n".join(self.rmdirs))


    def on_compare(self, path, kind, result):
        from os.path import join

        if result == CompareBase.SAME:
            return

        if kind not in ['d', 'f']:
            raise AssertionError("Unknown kind of path ('%s')" % kind)

        if result == CompareBase.SIZEDIFF:
            if kind == 'f':
                self.cpfiles.append(
                    'echo copy "%s"' % path
                )
                self.cpfiles.append(
                    'cp -f --preserve=all "%s" "%s"' % (join(self.dir1.rootdir, path), join(self.dir2.rootdir, path))
                )
        elif result in [CompareBase.YOUNGER, CompareBase.OLDER]:
            if kind == 'f':
                self.cpfiles.append(
                    'echo copy "%s"' % path
                )
                self.cpfiles.append(
                    'cp -f --preserve=all "%s" "%s"' % (join(self.dir1.rootdir, path), join(self.dir2.rootdir, path))
                )
        elif result == CompareBase.MISSING2:
            if kind == 'f':
                self.cpfiles.append(
                    'echo copy "%s"' % path
                )
                self.cpfiles.append(
                    'cp --preserve=all "%s" "%s"' % (join(self.dir1.rootdir, path), join(self.dir2.rootdir, path))
                )
            elif kind == 'd':
                self.mkdirs.append(
                    'mkdir -p "%s"' % join(self.dir2.rootdir, path)
                )
        elif result == CompareBase.MISSING1:
            if kind == 'f':
                self.rmfiles.append(
                    'echo del "%s"' % path
                )
                self.rmfiles.append(
                    'rm -f "%s"' % join(self.dir2.rootdir, path)
                )
            elif kind == 'd':
                self.rmdirs.append(
                    'rmdir "%s"' % join(self.dir2.rootdir, path)
                )
        #
    
def help(ret=0):
    print(
        """
        usage: program M directory1 directory2

         M is method of compare result presentation:"
         d - print simple description"
         s - print shell script that makes mirrof of dir1 in dir2"
        """
    )
    sys.exit(ret)


if __name__ == '__main__':
    if "-h" in sys.argv[1:] or "--help" in sys.argv[1:]:
        help()

    if len(sys.argv) != 4:
        help(1)

    M = sys.argv[1]
    if M not in ['d', 's']:
        help(2)

    dir1 = sys.argv[2]
    dir2 = sys.argv[3]
    if not os.path.exists(dir1):
        sys.stderr.write("'%s' is not a directory" % dir1)
    if not os.path.isdir(dir1):
        sys.stderr.write("'%s' is not a directory" % dir1)
    if not os.path.exists(dir2):
        sys.stderr.write("'%s' is not a directory" % dir2)
    if not os.path.isdir(dir2):
        sys.stderr.write("'%s' is not a directory" % dir2)

    l1 = DirectoryList(dir1)
    l2 = DirectoryList(dir2)
    l1.scan()
    l2.scan()

    if M == 'd':
        Cmp = CompareDescription(l1, l2)
    elif M == 's':
        Cmp = CompareShell(l1, l2)

    Cmp.compare()
#

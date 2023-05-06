#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 
# Make or compare list of files
#
# Author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# www:    http://0x80.pl/
#
# License: public domain

import os
import os.path
import hashlib
import sys

from os.path import join, getsize

def main(args):
    def arg(index, default=None):
        try:
            return args[index]
        except IndexError:
            if default is not None:
                return default
            else:
                help()
                sys.exit(1)

    action = arg(1)
    if action in ['make', 'list', 'ls']:
        make_list(arg(2), sys.stdout, getmd5sum)
    elif action in ['sha', 'sha512']:
        make_list(arg(2), sys.stdout, getsha512sum)
    elif action in ['cmp', 'compare']:
        path1 = arg(2)
        path2 = arg(3)

        list1 = open(path1, 'r').readlines()
        list2 = open(path2, 'r').readlines()
        compare(list1, list2, arg(4, ''), sys.stdout)
    else:
        sys.stderr.write("Unknown action '%s'\n" % action)
        help()


def make_list(root_directory, out, getchecksum):
    root_directory = os.path.normpath(os.path.abspath(root_directory))
    n = len(root_directory)

    for root, dirs, files in os.walk(root_directory):
        for file in files:
            path = join(root, file)
            s = "%s %10d %s\n" % (getchecksum(path), getsize(path), path[n:])
            out.write(s)
    pass


def compare(list1, list2, prefix, out):
    for line in set(list1) - set(list2):
        s = prefix + line.split()[2]
        out.write(s + "\n")


def getmd5sum(path):
    h = hashlib.md5()
    with open(path, 'rb') as f:
        h.update(f.read())

    return h.hexdigest()


def getsha512sum(path):
    h = hashlib.sha512()
    with open(path, 'rb') as f:
        h.update(f.read())

    return h.hexdigest()


def help():
    print("""
    program ls directory
        
        make listing of all files - each file contains md5sum, size and filename

    program sha directory
        
        make listing of all files - each file contains sha512, size and filename

    program cmp list1 list2
        
        compare two listings, prints file from list1 that do not exists in list2
        or has different checksum or size 
    """)

if __name__ == '__main__':
    main(sys.argv)

# eof

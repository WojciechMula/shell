#!/usr/bin/env python
# 
# Author: Wojciech Mula
# e-mail: wojciech_mula@poczta.onet.pl
# www:    http://0x80.pl/
#
# License: public domain

import os, sys

from os.path import isdir, islink, exists, getsize, getmtime
from os.path import abspath, dirname, normpath, join
from hashlib import md5
from time import sleep

def parse_args(args):
    # define options
    from optparse import OptionParser

    parser = OptionParser("usage: %prog [options] directories")
    parser.add_option("-o", "--out", metavar="FILE", dest="log_file",
                      help="log file name")
    parser.add_option("-e", "--exclude", action="append", dest="exclude",
                      help="exclude given files or patterns; you can pass as many options as you need")
    parser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False,
                      help="be quiet")
    parser.add_option("-s", "--sleep", dest="delay", default=None,
                      help="pause given seconds amount between checking each file")
    parser.add_option("--no-recursive", dest="no_recursive", action="store_true", default=False,
                      help="do not go deeper")
    parser.add_option("--keep", action="store_false", dest="overwrite", default=True,
                      help="do not overwrite log file if exists")
    parser.add_option("--traceback", dest="print_traceback", action="store_true", default=False,
                      help="in case of error print full traceback, that can help identify an error")

    # parse
    (options, rest) = parser.parse_args(args)

    # check options
    if options.log_file is None:
        parser.error("-o is required")
        raise SystemExit

    if exists(options.log_file) and not options.overwrite:
        parser.error("File %s already exists." % options.log_file)
        raise SystemExit

    if options.exclude is None:
        options.exclude = []

    if options.delay is not None:
        options.delay = float(options.delay)

    tmp = set()
    directories = []
    for dir in rest[1:]:
        path = normpath(abspath(dir))
        if path in tmp:
            continue

        if not exists(path):
            parser.error("'%s' doesn't exists" % dir)
        elif not isdir(path):
            parser.error("'%s' is not a directory" % dir)
        else:
            directories.append(dir)
          
    if not directories:
        parser.print_help()
        raise SystemExit

    return (options, directories)


def main():
    options, directories = parse_args(sys.argv)

    # set up print-status function
    class Status:
        def __init__(self, quiet, max_width=72):
            self.last_len  = 0
            self.max_width = max_width
            self.progress  = 0.0
            self.file = sys.stderr

            if self.file.isatty() and not quiet:
                self.write = self.__print_stdout
            else:
                self.write = self.__print_dummy

        def __print_stdout(self, string, path=""):
            string = "%4.1f %s" % (100.0 * self.progress, string)
            n = len(string)
            k = len(path)

            if n + k > self.max_width:
                if n > self.max_width:
                    out = string[:self.max_width]
                else:
                    m = k-(self.max_width - n - 3)
                    out = string + "..." + path[m:]
            else:
                out = string + path

            n = len(out)
            if n >= self.last_len:
                sys.stderr.write(out + "\r")
            else:
                sys.stderr.write(out + (" "*(self.last_len - n)) + "\r")

            sys.stderr.flush()
            self.last_len = n

        def __print_dummy(self, string, path=""):
            pass

        def error(self, string):
            sys.stderr.write(string + "\n")
    
    status = Status(options.quiet)

    def printerror():
        if options.print_traceback:
            import traceback
            traceback.print_exc()
        else:
            info = sys.exc_info()
            status.error("%s: %s" % (info[0].__name__, info[1]))

    with open(options.log_file, 'wt') as log:
        list = scan_directories(directories, options, status)
        broken = check_files(list, status, options)
        for path in broken:
            log.write(path)
            log.write('\n')

    status.write('\n')


def scan_directories(directories, options, status):
    # Scanning directories
    def match(filename):
        from fnmatch import fnmatch

        for pattern in options.exclude:
            if fnmatch(filename, pattern):
                return True
        else:
            return False

    list = []
    for directory in directories:
        for root, dirs, files in os.walk(directory):
            status.write("Scanning: ", root)
            for file in files:
                if match(file):     # skip file
                    continue

                path = join(root, file)
                if islink(path):
                    continue
                else:
                    list.append((path, file))

            if options.no_recursive:    # do not go deeper
                del dirs[:]

    return list


def check_file(path):
    cmd = 'jpeginfo -c "%s" > /dev/null' % path
    ret = os.system(cmd)
    if ret == 2:
        raise KeyError

    return ret == 0


def format_time(seconds):
    T = int(seconds)

    s = T % 60
    m = (T / 60) % 60
    h = ((T / 60)/60)/60

    if h > 0:
        return '%02d:%02d' % (m, s)
    else:
        return '%02d:%02d:%02d' % (h, m, s)
    

def check_files(files, status, options):
    from time import time
    total  = len(files)
    errors = 0
    list   = []

    start = time()
    for index, (path, file) in enumerate(files):
        now = time()
        status.progress = float(index)/total
        ETA = format_time(now - start)
        EET = format_time(((now - start) * total)/float(index + 1))
        status.write("[%d/%d][E:%d][%s %s] checking: " % (index + 1, total, errors, ETA, EET), file)
        if not check_file(path):
            print "Wrong JPEG or not a JPEG file: ", path
            list.append(path)
            errors = len(list)
    
        if options.delay:
            sleep(options.delay)

    return list


if __name__ == '__main__':
    main()

# vim: ts=4 sw=4 nowrap

#!/bin/evn python

import os
import stat
import sys
import argparse
from os import walk, chmod
from os.path import join, isdir

def main():

	options = parse_args();

	def printmsg(string, important=False):
		print string

	def quietmsg(string, important=False):
		if important:
			print string

	if options.quiet:
		status = quietmsg
	else:
		status = printmsg

	if options.no_errors:
		error = quietmsg
	else:
		error = printmsg

	for directory in options.directories:
		forcereadonly(directory, status, error, options)


def parse_args():
	parser = argparse.ArgumentParser(description='Make subtree readonly - set files to 444 and directories to 555')
	parser.add_argument('directories', help='directories', nargs='+')
	parser.add_argument('-q', '--quiet', help='supress massages', action='store_true')
	parser.add_argument('-e', '--no-errors', help='do not print error messages', action='store_true')
	parser.add_argument('-d', '--dry-run', help='do not change rights', action='store_true')

	args = parser.parse_args()

	return args


def forcereadonly(directory, status, error, options):
	file_mod = 0444;
	dir_mod  = 0555;
	n = 0
	k = 0

	status("processing dir %s" % directory, important=True);

	if not isdir(directory):
		status("'%s' is not a directory, skipping" % directory, important=True)
		return

	def get_mode(path):
		mode = os.stat(path).st_mode
		return stat.S_IMODE(mode)

	for root, dirs, files in os.walk(directory):
		for file in files:
			path = join(root, file)
			try:
				if get_mode(path) != file_mod:
					status("file: %s" % path)
					if not options.dry_run:
						chmod(path, file_mod)
					n += 1
			except OSError, e:
				error(e)

		for dir in dirs:
			path = join(root, dir)
			try:
				if get_mode(path) != dir_mod:
					status("dir: %s" % path)
					if not options.dry_run:
						chmod(path, dir_mod)
					k += 1
			except OSError, e:
				error(e)

	status("fixed files: %d, directories: %d" % (n, k), important=True)

if __name__ == '__main__':
	main()


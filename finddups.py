#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-
# $Id$
#
# Find duplicated files. Just a list of duplicated is
# created, no files are deleted, nor moved.
#
# Progam works in 3 steps: first group files of same size,
# then group them by contents first 4kB, and finally calculate
# md5 checksum for selected files.
# 
# Program creates two files: removedups.md5cache and
# removedups.md5headcache, which store calculated checksum;
# these files can by reused later, making comparision much
# faster. However you are free to remove them.
# 
# Author: Wojciech Muła
# e-mail: wojciech_mula@poczta.onet.pl
# www:    http://0x80.pl/
#
# License: public domain

import os, sys

from os.path import isdir, islink, exists, getsize, getmtime
from os.path import abspath, dirname, normpath, join
from hashlib import md5

def parse_args(args):
	# define options
	from optparse import OptionParser

	parser = OptionParser("usage: %prog [options] list-of-directories")
	parser.add_option("-s", action="store_true", dest="shell", default=False,
					  help="create shell script that remove dups")
	parser.add_option("-o", "--out", metavar="FILE", dest="log_file",
	                  help="log file name; will not overwrite existing file")
	parser.add_option("--sep", dest="separator", default="\n\t",
	                  help="seperator for duplicated entries; use \\n for newline, \\t for tab [default: \\n\\t]")
	parser.add_option("--sort", action="store_true", dest="sort", default=False,
	                  help="sort filenames in log")
	parser.add_option("-q", "--quote", action="store_true", dest="quote", default=False,
	                  help="quote paths with \" if contain space")
	parser.add_option("-a", "--abs-path", action="store_true", dest="abspath", default=False,
	                  help="save absolute paths")
	parser.add_option("-e", "--exclude", action="append", dest="exclude",
	                  help="exclude given files or patterns; you can pass as many options as you need")
	parser.add_option("--keep", action="store_false", dest="overwrite", default=True,
	                  help="do not overwrite log file if exists")
	parser.add_option("--no-recursive", dest="no_recursive", action="store_true", default=False,
	                  help="do not go deeper")
	parser.add_option("--traceback", dest="print_traceback", action="store_true", default=False,
	                  help="in case of error print full traceback, that can help identify an error")

	# parse
	(options, rest) = parser.parse_args(args)
	
	# check options
	if options.log_file is None:
		parser.error("-o parameter is required")
		raise SystemExit
	elif exists(options.log_file) and not options.overwrite:
		parser.error("File %s already exists." % options.log_file)
		raise SystemExit

	if options.exclude is None:
		options.exclude = []

	options.separator = options.separator.replace("\\n", '\n').replace("\\t", '\t')

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


class Dict(dict):
	"Ocaml-like dict"
	def __setitem__(self, key, value):
		try:
			L = super(Dict, self).__getitem__(key)
		except KeyError:
			L = []
			super(Dict, self).__setitem__(key, L)

		L.append(value)


class Md5Cache:
	"cache for md5 sums of files; md5 sum is recalculated when modification time changed"
	def __init__(self):
		self.cache = {}		# path => (mod. time, md5sum)

	def get_sum(self, filename):
		filename   = abspath(filename)

		file_mtime = getmtime(filename)

		if filename in self.cache:
			cache_mtime, sum = self.cache[filename]
			if cache_mtime == file_mtime:
				return sum

		sum = self.calc_sum(filename)
		self.cache[filename] = (file_mtime, sum)
		return sum
		
	def calc_sum(self, filename):
		file    = open(filename, 'rb')
		bufsize = 8192
		sum     = md5()
		while True:
			buf = file.read(bufsize)
			if not buf:
				break
			sum.update(buf)

		file.close()
		return sum.digest()

	def save(self, filename):
		import pickle
		print("dumping to", filename)
		pickle.dump(self.cache, open(filename, "wb"), pickle.HIGHEST_PROTOCOL)
	
	def load(self, filename):
		import pickle
		self.cache = pickle.load(open(filename, "rb"))


class Md5ShortCache(Md5Cache):
	"cache for md5 sums of first 4kB of files"
	def calc_sum(self, filename):
		file    = open(filename, 'rb')
		bufsize = 4096
		sum     = md5()
		sum.update(file.read(bufsize))
		file.close()
		return sum.digest()


def main():
	options, directories = parse_args(sys.argv)

	# set up print-status function
	class Status:
		def __init__(self, max_width=72):
			self.last_len  = 0
			self.max_width = max_width
			self.progress  = 0.0

			if sys.stdout.isatty():
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
				sys.stdout.write(out + "\r")
			else:
				sys.stdout.write(out + (" "*(self.last_len - n)) + "\r")

			sys.stdout.flush()
			self.last_len = n

		def __print_dummy(self, string, path=""):
			pass

		def error(self, string):
			sys.stdout.write(string + "\n")
	
	status = Status()

	def printerror():
		if options.print_traceback:
			import traceback
			traceback.print_exc()
		else:
			info = sys.exc_info()
			status.error("%s: %s" % (info[0].__name__, info[1]))

	# load md5cache
	md5cache = Md5Cache()
	try:
		md5cache.load("removedups.md5cache")
	except:
		status.error("Can't load md5cache file")
		printerror()

	md5headcache = Md5ShortCache()
	try:
		md5headcache.load("removedups.md5headcache")
	except:
		status.error("Can't load md5headcache file")
		printerror()


	try:
		# Scanning directories

		def match(filename):
			from fnmatch import fnmatch

			for pattern in options.exclude:
				if fnmatch(filename, pattern):
					return False
			else:
				return True

		d = Dict()
		for directory in directories:
			for root, dirs, files in os.walk(directory):
				status.write("Scanning: ", root)
				for file in files:
					if not match(file):		# exclude files
						continue

					path = join(root, file)
					if not islink(path):	# do not consider links
						try:
							if options.abspath:
								d[getsize(path)] = abspath(path)
							else:
								d[getsize(path)] = path
						except:
							printerror()

				if options.no_recursive:	# do not go deeper
					del dirs[:]


		def group_by_first4kb(file_list):
			dict = Dict()

			for file in file_list:
				status.write("read head of ", file)
				try:
					head = md5headcache.get_sum(file)

					dict[head] = file
				except:
					printerror()

			return dict


		def group_by_md5sum(file_list):
			dict = Dict()

			for file in file_list:
				status.write("calc. MD5 of ", file)
				try:
					sum = md5cache.get_sum(file)
					dict[sum] = file
				except:
					printerror()

			return dict


		def group_files(dict):
			duplicates = []
			unique     = []

			total = float(len(dict))
			for curr, (size, files) in enumerate(iter(dict.items())):
				if size == 0:
					continue

				status.progress = curr/total
				if len(files) == 1:
					unique.append(files[0])
					continue

				dict1 = group_by_first4kb(files)
				for _, files1 in dict1.items():
					if len(files) == 1:
						unique.append(files1[0])
						continue

					dict2 = group_by_md5sum(files1)
					for _, files2 in dict2.items():
						if len(files2) > 1:
							duplicates.append(files2)
						else:
							unique.append(files2[0])
					
			return (unique, duplicates)


		unique, duplicates = group_files(d)

		log = open(options.log_file, "wt")

		if options.quote:
			def quote(string):
				if " " in string:
					return '"' + string + '"'
				else:
					return string
		else:
			def quote(string):
				return string


		for file_list in duplicates:
			if options.sort:
				file_list.sort()

			if options.shell:
				f0 = quote(file_list[0])
				for fi in file_list[1:]:
					assert f0 != fi
					log.write("cmp %s %s && rm %s\n" % (f0, fi, fi))
			else:
				log.write(quote(file_list[0]))
				for file in file_list[1:]:
					log.write(options.separator + quote(file))
				else:
					log.write("\n")

		log.close()
		status.write("\n")

	except:
		printerror()

	try:
		md5cache.save("removedups.md5cache")
	except:
		status.error("Can't save md5cache file")
		printerror()
		
	try:
		md5headcache.save("removedups.md5headcache")
	except:
		status.error("Can't save md5headcache file")
		printerror()


if __name__ == '__main__':
	main()

# vim: ts=4 sw=4 nowrap noexpandtab

import sys

help = """
Compare list of strings/directory listings

%s [%s] list1|dir1 list2|dir2

where:
* list is a file that contains list of strings (usually paths)
* dir - directory to scan
* action is:
  - diff or minus [default] - list string from set 1 that not exist in set 2
  - or or sum               - sum of all strings (duplicates removed)
  - and or common           - string that exist in 1 and 2
  - xor                     - set 1 minus 2 or 2 minus 1
"""


def main():
	import os.path as path

	actions = ["diff", "minus", "or", "sum", "xor", "and", "common"]

	def usage(error=None):
		if error:
			print "Error:", error

		print help % (sys.argv[0], "|".join(actions))
		sys.exit(1)


	# parse arguments and load lists
	if len(sys.argv) == 4:
		action = sys.argv[1].lower()
		if action not in actions:
			usage("Invalid action name '%s'" % action)

		list1 = load(sys.argv[2])
		list2 = load(sys.argv[3])

	elif len(sys.argv) == 3:
		action = "diff"
		list1 = load(sys.argv[1])
		list2 = load(sys.argv[2])
	else:
		usage()
	
	
	# do action
	res = set()
	if action in ["diff", "minus"]:
		res = list1 - list2
	elif action in ["or", "sum"]:
		res = list1 | list2
	elif action in ["and", "common"]:
		res = list1 & list2
	elif action == "xor":
		res = list1 ^ list2

	if res:
		print "\n".join(res)


def load(path):
	from os.path import isdir, isfile, exists

	if not exists(path):
		print "Path '%s' does not exists." % path
		sys.exit()

	if isdir(path):
		try:
			return set(load_dir(path))
		except IOError, e:
			print "Can't load contents of directory %s." % path
			print str(e)
			sys.exit(1)

	elif isfile(path):
		try:
			return set(load_file(path))
		except IOError, e:
			print "Can't load contents of file %s." % path
			print str(e)
			sys.exit(1)
	else:
		print path, "is neither directory nor file."
		sys.exit(1)


def load_file(path):
	file = open(path, "rt")
	list = [line.rstrip('\n') for line in file]
	file.close()

	return list


def load_dir(path):
	from os import walk
	from os.path import normpath, join

	path = normpath(path)
	n    = len(path)
	list = []
	for root, files, dirs in walk(path):
		for file in files:
			list.append(join(root[n:], file))
	
	return list


if __name__ == '__main__':
	main()

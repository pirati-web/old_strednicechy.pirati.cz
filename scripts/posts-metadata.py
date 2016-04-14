#!/usr/bin/env python3

import sh # http://amoffat.github.io/sh/
import re
import sys
from glob import glob
from pprint import pprint
from os.path import (join, basename, split)
from markdown import Markdown

__version__ = "0.8.0"
__author__ = "Ondřej Profant"
__doc__ = """
Manipulation with blog posts metadata
"""

rules = {
    'keys': [ ('autor', 'author') ],      # rename of key
    'vals': [ ('layout', 'eu', 'post') ], # change value eu to default in layout
    'add': [ ('date', '2014-10-10') ],	# add key and default value, for example: [ ( 'new-key', 'default'), ('other-key', 'default') ]
    'del': [],
	'func': [  # image modify to basename
        ('image', lambda v, n: basename(v) ),
        ('date',  lambda v, n: re.match('\d{4}-\d{2}-\d{2}', n).group() )
        ]
}
input_dir = "../../old"
output_dir = "new/"


def files_info(files):
	print(sh.file( sh.glob(files )))

def read_file(filename):
	with open(filename) as f:
		file_text = f.read()

	md = Markdown(extensions=['markdown.extensions.meta'])
	text2 = md.convert(file_text)

	return md

def write_file(filename, meta, lines, refs):
	with open(filename, 'w') as f:
		f.write('---\n')
		for (k,v) in meta.items():
			f.write('%s:\t' % k)
			if len(v) == 1:
				f.write('%s\n' % v[0])
		f.write('---\n\n')
		f.write('\n'.join(str(line) for line in lines))
		for (k,v) in refs.items():
			f.write('[%s]: %s\n' % (k, v[0]))

def process_meta_data(meta, rules, name = ''):
	try:
		for r in rules['del']:
			meta.pop(r[0])

		for r in rules['add']:
			meta[r[0]] = [r[1]]

		for r in rules['keys']:
			meta[r[1]] = meta.pop(r[0])

		for r in rules['vals']:
			if meta[r[0]] == [r[1]]:
				meta[r[0]] = [r[2]]
			else:
				print(meta[r[0]])

		for f in rules['func']:
			key = f[0]
			func = f[1]
			if meta[key][0]:  # key exists in meta
				meta[key][0] = func(meta[key][0], name) # modify value by lambda

	except KeyError as e:
		print('Old meta:\n')
		pprint(meta)
		raise e
	return meta

def run(files=None, test=False):
	if not files:
		files = glob( join(input_dir, '*.md') )
	for f in files:
		if test:
			print('Procces file: %s' % f)
		(path, name) = split(f)
		data = read_file(f)
		meta = process_meta_data(data.Meta, rules, name)
		nf = join(output_dir, name)
		if test:
			pprint(meta)
			print('---\n')
		else:
			write_file(nf, meta, data.lines, data.references)

files = sys.argv[1:]
run(files)

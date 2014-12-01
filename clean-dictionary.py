import cPickle as pickle
import re

with open("en-span-dict-cleaned.txt", "r") as dictFile:
	raw = dictFile.read()
	words = raw.split('\n')
	word_def_pairs = [x.split('\t') for x in words]
	word_def_pairs = [[re.sub(r'\[[^)]*\]', '', re.sub(r'\([^)]*\)', '', y)) for y in x] for x in word_def_pairs]
	print word_def_pairs
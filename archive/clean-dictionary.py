import cPickle as pickle
import re

class emptyDict(dict):
	def __missing__(self, key):
		self[key] = []
		return self[key]
		
def slash_split(string):
	if '/' not in string:
		return [string]

	output = []
	splitted = string.split('/')
	if splitted[1] in ['a','o']:
		output = [splitted[0], splitted[0][:-1] + splitted[1]]
	else:
		output = [splitted[0], splitted[0] + splitted[1]]
		
	return output
	

with open("en-span-dict-cleaned.txt", "r") as dictFile:
	raw = dictFile.read()
	words = raw.split('\n')
	word_def_pairs = [x.split('\t') for x in words]
	word_def_pairs = [[re.sub(r'\[[^)]*\]', '', re.sub(r'\([^)]*\)', '', y)) for y in x] for x in word_def_pairs]
	en_span = emptyDict()
	for pair in word_def_pairs:
		if len(pair) == 2:
			en_span[pair[0]] += pair[1].split(",")
	for key in en_span:
		en_span[key] = [y.strip().replace('.','') for y in sum([slash_split(x) for x in en_span[key]],[])]
		
	print en_span#['abbacy']
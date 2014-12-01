import collections
import random
import re
import copy

"""
RandomDict

Similar to collections.defaultdict, but instantiates new keys with a random value between 0 and 1.
"""
class RandomDict(dict):
	def __missing__(self, key):
		self[key] = random.random()
		return self[key]

"""
MachineTranslation

The base class for generating transition probabilities t(f|e) for two languages (i.e. French & English)
in machine translation.

See http://www.cs.columbia.edu/~mcollins/courses/nlp2011/notes/ibm12.pdf for pseudocode algorithm.
"""
class MachineTranslation(object):
	def __init__(self):
		"""
		Initializes the variables

		Args:
			None
		Returns:
			None
		Raises:
			None
		"""
		# language pairings of sentences (each sentence is an ordered list of word tokens)
		self.corpus = None
		# initializing transition probabilities with random variables
		self.t = RandomDict()
		self.q = RandomDict()
		# counts, initialized to 0
		# counts_ef and counts_e utilized in all models (word-specific)
		self.counts_ef = collections.defaultdict(int)
		self.counts_e = collections.defaultdict(int)
		# counts_jilm and counts_ilm utilized only in model 2 (word positions)
		self.counts_jilm = collections.defaultdict(int)
		self.counts_ilm = collections.defaultdict(int)

	def process_text(self, fr_file, en_file):
		"""
		Processes text files and stores info in corpus variable.

		Args:
			fr_file: filename of the French corpus (i.e. the input language)
			en_file: filename of the English corpus (i.e. the output language)
		Returns:
			None
		Raises:
			None
		"""
		with open(fr_file) as f:
			fr_corpus = [self.tokenize(line) for line in f]
		with open(en_file) as f:
			en_corpus = [self.tokenize(line) for line in f]
		assert(len(fr_corpus) == len(en_corpus))
		self.corpus = zip(fr_corpus, en_corpus)

	def calc_delta(self, fr_word, en_word, en_sent, i, j, M, L):
		"""
		Abstract method, implemented in child classes. Calculates the delta value that is
		added to counts in the E step of the EM iteration

		Args:
			fr_word: current french word
			en_word: current english word
			en_sent: current english sentence
			i: position of french word in french sentence
			j: position of english word in english sentence
			M: length of french sentence
			L: length of english sentence
		Returns:
			delta: delta value (differs for Model 1 and Model 2)
		Raises:
			None
		"""
		pass

	def train_model(self):
		"""
		Trains the model by iterating through EM algorithm until t(f|e) and q(j,i,L,M) values converge.

		Args:
			None
		Returns:
			None
		Raises:
			None
		"""
		converged = False
		while not converged:
			# E step
			for fr, en in self.corpus:
				M, L = len(fr), len(en)
				for i in range(1, M + 1):
					for j in range(0, L + 1):
						fr_word = fr[i - 1]
						en_word = None if j == 0 else en[j - 1]
						delta = self.calc_delta(fr_word, en_word, en, i, j, M, L)
						self.counts_ef[(en_word, fr_word)] += delta
						self.counts_e[en_word] += delta
						self.counts_jilm[(j,i,L,M)] += delta
						self.counts_ilm[(i,L,M)] += delta
			# M step
			converged = True
			# update t(e|f) values
			for e, f in self.counts_ef:
				old_ef = self.t[(f,e)]
				self.t[(f,e)] = float(self.counts_ef[(e,f)]) / self.counts_e[e]
				if abs(self.t[(f, e)] - old_ef) > 0.005:
					converged = False
			# update q(j,i,L,M) values
			for j,i,L,M in self.counts_jilm:
				old_jilm = self.q[(j,i,L,M)]
				self.q[(j,i,L,M)] = float(self.counts_jilm[(j,i,L,M)]) / self.counts_ilm[(i,L,M)]
				if abs(self.q[(j,i,L,M)] - old_jilm) > 0.005:
					converged = False
			print "converging"
		print "training complete"

	def tokenize(self, content):
		"""
		Given a string, converts it into an array of alphanumeric tokens (i.e. words).

		Args:
			content: input string
		Returns:
			array of tokens (words)
		Raises:
			None
		"""
		regex = re.compile(r"[0-9a-z-'A-Z]+")
		token_list = regex.findall(content)
		return [w.strip().lower() for w in token_list]

	def print_word_pairings(self):
		match = {}
		for fr, en in self.t:
			if en not in match or (en in match and match[en][1] < self.t[(fr, en)]):
				match[en] = (fr, self.t[(fr, en)])
		print match

	def best_alignment(self, fr_str, en_str):
		fr_tokens = self.tokenize(fr_str)
		en_tokens = self.tokenize(en_str)
		alignment = []
		for fr_index, fr_t in enumerate(fr_tokens):
			max_pos = 0
			max_val = self.calc_align_prob(fr_index + 1, fr_t, len(fr_tokens), 0, None, len(en_tokens))
			for en_index, en_t in enumerate(en_tokens):
				align_prob = self.calc_align_prob(fr_index + 1, fr_t, len(fr_tokens), en_index + 1, en_t, len(en_tokens))
				if align_prob > max_val:
					max_pos = en_index + 1
					max_val = self.calc_align_prob(fr_index + 1, fr_t, len(fr_tokens), en_ind, None, len(en_tokens))
			alignment.append(max_pos)
		return alignment

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		pass

"""
Model1

Inherits from MachineTranslation, only calculates transition probabilities based on the respective
french and english words themselves.
"""
class Model1(MachineTranslation):
	def calc_delta(self, fr_word, en_word, en_sent, i, j, M, L):
		"""
		Calculates delta value according to Model 1. (For full comment, see method in parent class MachineTranslation)
		"""
		numerator = self.t[(fr_word, en_word)]
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.t[(fr_word, en_sent[ind_j - 1])]
		return float(numerator) / denominator

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		return self.t[(fr_t, en_t)]

class Model2(MachineTranslation):
	def calc_delta(self, fr_word, en_word, en_sent, i, j, M, L):
		"""
		Calculates delta value according to Model 2. (For full comment, see method in parent class MachineTranslation)
		"""
		numerator = self.t[(fr_word, en_word)] * self.q[(j,i,L,M)]
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.q[(ind_j, i, L, M)] * self.t[(fr_word, en_sent[ind_j - 1])]
		return float(numerator) / denominator

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		return self.t[(fr_t, en_t)] * self.q[(en_index, fr_index, en_len, fr_len)]

def train_consecutive_models(fr_file, en_file):
	"""
	Consecutively runs model 1 and model 2 on test files.

	Args:
		fr_file: filename of the French corpus (i.e. the input language)
		en_file: filename of the English corpus (i.e. the output language)
	Returns:
		the two model objects (model1, model2, each with transition probabilities stored inside)
	Raises:
		None
	"""
	# train model 1
	model1 = Model1()
	model1.process_text(fr_file, en_file)
	model1.train_model()
	# copy data from model 1 and train model 2
	model2 = Model2()
	model2.corpus = model1.corpus
	model2.t = copy.deepcopy(model1.t)
	model2.q = copy.deepcopy(model1.q)
	model2.train_model()
	return model1, model2

def main():
	"""
	Runs machine translation algorithm.

	Args:
		None
	Returns:
		None
	Raises:
		None
	"""
	print "Starting training..."
	model1, model2 = train_consecutive_models("spanish.txt", "english.txt")
	# show transition probabilities
	print "MODEL 1 TRANSITION PROBABILITIES"
	print model1.t
	print "MODEL 2 TRANSITION PROBABILITIES"
	print model2.t
	model1.print_word_pairings()
	model2.print_word_pairings()

if __name__ == "__main__":
	main()

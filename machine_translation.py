import collections
import random
import re
import timing
import copy
import os
import cPickle as pickle

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

	def make_denominator(self, fr_word, en_word, en_sent, i, j, M, L):
		"""

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
					fr_word = fr[i - 1]
					denominator = self.make_denominator(fr_word, en, i, M, L)
					for j in range(0, L + 1):
						en_word = None if j == 0 else en[j - 1]
						delta = self.calc_delta(fr_word, en_word, en, i, j, M, L, denominator)
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
		"""
		Print out all transition probabiltiies P(fr|en).

		Args:
			None
		Returns:
			None
		Raises:
			None
		"""
		match = {}
		for fr, en in self.t:
			if en not in match or (en in match and match[en][1] < self.t[(fr, en)]):
				match[en] = (fr, self.t[(fr, en)])
		print match

	def best_alignment(self, fr_str, en_str):
		"""
		Given a pair of english and non-english sentences, returns an array of the alignment
		(this has the length of the non-english sentence, where each value corresponds to the
		index of the word in the english sentence which it matches, 0 being None)

		Args:
			fr_str: non-english string
			en_str: english string that is the translation of fr_str
		Returns:
			alignment: array of alignment values
		Raises:
			None
		"""
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
					max_val = self.calc_align_prob(fr_index + 1, fr_t, len(fr_tokens), en_index + 1, en_t, len(en_tokens))
			alignment.append(max_pos)
		return alignment

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		"""
		Abstract method, implemented in child classes. Calculates the probability value that is
		maximized to determine optimal alignments

		Args:
			fr_index: index in french sentence (starting at 1)
			fr_t: french word
			fr_len: length of french sentence
			en_index: index in english sentence (starting at 1)
			en_t: english word
			en_len: length of english sentence
		Returns:
			value that is meant to be maxed (we're choosing the english word that maxes this value)
		Raises:
			None
		"""
		pass

	def generate_phrase_table(self, output_file):
		"""
		Generates the t(f|e) translation probabilities in a format that can be read by the Pharaoh decoder.

		Args:
			output_file: filename for the phrase table tranlation model
		Returns:
			None
		Raises:
			None
		"""
		with open(output_file, "w") as f:
			# unigram_prob_f = open(unigram_prob_file, "rb")
			# unigram_prob = pickle.load(unigram_prob_f)
			# unigram_prob_f.close()			
			for (fr_token, en_token) in self.t:
				if self.t[(fr_token, en_token)] > 0.01:
					f.write("{0} ||| {1} ||| {2}\n".format(fr_token, en_token, self.t[(fr_token, en_token)]))

"""
Model1

Inherits from MachineTranslation, only calculates transition probabilities based on the respective
french and english words themselves.
"""
class Model1(MachineTranslation):
	def calc_delta(self, fr_word, en_word, en_sent, i, j, M, L, denominator):
		"""
		Calculates delta value according to Model 1. (For full comment, see method in parent class MachineTranslation)
		"""
		numerator = self.t[(fr_word, en_word)]
		"""
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.t[(fr_word, en_sent[ind_j - 1])]
			"""
		return float(numerator) / denominator
		
	def make_denominator(self, fr_word, en_sent, i, M, L):
		"""
		"""
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.t[(fr_word, en_sent[ind_j - 1])]
		return denominator

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		"""
		Calculates value to be optimized for alignments, according to Model 1.
		(For full comment, see method in parent class MachineTranslation)
		"""
		return self.t[(fr_t, en_t)]

class Model2(MachineTranslation):
	def calc_delta(self, fr_word, en_word, en_sent, i, j, M, L, denominator):
		"""
		Calculates delta value according to Model 2. (For full comment, see method in parent class MachineTranslation)
		"""
		numerator = self.t[(fr_word, en_word)] * self.q[(j,i,L,M)]
		"""
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.q[(ind_j, i, L, M)] * self.t[(fr_word, en_sent[ind_j - 1])]
			"""
		return float(numerator) / denominator
		
	def make_denominator(self, fr_word, en_sent, i, M, L):
		"""
		Calculates delta value according to Model 2. (For full comment, see method in parent class MachineTranslation)
		"""
		denominator = self.q[(0, i, L, M)] * self.t[(fr_word, None)]
		for ind_j in range(1, L + 1):
			denominator += self.q[(ind_j, i, L, M)] * self.t[(fr_word, en_sent[ind_j - 1])]
		return denominator

	def calc_align_prob(self, fr_index, fr_t, fr_len, en_index, en_t, en_len):
		"""
		Calculates value to be optimized for alignments, according to Model 2.
		(For full comment, see method in parent class MachineTranslation)
		"""
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
	if os.path.isfile("model2.p"):
		print "opening pickles"
		model1_file = open("model1.p", "rb")
		model2_file = open("model2.p", "rb")
		model1_pickle = pickle.load(model1_file)
		model2_pickle = pickle.load(model2_file)
		model1_file.close()
		model2_file.close()

		# copy models because pickle files have old function implementations
		# model1 = Model1()
		# model2 = Model2()
		# model1.t = copy.deepcopy(model1_pickle.t)
		# model1.q = copy.deepcopy(model1_pickle.q)
		# model2.t = copy.deepcopy(model2_pickle.t)
		# model2.q = copy.deepcopy(model2_pickle.q)

		model1_pickle.generate_phrase_table("phrase-table-model1")
		model2_pickle.generate_phrase_table("phrase-table-model2")
		# print model1.best_alignment("yo no soy organizado", "I am not organized")
		# print model2.best_alignment("yo no soy organizado", "I am not organized")
	else:
		print "Starting training..."
		model1, model2 = train_consecutive_models("spanish1000.txt", "english1000.txt")
		model1_file = open("model1.p", "wb")
		model2_file = open("model2.p", "wb")
		pickle.dump(model1, model1_file)
		pickle.dump(model2, model2_file)
		model1_file.close()
		model2_file.close()

		# show transition probabilities
		print "MODEL 1 TRANSITION PROBABILITIES"
		print model1.t
		print "MODEL 2 TRANSITION PROBABILITIES"
		print model2.t
		model1.print_word_pairings()
		model2.print_word_pairings()


if __name__ == "__main__":
	main()

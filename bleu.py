from __future__ import division
import sets;
import re;

class BLEU:
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
		self.machine_file = None;
		self.human_file = None;
		self.N = 4;

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

	def set_files(self, human_file, machine_file):
		self.human_file = open(human_file);
		self.machine_file = open(machine_file);

	def calculate_score(self):
		"""
		Assigns a score based on the accuracy of machine translation in self.machine_file.

		Args:
			None
		Returns:
			score value from 0.0 to 1.0.
		Raises:
			None
		"""
		score_denom = 0;
		score_num = 0;
		for human_line in self.human_file:
			machine_line = self.machine_file.readline();
			score = self.line_score(self.tokenize(human_line), self.tokenize(machine_line));
			if not score == -1:
				score_num += score;
				score_denom += 1;
		return score_num / score_denom;

	def line_score(self, human, machine):
		"""
		Takes a sentence, assigns a score on the accuracy of the machine translation.

		Args:
			human: list of tokenized words in a sentence
			machine: list of tokenized words in a sentence
		Returns:
			score value from 0.0 to 1.0. -1 if human or machine too short
		Raises:
			None
		"""
		if len(human) < self.N or len(machine) < self.N:
			return -1;
		human_set = {};
		for i in range(0, len(human) - self.N + 1):
			entry = "";
			for j in range(0, self.N):
				entry += human[i+j] + "|";
			if entry in human_set:
				human_set[entry] += 1;
			else:
				human_set[entry] = 1;

		score_denom = 0;
		score_num = 0;
		for i in range(0, len(machine) - self.N + 1):
			entry = "";
			for j in range(0, self.N):
				entry += machine[i+j] + "|";
			if entry in human_set and not human_set[entry] == 0:
				score_num += 1;
				human_set[entry] - 1;
			score_denom += 1;
		print score_num, "/", score_denom;
		return score_num / score_denom;

def main():
	b = BLEU();
	b.set_files("english-test.txt", "./pharaoh-v1.2.3/out.txt");
	score = b.calculate_score();
	print "score is", score;

if __name__ == "__main__":
	main()

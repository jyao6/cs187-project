"""
  Language Model
  Wilson Qin
"""

from collections import defaultdict
import re
import pprint
import sys

pp = pprint.PrettyPrinter(indent=4)

param_base_lang_fp = "data/english.txt"

param_pad_sym = "<s>"
param_n_gram_len = 3

param_total = "*total*"

def tokenize(content):
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


def gram_pad(sentence, n):
  """
    pad a sentence for an n-gram (n-1 blank word pads)

    args:
      sentence - a list of words(strings)
      n - ngram to pad, n-1 number of words to pad

    returns:
      padded sentence: list of words

    raises:
  """
  # start pad
  spad = []
  for i in xrange(0, n-1, 1):
    spad.append(param_pad_sym)

  # end pad
  epad = []
  for i in xrange(0, n-1, 1):
    epad.append(param_pad_sym)

  return spad + string + epad

def get_corpus(base_lang_fp):
  """
    seeding corpus

    args:
      base_lang_fp - filepath to the base language corpus
      trans_lang_fp - filepath to the translated language corpus

    returns:
      corpus - list of list of strings

    raises:
      FileException if either base_lang_fp non existent
  """
  with open(base_lang_fp, "r") as b_f:
    return [tokenize(line) for line in b_f.readlines()]


def count_n_grams(corpus, n):
  """
    tallies n-grams in a corpus

    args:
      corpus - a list of list of strings
      n - an integer
  
    return:
      a dict with key as a n-tuple
  """

  ngram_counts = defaultdict(int)

  for sentence in corpus:
    for i in xrange(0,len(sentence)-n+1,1):
      ngram = ()
      for j in xrange(0,n,1):
        ngram = ngram + (sentence[i+j],)

      ngram_counts[ngram] += 1

  return ngram_counts

def get_cond_prob(ngram_counts, n):
  """
    gets cond probabilities of n-grams from a ngram_count

    args:
      corpus - a list of list of strings
      n - an integer
  
    return:
      a dict with key as a n-tuple
  """
  count_dict = defaultdict(lambda: defaultdict(float))
  prob_dict = defaultdict(lambda: defaultdict(float))
  lexicon = set()
  cond_key = None
  for tup, count in ngram_counts.iteritems():
    cond_key = tup[0:n-1]
    lexicon = lexicon.union([tup[0]])
    count_dict[cond_key][tup[n-1]] += count
    count_dict[cond_key][param_total] += count

  for cond_key, innerdict in count_dict.iteritems():
    for word, count in innerdict.iteritems():
      if word != param_total:
        key = " ".join(list(cond_key + (word,)))
        prob_dict[key] = count_dict[cond_key][word] / count_dict[cond_key][param_total]

  return prob_dict


def main():
  """
    runs the language model

    args: None

    return: 
      void, prints to screen

    raises:
  """

  corpus = get_corpus(param_base_lang_fp)

  pp.pprint(get_cond_prob(count_n_grams(corpus, param_n_gram_len), param_n_gram_len))

if __name__ == "__main__":
  # if sys.argv[2] and sys.argv[3] and sys.argv[4]:
  #   if sys.argv[2] == "t":
  #     main(sys.argv[2])
  #   elif sys.argv[2] == "p":
  #     param_base_lang_fp = 
  #     corpus = get_corpus(param_base_lang_fp)
  # except:
  #   print "usage: python language_model.py <t/p> <corpus-filepath> <output-filepath>"
  #   exit()
  main()

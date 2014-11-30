"""
  Language Model
"""

from collections import defaultdict

import pprint

pp = pprint.PrettyPrinter(indent=4)

param_base_lang_fp = "../data/english.txt"
param_trans_lang_fp = "../data/spanish.txt"

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
    return map(lambda a: a.split(" "), b_f.read().split("\n"))


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

      print ngram

      ngram_counts[ngram] += 1

  return ngram_counts

def main():
  """
    runs the language model

    args: None

    return: 
      void, prints to screen

    raises:
  """

  corpus = get_corpus(param_base_lang_fp)

  pp.pprint(count_n_grams(corpus, 3))

if __name__ == "__main__":
  main()

"""
  MT IBM Model 1
  Wilson Qin
"""

import numpy as np
import scipy as spy

import sys
import re

from collections import defaultdict
import pprint

pp = pprint.PrettyPrinter(indent=4)

param_base_lang_fp = "data/english.txt"
param_trans_lang_fp = "data/spanish.txt"

param_cutout = 50
param_filter_prob_thresh = 0.01

class LanguageModel:
  """ Language Model Stub """
  def __init__(self, fp):
    """
      initializes the instance by seeding corpus

      args:
        fp - filepath to the base language corpus

      returns:
        instance

      raises:
        FileException if either base_lang_fp or trans_lang_fp non-existant
    """

  def prob(word):
    """
      gets the probability of a word

      args:
        base_lang_fp - filepath to the base language corpus
        trans_lang_fp - filepath to the translated language corpus

      returns:
        instance

      raises:
        FileException if either base_lang_fp or trans_lang_fp non-existant
    """
    ##### STUB ##### TODO - fill out with real probabilities from a corpus
    return 1.0

class Model1:
  """ IBM Model 1 Class, lexical translation model """

  def __init__(self, base_lang_fp, trans_lang_fp):
    """
      initializes the instance by seeding corpuses and compiling working dictionaries

      args:
        base_lang_fp - filepath to the base language corpus
        trans_lang_fp - filepath to the translated language corpus

      returns:
        instance

      raises:
        FileException if either base_lang_fp or trans_lang_fp non-existant
    """
    with open(base_lang_fp, "r") as b_f, open(trans_lang_fp, "r") as t_f:
      self.base_corpus = map(lambda a: a.split(" "), b_f.read().split("\n"))
      self.trans_corpus = map(lambda a: a.split(" "), t_f.read().split("\n"))

      self.set_dict()

  def set_dict(self):
      """
        compile the instance's base and translation language dictionaries

        args: None
        return: void
        raises:
      """
      uniq_wds = frozenset([])
      for s in self.trans_corpus:
        uniq_wds = uniq_wds.union(s)
      self.trans_dict = uniq_wds

      uniq_wds = frozenset()
      for s in self.base_corpus:
        uniq_wds = uniq_wds.union(s)
      self.base_dict = uniq_wds

  def em_trans_prob(self, cutout):
    """
      Generate translation probabilities, up to `cutout` iteration for convergence

      args:
        cutout - an int for the convergence iterations cut out limit

      return:
        a defaultdict of translation probabilities, representing t(e-base|f-target)
        
      raises:
    """

    # t(e|f) table, initialize uniformly with equivalent probabilities
    trans_probs = defaultdict(float)
    norm_divisor = len(self.base_dict) * len(self.trans_dict)
    for bw in self.base_dict:
      for tw in self.trans_dict:
        trans_probs[(bw, tw)] = 1.0 / norm_divisor


    i = 0

    # this is the convergence loop
    while i < cutout:
      # instantiate count table for all alignment pairs
      count_table = defaultdict(float)

      # instantiate total table for potential translation words
      total_table = defaultdict(float)

      # this is a counting, permuting all possible alignments

      #iterate through all sentence pairs
      for b_sentence, t_sentence in zip(self.base_corpus, self.trans_corpus):
        # compute a normalization
        s_total = defaultdict(float)
        for bw in b_sentence:
          for tw in t_sentence:
            s_total[bw] += trans_probs[(bw,tw)]

        for bw in b_sentence:
          for tw in t_sentence:
            norm_trans_probs = (trans_probs[(bw, tw)] / s_total[bw])
            count_table[(bw, tw)] += norm_trans_probs
            total_table[tw] += norm_trans_probs

      # recompute the t(e|f) 
      for tw in self.trans_dict:
        for bw in self.base_dict:
          trans_probs[(bw, tw)] = count_table[(bw, tw)] / total_table[tw]
      i += 1


    return trans_probs

  def translate(self, trans_probs, language_model, base_sentences):
    """
      expectation maximization over the transition probabilites with language model applied

      args:
        trans_probs - a defaultdict with float values b/t 0.0 - 1.0
        language_model - a language model
        base_sentences - list of sentences to translate from base into trans language

      return:
        list of translated sentences

      raises:
    """
    ####### STUB ######## - TODO - use this for actual translation, for the test dataset

    for bs in base_sentences:
      for bw in bs:
        # maximum = 0.0
        # tword = None
        # for tw in self.trans_dict:
        #   if trans_probs[(bw, tw)]*language_model.prob(bw) > maximum:
        #     maximum = trans_probs[(bw, tw)]*language_model.prob(bw)
        #     tword = tw
        # print tw, maximum
        pass


    return []

def filter_probs(trans_probs, del_thresh):
  """
    filters a translation probability table to a more readable size, by deleting on a threshold

    args:
      trans_probs - a defaultdict with float values b/t 0.0 - 1.0
      del_thresh - threshold under which probabilities are deleted, float between 0.0 - 1.0

    return:
      trans_probs as a filtered defaultdict, note this modifies trans_probs in place

    raises:
  """

  rem_keys = []

  for key, prob in trans_probs.iteritems():
    if prob < del_thresh:
      rem_keys.append(key)

  [trans_probs.pop(key) for key in rem_keys]

  return trans_probs

def main():
  """
    runs the Machine Translation with an Model1 instance, invoking EM

    args: None

    return: 
      void, prints to screen

    raises:
  """

  lm = Model1(param_base_lang_fp, param_trans_lang_fp)

  # Run EM Algorithm
  # then casting the filtered translation probabilities to a dict, for clarity and print
  pp.pprint(dict(filter_probs(lm.em_trans_prob(param_cutout), param_filter_prob_thresh)))

if __name__ == "__main__":
  main()

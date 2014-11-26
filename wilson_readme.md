Machine Translation IBM Model 1 + 2
================

Wilson Qin, individual implementation

TO RUN:
python ibm1.py

Will run the IBM Model 1, and produce the translation probabilities with english as the base language, and spanish as the target language from the respective training sets.
The Expectation Maximization will be run until convergence, under a user specified bound for trial depth.

So far, the program is not fully supported to run on a test dataset yet (doing actual translation). 
Forthcoming will also be functionality to calculate the precision and recall of the translated test sets, as well as the BLEU metric calculations.

Notes:
  What's working:
    -IBM Model 1
      -IBM Lexical Translation Model 1 converges on translation probabilites on our small toy dataset. 
      -training dataset for model 1

  What's stubbed:
    -IBM Model 1
      -Language Model from a separate language corpus to get p(e), e belonging to base_language

  What's missing:
    -IBM Model 1
      -test runner for test dataset
      -precision/recall metrics
      -BLEU metric

    -IBM Model 2
      -when alignment probabilities need to be abstracted out, and dynamically computed
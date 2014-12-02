import re

fr_file = "spanish-test.txt"
en_file = "english-test.txt"

def tokenize(content):
  regex = re.compile(r"[0-9a-z-'A-Z]+")
  token_list = regex.findall(content)
  return [w.strip().lower() for w in token_list]

def main():
  with open(fr_file) as f:
    fr_corpus = [tokenize(line) for line in f]
  with open(en_file) as f:
    en_corpus = [tokenize(line) for line in f]

  with open("sanitized-"+fr_file, 'w') as f:
    for line in fr_corpus:
      f.write(" ".join(line) + "\n")
    f.close()

  with open("sanitized-"+en_file, 'w') as f:
    for line in en_corpus:
      f.write(" ".join(line) + "\n")
    f.close()

main()

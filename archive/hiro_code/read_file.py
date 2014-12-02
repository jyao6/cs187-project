import random;
import re;
import pickle;
import time;

def jilm_key(j, i, l, m):
	return str(j) + "|" + str(i) + "," + str(l) + "," + str(m);

def ilm_key(i, l, m):
	return str(i) + "," + str(l) + "," + str(m);

def del_kij_denom_func(k, i, model):
	global t;
	global q;
	global en_corpus;
	global sp_corpus;
	del_kij_denom = 0;
	sp_word = sp_corpus[k][i];
	m = len(sp_corpus[k]);
	l = len(en_corpus[k]);

	for j in range(0, l):
		en_word = en_corpus[k][j];
		if model == 1:
			del_kij_denom += t[sp_word + "|" + en_word];
		elif model == 2:
			del_kij_denom += t[sp_word + "|" + en_word]*q[jilm_key(j,i,l,m)];
		else:
			print "model neither 1 or 2";
			sys.exit();

	return del_kij_denom;

def del_kij_num_func(k, i, j, model):
	global t;
	global q;
	global en_corpus;
	global sp_corpus;
	sp_word = sp_corpus[k][i];
	en_word = en_corpus[k][j];
	m = len(sp_corpus[k]);
	l = len(en_corpus[k]);
	if model == 1:
		return t[sp_word + "|" + en_word];
	elif model == 2:
		return t[sp_word + "|" + en_word] * q[jilm_key(j,i,l,m)];
	else:
		print "model neither 1 or 2";
		sys.exit();

def tokenize(input_str):
	pat = r"[a-zA-Z]+|.";
	tokens = [];
	for substr in input_str:
		tokens.extend(re.findall(pat, substr));
	return tokens;


CORPUS_SIZE =  500; # Number of sentencsp to include in the corpus.
ITERATION = 5;
T_FILENAME = "t_file";
Q_FILENAME = "q_file";
SP_FILENAME = '../data/spanish.txt';
EN_FILENAME = '../data/english.txt';


en_file = open(EN_FILENAME, 'r');
sp_file = open(SP_FILENAME, 'r');

en_corpus = [];
sp_corpus = [];

for k in range (0, CORPUS_SIZE):
	sp_sentence = tokenize(sp_file.readline().split());
	sp_corpus.append(sp_sentence);
	en_sentence = tokenize(en_file.readline().split());
	en_sentence.insert(0, "NULL");
	en_corpus.append(en_sentence);

# First implement model 1.

# Initialize t(s|e) to random valusp, and c_sp c_e, c_jilm, c_ilm to 0.
t = {};
q = {};
c_e = {};
c_sp = {};
c_jilm = {};
c_ilm = {};

for k in range (0, len(en_corpus)):
	en_sentence = en_corpus[k];
	sp_sentence = sp_corpus[k];
	l = len(en_sentence);
	m = len(sp_sentence);
	for j in range (0,l):
		en_word = en_sentence[j];
		c_e[en_word] = 0;
		for i in range (0,m):
			sp_word = sp_sentence[i];
			t[sp_word + "|" + en_word] = random.random();
			c_sp[en_word + "," + sp_word] = 0;
			c_jilm[jilm_key(j,i,l,m)] = 0;
			q[jilm_key(j,i,l,m)] = random.random();
			if (j == 0):
				c_ilm[ilm_key(i,l,m)] = 0;

print ("parameters initialized");

# Refine parameters for 5 iterations. First iteration model 1, model 2
# for the rest.

for iteration_count in range(0, ITERATION):
	if iteration_count == 0:
		model_type = 1;
	else:
		model_type = 2;

	for k in range (0, CORPUS_SIZE):
		m_k = len(sp_corpus[k]);
		l_k = len(en_corpus[k]);
		for i in range (0, m_k):
			sp_word = sp_corpus[k][i];
			del_kij_denom = del_kij_denom_func(k, i, model_type);
			for j in range (0, l_k):
				en_word = en_corpus[k][j];
				del_kij_num = del_kij_num_func(k, i, j, model_type);
				del_kij = del_kij_num / del_kij_denom;
				c_sp[en_word+","+sp_word] += del_kij;
				c_e[en_word] += del_kij;
				c_jilm[jilm_key(j,i,l_k,m_k)] += del_kij;
				c_ilm[ilm_key(i,l_k,m_k)] += del_kij;

	for pair_key in t.keys():
		sp_word = pair_key.split("|")[0];
		en_word = pair_key.split("|")[1];
		t[pair_key] = c_sp[en_word+","+sp_word] / c_e[en_word];

	for key in q.keys():
		q[key] = c_jilm[key] / c_ilm[key.split("|")[1]];

	print str(iteration_count) + "th iteration done.";

dump_file = open(T_FILENAME, 'w');
pickle.dump(t, dump_file);
dump_file.close();

dump_fileq = open(Q_FILENAME, 'w');
pickle.dump(q, dump_fileq);
dump_fileq.close();

print "done";
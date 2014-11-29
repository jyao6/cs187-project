import pickle;

f = open("t_file");

t = pickle.load(f);

for k, v in sorted(t.items(), key=lambda x:x[1]):
	print k, v
	#if k.endswith("|Strasbourg"):
	#    print k, v


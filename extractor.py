# import stanfordnlp

# config = {
# 	'processors': 'tokenize,mwt,pos,lemma,depparse',
# 	'lang': 'en',
# 	'tokenize_model_path': '../en_ewt_models/en_ewt_tokenizer.pt', 
# 	'pos_model_path': '../en_ewt_models/en_ewt_tagger.pt',
# 	'pos_pretrain_path': '../en_ewt_models/en_ewt.pretrain.pt',
# 	'lemma_model_path': '../en_ewt_models/en_ewt_lemmatizer.pt',
# 	'depparse_model_path': '../en_ewt_models/en_ewt_parser.pt',
# 	'depparse_pretrain_path': '../en_ewt_models/en_ewt.pretrain.pt'
# }

class Word:
	def __init__(self, w, i, g, r):
		self.text = w
		self.index = i
		self.governor = g
		self.dependency_relation = r


class Sentence:
	def __init__(self, L):
		self.words = list()
		for i, l in enumerate(L):
			w, g, r = l.strip('()').split('|')
			w = w.strip('\' ')
			g = g.strip('\' ')
			r = r.strip('\' ')
			self.words.append(Word(w, i + 1, g, r))


class DependencyTree:
	def __init__(self, word=None, index=None, parent=None, parent_rel=None):
		self.word = word
		self.index = index
		self.parent = parent
		self.parent_rel = parent_rel
		self.children = list()

	def __repr__(self):
		s = '<Node word={:s}; index={:d}; Parent = {:d}; Dependency relation = {:s}>\n'.format(self.word, 
																								self.index
																									if not self.index is None
																									else -1, 
																								self.parent.index 
																									if not self.parent is None and not self.parent.index is None 
																									else 0, 
																								self.parent_rel
																									if not self.parent is None 
																									else 'root')
		return s + ''.join([t.__repr__() for t in self.children])

	def __get_sentence(self, exclude):
		if (self.word, self.index) in exclude:
			return []
		l = [(self.word, self.index)]
		for v in self.children:
			l.extend(v.__get_sentence(exclude))
		return l

	def get_sentence(self, exclude=[]):
		l = self.__get_sentence(exclude)
		l.sort(key=lambda x: x[1])
		return ' '.join([i[0] for i in l])

	@staticmethod
	def from_graph(G, root):
		n = DependencyTree(root[0], root[1], None)
		try:
			for v, r in G[root]:
				n.children.append(DependencyTree.from_graph(G, v))
				n.children[-1].parent = n
				n.children[-1].parent_rel = r
		except KeyError:
			pass
		return n
	
	@staticmethod
	def from_sentence(sentence):
		G1 = dict()
		for w in sentence.words:
			G1[(w.text, int(w.index))] = ((sentence.words[int(w.governor) - 1].text, int(w.governor)), w.dependency_relation)
		
		G2 = dict()
		for v in G1:
			u, r = G1[v]
			if r == 'root':
				G2[('.', 0)] = [(u, r)]
			try:
				G2[u].append((v, r))
			except:
				G2[u] = [(v, r)]
		
		return DependencyTree.from_graph(G2, G2[('.', 0)][0][0])
	
	def search_node(self, word, index=None):
		if self.word == word:
			if index is None or (not index is None and self.index == index):
				return self
		for n in self.children:
			r = n.search_node(word, index)
			if not r is None:
				return r
		
		return None
	
	def match(self, T):
		if self.word == T.word:
			if len(self.children) == len(T.children):
				t = True
				for i in range(len(self.children)):
					t = t and (self.children[i].parent_rel == T.children[i].parent_rel and self.children[i].match(T.children[i]))
				return t
		return False

class Template:
	def __init__(self, s):
		l = s.split(',')
		self.dm = DependencyTree(l[0], 0)
		self.S2_dm = l[1] if len(l[1]) > 0 else None
		self.S1_S2 = l[2] if len(l[2]) > 0 else None
		self.S1_dm = l[3] if len(l[3]) > 0 else None
		self.S2_S1 = l[4] if len(l[4]) > 0 else None
		self.dm_S2 = l[5] if len(l[5]) > 0 else None
		i = 6
		while i < len(l):
			next_dm = l[i]
			next_dm_parent = l[i + 1]
			next_dm_rel = l[i + 2]
			parent = self.dm.search_node(next_dm_parent)
			parent.children.append(DependencyTree(next_dm, i // 3, parent, next_dm_rel))
			i += 3
	
	def __repr__(self):
		return '(dm = {:s}, S2->dm = {:s}, S1->S2 = {:s}, S1->dm = {:s}, S2->S1 = {:s}, dm->S2 = {:s})'.format(
			self.dm.word,
			self.S2_dm if not self.S2_dm is None else 'None',
			self.S1_S2 if not self.S1_S2 is None else 'None',
			self.S1_dm if not self.S1_dm is None else 'None',
			self.S2_S1 if not self.S2_S1 is None else 'None',
			self.dm_S2 if not self.dm_S2 is None else 'None'
		)
	
	def get_sentence_pair(self, tree):
		if not self.S2_dm is None:
			# print("entered")
			dm_node = tree.search_node(self.dm.word)
			if self.dm.match(dm_node):
				# print("Matched")
				if not dm_node.parent is None and dm_node.parent_rel == self.S2_dm:
					# print("Matched S2")
					if not dm_node.parent.parent is None and dm_node.parent.parent_rel == self.S1_S2:
						# print("Matched S1")
						return dm_node.parent.parent.get_sentence(exclude=[(dm_node.parent.word, dm_node.parent.index)]), dm_node.parent.get_sentence(exclude=[(dm_node.word, dm_node.index)])
		elif not self.S1_dm is None and not self.S2_S1 is None:
			dm_node = tree.search_node(self.dm.word)
			if self.dm.match(dm_node):
				if not dm_node.parent is None and dm_node.parent_rel == self.S1_dm:
					if not dm_node.parent.parent is None and dm_node.parent.parent_rel == self.S2_S1:
						return dm_node.parent.parent.get_sentence(exclude=[(dm_node.parent.word, dm_node.parent.index)]), dm_node.parent.get_sentence(exclude=[(dm_node.word, dm_node.index)])
		elif not self.S1_dm is None and not self.dm_S2 is None:
			dm_node = tree.search_node(self.dm.word)
			if self.dm.match(dm_node):
				if not dm_node.parent is None and dm_node.parent_rel == self.S1_dm:
					for v in dm_node.children:
						if v.parent_rel == self.dm_S2:
							return dm_node.parent.get_sentence(exclude=[(dm_node.word, dm_node.index)]), v.get_sentence()
		elif not self.S1_dm is None and not self.S1_S2 is None:
			dm_node = tree.search_node(self.dm.word)
			if self.dm.match(dm_node):
				if not dm_node.parent is None and dm_node.parent_rel == self.S1_dm:
					for v in dm_node.parent.children:
						if v.parent_rel == self.S1_S2:
							return dm_node.parent.get_sentence(exclude=[(dm_node.word, dm_node.index)]), v.get_sentence()
		else:
			return '', ''

sentence = Sentence("""जिन|2|det
व्यक्तियों|6|nmod
और|4|cc
समुदायों|2|conj
की|2|case
आत्मछवि|7|nsubj
पिछड़े|12|acl:relcl
की|7|case
नहीं|10|advmod
थी|7|cop
,|10|punct
वे|17|nsubj
भी|12|dep
पिछड़ा|15|compound
बनने|17|obl
में|15|mark
जुट|0|root
गए|17|aux
हैं|18|aux:pass""".split('\n'))
spec = 'और,cc,conj,,'
template = Template(spec)
tree = DependencyTree.from_sentence(sentence)
s1, s2 = template.get_sentence_pair(tree)
print(s1, s2, sep='\n')



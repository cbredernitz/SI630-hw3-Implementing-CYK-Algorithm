import sys
import math
import numpy as np
from nltk.tree import *
from collections import Counter


def load_grammar(filename):
	'''
	load grammar that following CNF
	return a dict = {(A, (B, C)): prob, (A, a): prob}
	A, B and C represent non-terminal rules and a is lexicon
	prob is  normalized probability
	'''
	# ...(TASK) load grammar and return normalized probability for each production rule

	grammarProb = {}
	each_prob = {}
	f = open(filename, 'r', encoding = 'utf-8')
	for line in f.read().split('\n'):
		lst = line.split()
		if len(lst) == 4:
			grammarProb[(lst[1], (lst[2], lst[3]))] = int(lst[0])
			each_prob[lst[1]] = each_prob.get(lst[1], 0) + 1
		elif len(lst) == 3:
			grammarProb[(lst[1], lst[2])] = int(lst[0])
			each_prob[lst[1]] = each_prob.get(lst[1], 0) + 1

	for element in grammarProb.keys():
		for ele in each_prob:
			if element[0] == ele:
				grammarProb[element] = np.log(grammarProb[element]/each_prob[ele])

	# print(grammarProb)
	print(each_prob)

	return grammarProb

def parse(words, grammar):
	invalidParse = False
	sentenceLen = len(words)

	# ...initialize score table and backpointer table
	score = [[{} for i in range(sentenceLen+1)] for j in range(sentenceLen)]
	backpointer = [[{} for i in range(sentenceLen+1)] for j in range(sentenceLen)]
	n_term = [key for key in grammar.keys() if type(key[1])==tuple]

	# ...(TASK) fill up score and backpointer table

	#  Creating the first diagnal calculations
	for i, word in enumerate(words):
		for key in grammar.keys():
			if word == key[1]:
				score[i][i+1][key[0]] = grammar[key]

	for span in range(2, sentenceLen+1):
		# handling each diag
		for begin in range(0, sentenceLen-span+1):
			end = begin + span
			# handling each column
			for split in range(begin+1, end):
				for A,B in n_term:
					# Checking if the two nodes are tied to A (main node)
					if B[0] in score[begin][split] and B[1] in score[split][end]:
						prob1 = score[begin][split][B[0]]
						prob2 = score[split][end][B[1]]
						probA_BC = grammar[(A,B)]
						prob = prob1 + prob2 + probA_BC
						if A in score[begin][end]:
							if prob > score[begin][end][A]:
								score[begin][end][A] = prob
								backpointer[begin][end][A] = (split, B[0], B[1])
						else:
							score[begin][end][A] = prob
							backpointer[begin][end][A] = (split, B[0], B[1])

	if len(score[0][-1]) == 0:
		invalidParse = True

	maxScore = 0
	for key, value in score[0][-1].items():
		maxScore = value
	# ...(TASK) return flag invalidParse and max probability parser can get

	return invalidParse, maxScore, backpointer



#... A => B,C, arr1 is for B and arr2 is for C
def addBranch(words, backpointer, arr1, arr2):

	[start1, end1, symb1] = arr1
	[start2, end2, symb2] = arr2

	# for first non-terminal/terminal
	if (end1-start1==1):
		tree1 = Tree(symb1,[words[start1]])
	else:
		B = backpointer[start1][end1][symb1]


		split, R1,R2 = B
		split1a = [start1, split]
		split1b = [split, end1]

		tree1 = Tree(symb1, addBranch(words, backpointer, [start1, split, R1], [split, end1, R2]))


	# for second non-terminal/terminal
	if (end2-start2==1):
		tree2 = Tree(symb2,[words[start2]])
	else:
		C = backpointer[start2][end2][symb2]
		split, R1,R2 = C
		split1a = [start2, split]
		split1b = [split, end2]

		tree2 = Tree(symb2, addBranch(words, backpointer, [start2, split, R1], [split, end2, R2]))

	return [tree1, tree2]

def pretty_print(words, backpointer):

	#... start at the root of the tree
	foundRoot = False
	sentLen = len(backpointer)
	for key,value in backpointer[0][-1].items():
		if key=="S": #... this is the root, REQUIRED symbol
			foundRoot = True
			split, B,C = value
			tree = Tree(key, addBranch(words, backpointer, [0,split,B], [split,sentLen,C]))
			break

	if foundRoot:
		tree.pretty_print()
	else:
		#... This grammar could not match the provided sentence.
		print ("Cannot find root")
		return

	return tree

def main():
	if len(sys.argv) != 4:
		print(('Wrong number of arguments?: %d\nExpected python parser.py ' +
			   'grammar.gr lexicon.txt sentences.txt') % (len(sys.argv)-1))
		exit(1)

	grammar_file = sys.argv[1]
	lexicon_file = sys.argv[2]
	sentences_file = sys.argv[3]

	#... we're assuming that lexicon.txt is line-separated with each line containing
	#... exactly one token that is permissible. The rules for these tokens is contained
	#... in grammar.gr
	lexicon = set()
	with open(lexicon_file) as f:
		for line in f:
			lexicon.add(line.strip())
	print("Saw %d terminal symbols in the lexicon" % (len(lexicon)))

	grammar = load_grammar(grammar_file)

	# non_terminals = get_non_terminals(grammar, lexicon)

	with open(sentences_file) as f:
		for line in f:
			words = line.strip().split()
			invalidParse, score, backpointer = parse(words, grammar)
			if invalidParse:
				print ("Grammar couldn't parse this sentence")
			else:
				print('%f\t%s' % (score, pretty_print(words,backpointer)))


if __name__ == '__main__':
	main()

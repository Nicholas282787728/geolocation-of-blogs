'''
Usage: 
	python extractLIWs.py
'''
# For each state, extract top 20 location indicative words (LIWs) using 
# chi-squared statistcs. Words with frequency less than ten are removed.

import json
from stemmer import PorterStemmer
from geolocation_of_blogs import *


def countWords(word_list, state, data):
	
	# data["word_count"] = {w1:1, w2:2, ...}
	# data["word_count_per_state"] = {s1: {w1: 10, w2: 20, ...},
	# 								s2: {w1: 20, w2: 30, ...}, ...}
	# data["length_per_state"] = {s1: 100, s2: 200, ...}	

	data["length_per_state"][state] += len(word_list)
	for word in word_list:
		data["word_count"][word] = data["word_count"].get(word, 0) + 1 
		data["word_count_per_state"][state][word] = data["word_count_per_state"][state].get(word, 0) + 1



def extractLIWs():

	remove_stopwords = True
	stem = True

	p_stemmer = PorterStemmer()

	US_state_map = json.load(open('state_map.json'))
	US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
	US_state_list = list(US_state_set)

	###################
	# initialize data #
	###################
	data = {}
	data["word_count"] = {}
	data["word_count_per_state"] = {}
	data["length_per_state"] = {}
	data["chi_square"] = {}
	for US_state in US_state_list:
		data["word_count_per_state"][US_state] = {}
		data["length_per_state"][US_state] = 0
		data["chi_square"][US_state] = {}

	state_count = {}
	empty_state_count = {}
	for state in US_state_list:
		state_count[state] = 0
		empty_state_count[state] = 0

	################
	# collect data #
	################
	decode_success_count = 0
	decode_failure_count = 0

	with open('train.csv', 'rb') as csvfile:
		csv.field_size_limit(sys.maxsize)
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			try:
				current_state = stateNamePreprocess(row[0])
				lower_content = row[3].lower()
				content = strip_markup(lower_content)
				files = re.findall(r'[a-zA-Z\']+',content)
				files = [x for x in files if x != "nbsp"]

				if remove_stopwords:
					files = removeStopwords(files)
				if stem:
					files = [ p_stemmer.stem(token, 0, len(token)-1) for token in files ]

				if len(files) == 0:
					empty_state_count[current_state] += 1

				state_count[current_state] += 1
				countWords(files, current_state, data)
				decode_success_count += 1

				if decode_success_count % 1000 == 0:
					print "Processing %d training data" % decode_success_count
			except:
				decode_failure_count += 1

	print "decode_success_count = ", decode_success_count
	print "decode_failure_count = ", decode_failure_count

	# print "state_count = "
	# print state_count
	# print "empty_state_count = "
	# print empty_state_count

	########################
	# calculate chi_square #
	########################
	
	# data["chi_square"] = {s1: {w1:3, w2:2, ...},
	# 						s2: {w3:4, w4:1, ...}, ...}

	# O(w, s) + O(w, ~s) = count(w)
	# O(w, s) + O(~w, s) = count(s)
	# E = count(w) * count(s) / N
	# chi_square[state][word] = ( O(w, s) - E )^2 / E

	N = sum( data["length_per_state"].values() )
	for state in US_state_list:
		for word in data["word_count_per_state"][state]:
			if data["word_count"][word] > 10 and len(word) > 1:
				O = data["word_count_per_state"][state][word]
				E = float(data["word_count"][word]) * float(data["length_per_state"][state]) / N
				data["chi_square"][state][word] = ( O - E ) ** 2 / E

		sorted_chi_square = sorted(data["chi_square"][state].items(), key=lambda x: x[1], reverse=True)
		print ">> State: ", state, "(", US_state_map[state], ")"
		for i in range( min(20, len(sorted_chi_square) ) ):
			print sorted_chi_square[i][0], sorted_chi_square[i][1]


if __name__ == '__main__':
	extractLIWs()


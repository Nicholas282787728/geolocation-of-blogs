# 
from geolocation_of_blogs import *

def main():
	US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
	US_state_list = list(US_state_set)

	# initialize data
	data = {}
	data["word_count"] = {}
	data["word_count_per_state"] = {}
	data["length_per_state"] = {}
	data["X_square"] = {}
	for US_state in US_state_list:
		data["word_count_per_state"][US_state] = {}
		data["length_per_state"][US_state] = 0
		data["X_square"][US_state] = {}

	state_count = {}
	empty_state_count = {}
	for state in US_state_list:
		state_count[state] = 0
		empty_state_count[state] = 0


	# collect data
	decode_success_count = 0
	decode_failure_count = 0

	with open('train.csv', 'rb') as csvfile:
		csv.field_size_limit(sys.maxsize)
		csvreader = csv.reader(csvfile, delimiter=',')
		for row in csvreader:
			try:
				current_state = stateNamePreprocess(row[0])
				lower_content = row[4].lower()
				content = strip_markup(lower_content)

				files = re.findall(r'[a-zA-Z\']+',content)

				files = [x for x in files if x != "nbsp"]

				files = removeStopwords(files)

				if len(files) == 0:
					empty_state_count[current_state] += 1

				state_count[current_state] += 1
				# countWords(files, current_state, data)
				decode_success_count += 1

				if decode_success_count % 1000 == 0:
					print "Processing %d training data" % decode_success_count
			except:
				decode_failure_count += 1

	print "decode_success_count = ", decode_success_count
	print "decode_failure_count = ", decode_failure_count

	# calculate X_square
	'''
	data["X_square"] = {s1: {w1:3, w2:2, ...},
						s2: {w3:4, w4:1, ...}, ...}

	O(w, s) + O(w, ~s) = count(w)
	O(w, s) + O(~w, s) = count(s)
	E = count(w) * count(s) / N
	X_square[state][word] = ( O(w, s) - E )^2 / E
	'''

	N = sum( data["length_per_state"].values() )
	for state in US_state_list:
		for word in data["word_count_per_state"][state]:
			O = data["word_count_per_state"][state][word]
			E = float(data["word_count"][word]) * float(data["length_per_state"]) / N
			data["X_square"][state][word] = ( O - E )^2 / E


def countWords(word_list, state, data):

	'''
	data["word_count"] = {w1:1, w2:2, ...}
	data["word_count_per_state"] = {s1: {w1: 10, w2: 20, ...},
									s2: {w1: 20, w2: 30, ...}, ...}
	data["length_per_state"] = {s1: 100, s2: 200, ...}
	'''

	data["length_per_state"][state] += len(word_list)

	for word in word_list:
		data["word_count"][word] = data["word_count"].find(word, 0) + 1 
		data["word_count_per_state"][state][word] = data["word_count_per_state"][state].find(word, 0) + 1


if __name__ == '__main__':
	main()


# Geolocation_of_blogs
# metadata["class_dict"][class_name]["class_len"]: total word count of class

# for c in metadata["class_dict"]:
# 	print c, metadata["class_dict"][c]["class_len"]

# nonempty_state_count = {x: state_count[x] - empty_state_count[x] for x in state_count}


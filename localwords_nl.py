from __future__ import division
import json
from stemmer import PorterStemmer
#from geolocation_of_blogs import stateNamePreprocess
from math import log
import sys
import csv


def stateNamePreprocess(state_name):
    state_name = state_name.replace(".", "")
    state_name = state_name.replace(" ", "")
    state_name = state_name.upper()

    if state_name == 'VIRGINIA':
        state_name = 'VA'

    if state_name == 'SOUTHDAKOTA':
        state_name = 'SD'

    return state_name

def countWords(word_list, state, data):
    for word in word_list:
        data["word_count"][word] = data["word_count"].get(word, 0) + 1
        if word not in data['word_count_per_state']:
            data['word_count_per_state'][word] = {}
        data["word_count_per_state"][word][state] = data["word_count_per_state"][word].get(state, 0) + 1

    return data

def calculate_prob(data,stopwords,US_state_list):
    prob_words = {}
    freq_stopwords = {}

    for w in data['word_count']:
        prob_words[w] = {}
        for state in US_state_list:
            #add one smoothing
            prob_words[w][state] = data['word_count_per_state'][word].get(state,1) / (data['word_count'][word] + len(US_state_list))
    
    freq_total = 0
    for s in stopwords:
        freq_total += data['word_count'].get(s,0)
    for s in stopwords:
        freq_stopwords[s] = data['word_count'].get(s,0) / freq_total


    return prob_words, freq_stopwords

def sim_SKL(w,s,prob_words,US_state_list):
    sim = 0
    for state in US_state_list:
        sim += prob_words[w][state] * log(prob_words[w][state]/prob_words[s][state])
        sim += prob_words[s][state] * log(prob_words[s][state]/prob_words[w][state])
    return sim

def localwords_NL():

    remove_stopwords = False
    stem = True

    p_stemmer = PorterStemmer()

    US_state_map = json.load(open('state_map.json'))
    US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
    US_state_list = list(US_state_set)

    # read stopword list
    f = open('stopword.txt')
    stopwords = f.read()
    stopwords = stopwords.strip().split()

    # initialize data 
    data = {}
    data["word_count"] = {}
    data["word_count_per_state"] = {}

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
		lower_content = row[3].lower()
		content = strip_markup(lower_content)
		files = re.findall(r'[a-zA-Z\']+',content)
		files = [x for x in files if x != "nbsp"]

		if stem:
                    files = [ p_stemmer.stem(token, 0, len(token)-1) for token in files ]

		if len(files) == 0:
                    empty_state_count[current_state] += 1

		state_count[current_state] += 1
		data = countWords(files, current_state, data)
		decode_success_count += 1

		if decode_success_count % 1000 == 0:
                    print "Processing %d training data" % decode_success_count
            except:
                decode_failure_count += 1


    print "decode_success_count = ", decode_success_count
    print "decode_failure_count = ", decode_failure_count

    sys.exit(0)

    # calculate probability, stopwords freq
    prob_words,freq_stopwords = calculate_prob(data,stopwords)

    # calculate Non-Localness
    non_localness = {}

    for w in data['word_count']:
        non_localness[w] = 0
        for s in stopwords:
            non_localness[w] += freq_stopwords[s] * sim_SKL(w,s,prob_words,US_state_list)

    #pickup words with smallest NL
    words_sorted = sorted(non_localness,key=non_localness.get)
    for w in words_sorted:
        print w
    return words_sorted

if __name__ == '__main__':
    localwords_NL()


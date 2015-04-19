# Geolocation_of_blogs
import argparse
import re
from stemmer import PorterStemmer
import math
import operator
import csv
import sys
from htmllaundry import strip_markup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from tficf import *
from chiSquareLIW import *


def mytokenizer(document):
    return re.findall(r'[a-zA-Z\']+', document)


# input: list of words
# output: list of words
def stemWords(input):
    ps = PorterStemmer()
    tokens_after_stem = []
    for token in input:
        stemmed_token = ps.stem(token, 0, len(token)-1)
        tokens_after_stem.append(stemmed_token)
    return tokens_after_stem


# input: list of words
# output: list of words
def removeStopwords(input):
    stop_words = set()
    stopword_file = open("stopword.txt", 'rU')

    for line in stopword_file:
        vocab = line.replace("\n", "")
        stop_words.add(vocab)

    output = [x for x in input if x not in stop_words]
    stopword_file.close()
    return output


def stateNamePreprocess(state_name):
    state_name = state_name.replace(".", "")
    state_name = state_name.replace(" ", "")
    state_name = state_name.upper()

    if state_name == 'VIRGINIA':
        state_name = 'VA'

    if state_name == 'SOUTHDAKOTA':
        state_name = 'SD'

    return state_name



def chiTopWords(percentage, US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])):
    
    sorted_chi_square = json.load(open('chi_LIW.json'))

    # count the number of total words
    total_word_set = set()
    for state in sorted_chi_square:
        for x in sorted_chi_square[state]:
            total_word_set.add(x[0])
    total_N = len(total_word_set)

    # select top percentage% of unique words
    selected_word_set = set()
    m = 0
    while len(selected_word_set) < (float(total_N) * float(percentage) / 100.0):
        for state in US_state_set:
            if len(sorted_chi_square[state]) > m:
                selected_word_set.add( sorted_chi_square[state][m][0] )
        m += 1

    return list(selected_word_set)


## input:
## method = tficf or chi or igr
## percentage = 0.0 - 1.0
## output:
## accuracy

def SVM(method = "original", percentage = 0):
    corpus = []
    label = []

    decode_failure_count = 0
    decode_success_count = 0

    print "Processing training data"

    with open('train.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                lower_content = row[3].lower()
                content = strip_markup(lower_content)
                content = content.encode('ascii','ignore')
                if current_state in ['MI', 'CA'] and len(content) != 0:
                    corpus.append(content)
                    label.append(current_state)
                decode_success_count += 1
                if decode_success_count % 1000 == 0:
                    print "Processing %d training data" % decode_success_count
            except:
                decode_failure_count += 1

    print len(corpus)
    print len(label)

    if method == 'tficf':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = tficf('train.csv', percentage))
    elif method == 'igr':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = igr('train.csv', percentage))
    elif method == 'chi':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = chiTopWords(percentage, set(['CA', 'MI'])))
    else:
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer)

    lin_clf = LinearSVC()
    print "Processing TfidfVectorizer fit_transform"
    X = vectorizer.fit_transform(corpus)
    print "Processing lin_clf.fit(X, label)"
    lin_clf.fit(X, label)

    ####################################################################
    ####################################################################

    while(1):
        content = raw_input("Input text: ")
        content = content.lower()
        
        test_corpus = []
        test_corpus.append(content)

        testX = vectorizer.transform(test_corpus)
        result = lin_clf.predict(testX)

        print "State:", result


def main():
    result = SVM('chi', 10)

if __name__ == '__main__':
    main()

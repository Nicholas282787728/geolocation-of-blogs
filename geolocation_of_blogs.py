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


# input: list of classes (50 states)
# output: metadata struct

# metadata: dictionary
# metadata["train_count"]: number of posts for training
# metadata["vocab_set"]: set of vocabs
# metadata["class_dict"]: dictionary for classes

# metadata["class_dict"][class_name]["class_len"]: total word count of class
# metadata["class_dict"][class_name]["class_count"]: total number of posts of class
# metadata["class_dict"][class_name]["class_word_count"]: dictionary of word count

def initializeNaiveBayes(class_list):
    metadata = dict()
    metadata["train_count"] = 0
    metadata["vocab_set"] = set()
    metadata["class_dict"] = dict()

    for class_name in class_list:
        metadata["class_dict"][class_name] = dict()
        metadata["class_dict"][class_name]["class_len"] = 0
        metadata["class_dict"][class_name]["class_count"] = 0
        metadata["class_dict"][class_name]["class_word_count"] = dict()

    return metadata


def initializeTestStats(class_list):
    metadata = dict()
    for class_name in class_list:
        metadata[class_name] = [0,0,0]

    return metadata


# input: list_of_words, class
# train one post and update metadata
def trainNaiveBayes(list_of_words, class_name, metadata):
    metadata["train_count"] += 1
    metadata["class_dict"][class_name]["class_len"] += len(list_of_words)
    metadata["class_dict"][class_name]["class_count"] += 1

    for word in list_of_words:
        metadata["vocab_set"].add(word)
        if word in metadata["class_dict"][class_name]["class_word_count"]:
            metadata["class_dict"][class_name]["class_word_count"][word] += 1
        else:
            metadata["class_dict"][class_name]["class_word_count"][word] = 1

# input: list_of_words, class_list, metadata
# test one post and return predicted result
def testNaiveBayes(list_of_words, class_list, metadata):
    class_prob = dict()

    for class_name in class_list:
        class_prob[class_name] = math.log10(float(metadata["class_dict"][class_name]["class_count"])/float(metadata["train_count"]))

    for word in list_of_words:
        for class_name in class_list:
            if word in metadata["class_dict"][class_name]["class_word_count"]:
                class_prob[class_name] += math.log10(float(1+metadata["class_dict"][class_name]["class_word_count"][word])/float(len(metadata["vocab_set"])+metadata["class_dict"][class_name]["class_len"]))
            else:
                class_prob[class_name] += math.log10(float(1)/float(len(metadata["vocab_set"])+metadata["class_dict"][class_name]["class_len"]))

    return max(class_prob.iteritems(), key=operator.itemgetter(1))[0]


def naiveBayes():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', nargs=1)
    args = parser.parse_args()

    US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
    US_state_list = list(US_state_set)
    metadata = initializeNaiveBayes(US_state_list)

    #############################################################
    ######################## Training ###########################
    #############################################################

    decode_success_count = 0
    decode_failure_count = 0

    with open('train.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                lower_content = row[3].lower()
                content = strip_markup(lower_content)
                files = re.findall(r'[a-zA-Z\']+',content)

                files = [x for x in files if x != "nbsp"]

                files = removeStopwords(files)

                trainNaiveBayes(files, current_state, metadata)
                decode_success_count += 1

                if decode_success_count % 1000 == 0:
                    print "Processing %d training data" % decode_success_count
            except:
                decode_failure_count += 1

    # print decode_success_count
    # print decode_failure_count


    # for state_name in US_state_list:
    #     current_dict = metadata["class_dict"][state_name]["class_word_count"]
    #     result = sorted(current_dict.items(), key=lambda t: (-t[1],t[0]))
    #     print state_name, result[:10]


    #############################################################
    ######################## Testing  ###########################
    #############################################################

    decode_failure_test_count = 0
    decode_success_test_count = 0
    predict_correct_count = 0

    testing_stats = initializeTestStats(US_state_list)

    with open('test.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                lower_content = row[3].lower()
                content = strip_markup(lower_content)
                files = re.findall(r'[a-zA-Z\']+',content)

                files = [x for x in files if x != "nbsp"]

                files = removeStopwords(files)

                predicted_state = testNaiveBayes(files, US_state_list, metadata)

                decode_success_test_count += 1
                testing_stats[current_state][1] += 1

                testing_stats[predicted_state][2] += 1

                if predicted_state == current_state:
                    predict_correct_count += 1
                    testing_stats[current_state][0] += 1

                if decode_success_test_count % 1000 == 0:
                    print "Processing %d testing data" % decode_success_test_count
                    print "predict_correct_count:", predict_correct_count

                # if decode_success_test_count == 2000:
                #     break

            except:
                decode_failure_test_count += 1

    test_accuracy = float(predict_correct_count)/ float(decode_success_test_count)

    print "decode_success_test_count:", decode_success_test_count
    print "predict_correct_count:", predict_correct_count
    print "Accuracy ", test_accuracy
    # print decode_failure_test_count

    for state in testing_stats:
        if testing_stats[state][1] != 0 and testing_stats[state][2] != 0:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], float(testing_stats[state][0])/float(testing_stats[state][1]), float(testing_stats[state][0])/float(testing_stats[state][2])
        elif testing_stats[state][1] != 0:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], float(testing_stats[state][0])/float(testing_stats[state][1]), "NA"
        else:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], "NA", "NA"



## input:
## method = tficf or chi or igr
## percentage = 0.0 - 1.0
## output:
## accuracy

def SVM(method = "original", percentage = 0):
    corpus = []
    label = []

    US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
    US_state_list = list(US_state_set)

    decode_failure_count = 0

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
                if len(content) != 0:
                    corpus.append(content)
                    label.append(current_state)

            except:
                decode_failure_count += 1

    print "decode_failure_count: ", decode_failure_count
    print len(corpus)
    print len(label)

    if method == 'tficf':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = tficf('train.csv', percentage))
    elif method == 'igr':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = igr('train.csv', percentage))
    elif method == 'chi':
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer, vocabulary = chiTopWords(percentage))
    else:
        vectorizer = TfidfVectorizer(tokenizer = mytokenizer)

    lin_clf = LinearSVC()
    print "Processing TfidfVectorizer fit_transform"
    X = vectorizer.fit_transform(corpus)
    print "Processing lin_clf.fit(X, label)"
    lin_clf.fit(X, label)

    ####################################################################
    ####################################################################

    print "Processing test data"

    test_corpus = []
    test_label = []
    test_decode_failure_count = 0

    with open('test.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                lower_content = row[3].lower()
                content = strip_markup(lower_content)
                content = content.encode('ascii','ignore')
                if len(content) != 0:
                    test_corpus.append(content)
                    test_label.append(current_state)

            except:
                test_decode_failure_count += 1

    print "test_decode_failure_count: ", test_decode_failure_count

    print "Processing testX = vectorizer.transform(test_corpus)"
    testX = vectorizer.transform(test_corpus)
    print "Processing Predict"
    result = lin_clf.predict(testX)


    index = 0
    correct_count = 0
    incorrect_count = 0


    testing_stats = initializeTestStats(US_state_list)

    for result_row in result:
        testing_stats[result_row][2] += 1
        testing_stats[test_label[index]][1] += 1

        if result_row == test_label[index]:
            correct_count += 1
            testing_stats[test_label[index]][0] += 1
        else:
            incorrect_count += 1
        index += 1


    for state in testing_stats:
        if testing_stats[state][1] != 0 and testing_stats[state][2] != 0:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], float(testing_stats[state][0])/float(testing_stats[state][1]), float(testing_stats[state][0])/float(testing_stats[state][2])
        elif testing_stats[state][1] != 0:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], float(testing_stats[state][0])/float(testing_stats[state][1]), "NA"
        else:
            print state, testing_stats[state][0], testing_stats[state][1], testing_stats[state][2], "NA", "NA"

    return float(correct_count)/float(correct_count+incorrect_count)

def main():
    # naiveBayes()
    result = SVM()
    # result = SVM('chi', 50)
    print result

    # outputFile = open("output.txt", "w")
    # outputFile.write("tficf:")
    # for i in range(85,100, 5):
    #     percentage = float(i) / float(100)
    #     print 'tficf percentage = %f' % (percentage)
    #     accuracy = SVM('tficf', percentage)
    #     print 'percentage = %f \t accuracy = %f' % (percentage, accuracy)
    #     outputFile.write('percentage = %f \t accuracy = %f' % (percentage, accuracy))

    # outputFile.close()
if __name__ == '__main__':
    main()

# Geolocation_of_blogs
import argparse
import re
from stemmer import PorterStemmer
import math
import operator
import csv
import sys
from htmllaundry import strip_markup

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


def main():
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
                lower_content = row[4].lower()
                content = strip_markup(lower_content)
                files = re.findall(r'[a-zA-Z\']+',content)

                trainNaiveBayes(files, current_state, metadata)
                decode_success_count += 1

                if decode_success_count % 1000 == 0:
                    print "Processing %d training data" % decode_success_count
            except:
                decode_failure_count += 1

    # print decode_success_count
    # print decode_failure_count


    #############################################################
    ######################## Testing  ###########################
    #############################################################

    decode_failure_test_count = 0
    decode_success_test_count = 0
    predict_correct_count = 0

    with open('test.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                lower_content = row[4].lower()
                content = strip_markup(lower_content)
                files = re.findall(r'[a-zA-Z\']+',content)

                predicted_state = testNaiveBayes(files, US_state_list, metadata)

                decode_success_test_count += 1
                if predicted_state == current_state:
                    predict_correct_count += 1

                if decode_success_test_count % 1000 == 0:
                    print "Processing %d testing data" % decode_success_test_count
                    print "predict_correct_count:", predict_correct_count

                if decode_success_test_count == 10000:
                    break

            except:
                decode_failure_test_count += 1

    test_accuracy = float(predict_correct_count)/ float(decode_success_test_count)

    print "decode_success_test_count:", decode_success_test_count
    print "predict_correct_count:", predict_correct_count
    print "Accuracy ", test_accuracy
    # print decode_failure_test_count

if __name__ == '__main__':
    main()
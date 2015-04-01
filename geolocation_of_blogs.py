# Geolocation_of_blogs
import argparse
import re
from stemmer import PorterStemmer
import math
import operator
import csv
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

    with open('myblogs.csv', 'rb') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            post =  ' || '.join(row)
            print strip_markup(post)




if __name__ == '__main__':
    main()
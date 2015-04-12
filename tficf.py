# tf-icf
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
from geolocation_of_blogs import *
from collections import OrderedDict
from operator import itemgetter, attrgetter, methodcaller

## input: string 
## output: list of words
def tokenizeText(string): 
    string = re.sub('i\'m', ' i am ', string) # i'm => i am
    string = re.sub('you\'re', ' you are ', string) # you're => you are    
    string = re.sub('he\'s', ' he is ', string) # he's => he is
    string = re.sub('she\'s', ' she is ', string) # she's => he is
    string = re.sub('she\'s', ' she is ', string) # she's => he is
    string = re.sub('i\'ve', ' i have ', string) # i've => i have
    string = re.sub('haven\'t', ' have not ', string) # haven't => have not 
    string = re.sub('hasn\'t', ' has not ', string) # hasn't => has not 
    string = re.sub('\'s', ' \'s ', string) # saturday's =>saturday 's
    wordlist = re.findall('\d+,\s\d+,\s\d+',string) 
    string = re.sub('\d+,\s\d+,\s\d+', ' ',string) 
    wordlist += re.findall('\w+\.\s\w+\.\s\w+\.*',string) 
    string = re.sub('\w+\.\s\w+\.\s\w+\.*', ' ',string) 
    string = re.sub('\s+[/.,-]+\s+', ' ', string)  
    string = re.sub('[/.-]+\s+', ' ', string)
    string = re.sub('\s+[/.-]+', ' ', string)
    string = re.sub('[/.,-]+\s+', ' ', string)
    string = re.sub('\s+[/.,-]+', ' ', string) 
    string = re.sub('\s+\.+', ' ', string)   
    string = re.sub('\.+\s+', ' ', string)   
    string = re.sub('\s+\,+', ' ', string)   
    string = re.sub('\,+\s+', ' ', string)   
    string = re.sub('\.$', ' ', string)
    string = re.sub('\,\s', ' ', string)    
    string = string .strip()    
    wordlist1 = re.split('\s+', string)
    wordlist += wordlist1
    
    return wordlist

## input: string filePath, float rankPercentage (0.0 - 1.0)
## output: list of words
## EX: ('train.csv', 0.5) will return top 50% of words ranked by icf then tf in decreasing order
def tficf(filePath, rankPercentage): 
    if rankPercentage > 1 or rankPercentage < 0:
        return -1
    
    word_dict = {}
    decode_failure_count = 0

    with open(filePath, 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                wordlist = []
                current_state = stateNamePreprocess(row[0])
                lower_content = row[4].lower()
                content = strip_markup(lower_content)                 
                content = content.encode('ascii','ignore')
                wordlist = mytokenizer(content)
                
                for word in wordlist:
                    if word not in word_dict:
                        metadata = [1, 1, set(current_state)]
                        word_dict[word] = metadata
                    else:
                        word_dict[word][0] += 1
                        if current_state not in word_dict[word][2]:
                            word_dict[word][1] += 1
                            word_dict[word][2].add(current_state)            
            except:
                decode_failure_count += 1
    
    for key in word_dict:
        word_dict[key][1] = float(50) / float(word_dict[key][1])
    
    ordered_word_dict = OrderedDict(sorted(word_dict.items(), key=lambda x: (x[1][1], x[1][0]), reverse=True))
    
    #count = 1
    #for key in ordered_word_dict:
    #    print "tf = %d  \t icf = %f \t %s" % (ordered_word_dict[key][0], ordered_word_dict[key][1], key) 
    #    count += 1

    ordered_word_list = ordered_word_dict.keys()
    
    return ordered_word_list[:int(len(ordered_word_list) * rankPercentage)]    


def main():
    wordlist = tficf('train.csv', 0.5)


if __name__ == '__main__':
    main()

import re
from stemmer import PorterStemmer
import math
import csv
import sys
from htmllaundry import strip_markup

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



#IGR - Information Gain Ratio
#Input: (File_name) Filename, (Per) Percentage of top words we want to select
#Output: (Word_list) Word list of selected LIW

def igr(File_name, Per):
    decode_failure_count = 0
    decode_success_count = 0
    word_count = 0
    word_dict = dict()
    state_dict = dict()
    word_state_dict = dict()
    with open(File_name, 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            try:
                current_state = stateNamePreprocess(row[0])
                

                lower_content = row[3].lower()
                content = strip_markup(lower_content)
                files = re.findall(r'[a-zA-Z\']+',content)
                files = removeStopwords(files)
                if current_state not in  state_dict:
                    state_dict[current_state] = 1
                else:
                    state_dict[current_state] += 1

                word_set = set()
                for word in files:
                    if len(word)>2:
                        word_set.add(word)
                        word_count += 1
                        if word not in word_dict:
                            word_dict[word] = 1
                        else:
                            word_dict[word] += 1

                for word in word_set:
                    if word not in word_state_dict:
                        new_dict = dict()
                        new_dict[current_state] = 1
                        word_state_dict[word] = new_dict
                    elif current_state not in word_state_dict[word]:
                        word_state_dict[word][current_state] = 1
                    else:
                        word_state_dict[word][current_state] += 1

                decode_success_count += 1

                if decode_success_count % 10000 == 0:
                    print "Processing %d training data" % decode_success_count
            except:
                decode_failure_count += 1


    ranking = list()
    for word in word_dict:
        if sum(word_state_dict[word].values())>=50:
            p_w = sum(word_state_dict[word].values())/float(sum(state_dict.values()))
            intrinsic_entropy = -p_w*math.log(p_w, 2) - (1-p_w)*math.log(1-p_w, 2)
            pre_sum = 0
            abs_sum = 0
            for state in state_dict:
                if state in word_state_dict[word]:
                    state_count = word_state_dict[word][state]
                else:
                    state_count = 0
                if state_count>0:
                    pre_sum += state_count/float(sum(word_state_dict[word].values()))*math.log(state_count/float(sum(word_state_dict[word].values())), 2)
                if state_dict[state]!=state_count:
                    abs_sum += (state_dict[state]-state_count)/float(sum(state_dict.values())-sum(word_state_dict[word].values()))*math.log((state_dict[state]-state_count)/float(sum(state_dict.values())-sum(word_state_dict[word].values())), 2)
            information_gain = p_w * pre_sum + (1-p_w) * abs_sum

            information_gain_ratio = information_gain/float(intrinsic_entropy)
            ranking.append((word, information_gain_ratio))

    
    
    result = sorted(ranking, key = lambda ranking:ranking[1])
    outfile = open("score_"+str(Per)+".txt",'wb')
    for feature in result[0:200]:
        outfile.write(str(feature)+'\n')
    res = [i[0] for i in result]
    res = res[:int(len(result)*Per)]
    return res


def main():
    wordlist = igr('test.csv', 0.01)


if __name__ == '__main__':
    main()




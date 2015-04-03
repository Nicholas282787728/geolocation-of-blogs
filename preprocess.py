# Preprocess
import csv
import sys
from htmllaundry import strip_markup

def stateNamePreprocess(state_name):
    state_name = state_name.replace(".", "")
    state_name = state_name.replace(" ", "")
    state_name = state_name.upper()

    if state_name == 'VIRGINIA':
        state_name = 'VA'

    if state_name == 'SOUTHDAKOTA':
        state_name = 'SD'

    return state_name


def main():
    US_state_set = set(['WA', 'DE', 'WI', 'WV', 'HI', 'FL', 'WY', 'NH', 'KS', 'NJ', 'NM', 'TX', 'LA', 'NC', 'ND', 'NE', 'TN', 'NY', 'PA', 'RI', 'NV', 'VA', 'CO', 'CA', 'AL', 'AR', 'VT', 'IL', 'GA', 'IN', 'IA', 'MA', 'AZ', 'ID', 'CT', 'ME', 'MD', 'OK', 'OH', 'UT', 'MO', 'MN', 'MI', 'AK', 'MT', 'MS', 'SC', 'KY', 'OR', 'SD'])
    test_author_count = 10

    # state_author_dict = dict()
    state_test_author_dict = dict()
    state_train_test_count = dict()

    output_csvfile_train = open('train.csv', 'w')
    spamwriter_train = csv.writer(output_csvfile_train, delimiter=',')

    output_csvfile_test = open('test.csv', 'w')
    spamwriter_test = csv.writer(output_csvfile_test, delimiter=',')

    count = 0

    with open('myblogs_v2.csv', 'rb') as csvfile:
        csv.field_size_limit(sys.maxsize)
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            count += 1
            current_state = stateNamePreprocess(row[0])
            current_author = row[1]

            # if current_state in state_author_dict:
            #     state_author_dict[current_state].add(row[1])
            # else:
            #     state_author_dict[current_state] = set()
            #     state_author_dict[current_state].add(row[1])

            if current_state in state_test_author_dict:
                if current_author in state_test_author_dict[current_state]:
                    state_train_test_count[current_state][1] += 1
                    spamwriter_test.writerow(row)
                elif len(state_test_author_dict[current_state]) < test_author_count:
                    state_test_author_dict[current_state].add(current_author)
                    state_train_test_count[current_state][1] += 1
                    spamwriter_test.writerow(row)
                else:
                    state_train_test_count[current_state][0] += 1
                    spamwriter_train.writerow(row)
            else:
                state_test_author_dict[current_state] = set()
                state_test_author_dict[current_state].add(current_author)
                state_train_test_count[current_state] = [0,1]
                spamwriter_test.writerow(row)

            # post =  ' || '.join(row)
            # print strip_markup(post)
            # raw_input()

        print count
        for state in state_train_test_count:
            print state, state_train_test_count[state]

    output_csvfile_test.close()
    output_csvfile_train.close()

if __name__ == '__main__':
    main()
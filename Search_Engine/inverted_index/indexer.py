import methods
from os import listdir
from os.path import isfile, join
import json
import time

start_time = time.time()
files = [] #All file path
postings = [] #posting for all files, [word, path, wordFrequency]
term = 'and'
N = 0 #Number of all files

for i in range(2): #Total number of folder is 75
    cur_files = [str(i) + '/' + f for f in listdir('WEBPAGES_CLEAN' + '/' + str(i)) if isfile(join('WEBPAGES_CLEAN'+ '/' + str(i), f))]
    files += cur_files
    N += len(cur_files)

for f in files:
    print('scanning... ' + f)
    curr_token = methods.tokenize(f)
    curr_count = methods.computeWordFrequencies(curr_token)
    posting = []
    for key, value in curr_count.items():
        posting.append([key, f, value ])
    postings += posting

tokenMap = methods.buildPosting(postings)
# doc = 'WEBPAGES_CLEAN/0/61'
# weight = methods.getWeight(tokenMap, term, doc, N)

with open('index.txt', 'w') as file:
     file.write(json.dumps(tokenMap)) # use `json.loads` to do the reverse

print("--- Build the posting: %s seconds ---" % (time.time() - start_time))

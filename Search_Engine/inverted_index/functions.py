from __future__ import division
import time
import csv
import os
import re
import operator
import math
from os import listdir
from os.path import isfile, join
import json
import time
from .models import Token

def tokenize(path):
    """
    Toknize the file, return inverted index, without position
    """
    TextFilePath = 'WEBPAGES_CLEAN/' + path
    f=open(TextFilePath)
    tokenList=[]
    pos = 0
    for line in f:
        for word in re.findall(r'\d+\.\d+' '|\w+\-\w+' '|\w+\'\w+' '|\w+\' \w+' '|\w+', line): #special cases
            #for word in re.findall(r'\w+', line):
            tokenList.append([word.lower(), path])
    f.close()
    return tokenList

def computeWordFrequencies(tokens):
    """
    Calculate the word frequency
    """
    counts=dict()
    for tokens in tokens:
        word = tokens[0]
        if word in counts:
            counts[word]+=1
        else:
            counts[word]=1
    # sorted_counts = sorted(counts.items(), key=operator.itemgetter(1))
    # sorted_counts.reverse()
    return counts

def buildPosting(postings):
    """
    Build posting for all, merge the same word
    """
    invertedIndex = dict()
    for posting in postings:
        key = posting[0]
        path = posting[1]
        count = posting[2]
        #print('adding...', key, path, count)
        if key not in invertedIndex:
            #invertedIndex[key] = []
            invertedIndex[key] = str(str(path) + "," + str(count))
        else:
            #invertedIndex[key].append([path, count])
            invertedIndex[key] += str('|' + str(path) + "," + str(count))

    return invertedIndex

def getWeight(tokenMap, term, doc, N):
    postings = tokenMap[term]
    tf = 0
    for posting in postings:
        if posting[0] == doc:
            tf += 1
    df = len(postings)
    weight = math.log10(1 + tf) * math.log10(N/df)
#print('postings: ', postings)
#print('N: ', N)
#print('tf: ', tf)
#print('df: ', df)
#print('weight: ', weight)
    return weight
    
def getWeightForDatabase(term, N):
    token = Token.objects.get(word=term)
    token = token.path.split('|')
    df=len(token) #document freqnency

    ranking = [] #ranking
    for item in token:
        item = item.split(',')
        weight = math.log10(1 + int(item[1])) * math.log10(N/df)
        ranking.append([item[0], weight])
    sort=sorted(ranking,key=lambda e:e[1],reverse=True)
    return sort[:50]

def readPosting(TextFilePath):
    file=open(TextFilePath).read()
    index=dict()
    index=eval(file)
    return index
    
def initialDatabase():
    #start_time = time.time()
    files = [] #All file path
    postings = [] #posting for all files, [word, path, wordFrequency]
    term = 'and'
    N = 0 #Number of all files

    for i in range(75): #Total number of folder is 75
        cur_files = [str(i) + '/' + f for f in listdir('WEBPAGES_CLEAN' + '/' + str(i)) if isfile(join('WEBPAGES_CLEAN'+ '/' + str(i), f))]
        files += cur_files
        N += len(cur_files)

    for f in files:
        #print('scanning... ' + f)
        curr_token = tokenize(f)
        curr_count = computeWordFrequencies(curr_token)
        posting = []
        for key, value in curr_count.items():
            posting.append([key, f, value ])
        postings += posting

    #The final postings, key : [[path1, tf2], [path2, tf2]]
    tokenMap = buildPosting(postings)
    # doc = 'WEBPAGES_CLEAN/0/61'
    # weight = getWeight(tokenMap, term, doc, N)
    
    token_list = []
    for key, value in tokenMap.items():
        token = Token(word=key, path=value)
        token_list.append(token)
        
    Token.objects.bulk_create(token_list)
    """
    with open('index.txt', 'w') as file:
         file.write(json.dumps(tokenMap)) # use `json.loads` to do the reverse

    print("--- Build the posting: %s seconds ---" % (time.time() - start_time))
    """

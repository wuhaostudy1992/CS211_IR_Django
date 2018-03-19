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
from .models import Token, Mapping
#import numpy as np

mapping = dict()

def tokenize(path):
    """
    Toknize the file, return inverted index, without position
    """
    TextFilePath = 'WEBPAGES_CLEAN/' + path
    f=open(TextFilePath)
    tokenList=[]
    pos = 0
    for line in f:
        #for word in re.findall(r'\d+\.\d+' '|\w+\-\w+' '|\w+\'\w+' '|\w+\' \w+' '|\w+', line): #special cases
        for word in re.findall(r'\w+', line):
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
    return weight
    
def getWeightForDatabase(terms, N, filename):
    """
    get weight of different terms
    terms:
    N: total number of files
    filename: mappings from file path to URL
    """
    terms = terms.lower().split(' ')
    postings = []
    for i in range(len(terms)):
        try:
            token = Token.objects.get(word=terms[i]).path.split('|')
        except:
            continue
        tokens = []
        for item in token:
            item = item.split(',')
            tokens.append(item)
        for item in tokens:
            if item[0] == '51/46':
                print(terms[i], ':', item)
        #df=len(token) #document freqnency
        tokens = dict(tokens)
        #postings.append([token, tf])
        postings.append(tokens)
    
    intersect = dict()
    for i in range(len(postings)):
        if not intersect:
            intersect = postings[i]
        else:
            temp = dict()
            for k in set(intersect.keys())&set(postings[i].keys()):
                temp[k] = int(intersect.get(k)) + int(postings[i].get(k))
            intersect = temp
    
    df=len(intersect) #document freqnency
    
    ranking = [] #ranking
    for key, value in intersect.items():
        if key == '51/46':
            print(value, df)
        weight = math.log10(1 + int(value)) * math.log10(N/df)
        ranking.append([key, weight])
        
    return mappingDocidToLink(ranking, filename)
    
def mappingDocidToLink(ranking, filename):
    sort=sorted(ranking,key=lambda e:e[1],reverse=True)
    
    '''
    This method is not efficient enough.
    mappings = Mapping.objects.all()
    data = dict()
    for item in mappings:
        data[item.file_name] = item.URL
    '''
    global mapping
    if not mapping:
        with open(filename, 'r') as f:
            mapping = json.load(f)
    for item in sort:
        #item[0] = Mapping.objects.get(file_name=item[i]).URL
        item[0] = mapping[item[0]]
    
    #sort = np.array(sort)[:, 0]
    return sort

def readPosting(TextFilePath):
    file=open(TextFilePath).read()
    index=dict()
    index=eval(file)
    return index
    
def getIntersect(tokenMap, query):
    terms=query.split(' ')
    postings=[]
    intersect=dict(tokenMap[terms[0]])
    for i in range(0,len(terms)):
        postings.append(tokenMap[terms[i]])
    for i in range(1,len(terms)):
        temp=intersect
        intersect=dict()
        for k in set(temp.keys())&set(dict(postings[i]).keys()):
            intersect[k]=temp.get(k) + dict(postings[i]).get(k)
    return intersect
    
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
    
def initialMapping(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    mapping_list = []
    for key, value in data.items():
        mapping = Mapping(file_name=key, URL=value)
        mapping_list.append(mapping)
        
    Mapping.objects.bulk_create(mapping_list)
    
def calculateScore(query, N, filename):
    """
    By vectoring the query and document name to rank all pages
    """
    terms = query.split(' ')
    q = set(terms)
    d = set()
    df = dict()
    tf = dict() # To store all tf of docuemnt
    docname = []
    for term in terms:
        try:
            token = Token.objects.get(word=term).path.split('|')
        except:
            continue
        for item in token:
            item = item.split(',')
            #t = lxml.html.parse("http://"+str(map[key].strip('\n')))
            #title=str(t.find(".//title").text.encode('utf-8'))
            docname = docname(item[0]).split(' ')
            tfSingle = dict()
            for word in docname:
                if word in tfSingle.keys():
                    tfSingle[word] += 1
                else:
                    tfSingle[word] = 1
            tf[item[0]] = tfSingle
        df[term]=len(token) #document freqnency

    total = 0
    for key, value in df.items():
        #idf
        df[key] = math.log10(N/value)
        total += df[key]**2
    for key, value in df.items():
        #Normalized weight of idf
        df[key] /= math.sqrt(total)
    
    result = dict()
    for docid, value in tf.items():
        total = 0
        for key in value.keys():
            value[key] = 1 + math.log10(times)
            total += value[key]**2
        for key, times in value.items():
            value[key] = times / math.sqrt(total)
        score = 0
        for key in value.keys():
            if key in df.keys():
                score += value[key] * df[key]
        result[docid] = score
        
    return mappingDocidToLink(result, filename)

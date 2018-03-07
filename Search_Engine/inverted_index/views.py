from django.shortcuts import render
from .models import Token
from .forms import SearchForm
from . import functions as af
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from os import listdir
from os.path import isfile, join
import json
import time
import operator

def home_page(request):
    """The home page for search engine."""
    if request.method != 'POST':
        form = SearchForm()
    else:
        # POST data submitted; search data.
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            #query = query.split(' ')
            #results = queryResult(query)
            context = {'form': form, 'results': queryResult(query)}
            return render(request, 'inverted_index/home_page.html', context)
    context = {'form': form}
    return render(request, 'inverted_index/home_page.html', context)
    
def queryResult(term):
    #start_time = time.time()

    N = 37497
    #print("Reading postings...")
    #index=af.readPosting('index.txt')
    #print index
    #print("--- Read the postings: %s seconds ---" % (time.time() - start_time))
    #print("Computing rankings...")
    """
    ranking=dict()
    for i in range(2):
        for f in listdir('WEBPAGES_CLEAN' + '/' + str(i)):
            docID=str(i) + '/' + f
            ranking[docID]=af.getWeight(index,term,docID,N)

    sorted_ranking = sorted(ranking.items(), key=operator.itemgetter(1), reverse=True)
    """
    ranking = af.getWeightForDatabase(term, N)
        
    '''print('--- Query Result: ---')
    for item in sorted_ranking:
        if item[1] > 0.0:
            print('')
            print(item[0], item[1])'''
    return ranking
    
def tokens(request):
    """Show all tokens"""
    if request.method == 'POST':
        af.initialDatabase()

    tokens = Token.objects.all()[:50]
    context = {'tokens': tokens}
    return render(request, 'inverted_index/tokens.html', context)

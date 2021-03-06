from django.shortcuts import render
from .models import Token, Mapping
from .forms import SearchForm
from . import functions as af
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse

from os import listdir
from os.path import isfile, join
import json
import time
import operator
import numpy as np

def home_page(request):
    """The home page for search engine."""
    if request.method != 'POST':
        form = SearchForm()
    else:
        # POST data submitted; search data.
        form = SearchForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            start_time = time.time()
            rank = dict(queryResult(query))
            end_time = time.time()
            context = {'form': form, 'ranks': rank, 'consumedtime' : end_time - start_time, 'totalResult': len(rank)}
            return render(request, 'inverted_index/home_page.html', context)
    context = {'form': form}
    return render(request, 'inverted_index/home_page.html', context)
    
def queryResult(term):
    N = 37497
    filename = 'bookkeeping.json'
    start_time = time.time()
    ranking = af.getWeightForDatabase(term, N, filename)
    #ranking = af.calculateScore(term, N, filename)
    print("--- Search time: %s seconds ---" % (time.time() - start_time))
    #ranking = np.array(ranking)
    return ranking
    
def tokens(request):
    """Show all tokens"""
    if request.method == 'POST':
        start_time = time.time()
        af.initialDatabase()
        print("--- Build the database takes: %s seconds ---" % (time.time() - start_time))

    tokens = Token.objects.all()[:50]
    context = {'tokens': tokens}
    return render(request, 'inverted_index/tokens.html', context)
    
def mapping(request):
    """map file path to URL"""
    filename = 'bookkeeping.json'
    if request.method == 'POST':
        # Create mappings
        af.initialMapping(filename)
    return render(request, 'inverted_index/mapping.html', None)

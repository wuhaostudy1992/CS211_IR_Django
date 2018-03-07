"""Defines URL patterns for inverted index"""

from django.conf.urls import url
from . import views
urlpatterns = [
    # Home page
    url(r'^$', views.home_page, name='home_page'),
    url(r'^tokens/$', views.tokens, name='tokens'),
]

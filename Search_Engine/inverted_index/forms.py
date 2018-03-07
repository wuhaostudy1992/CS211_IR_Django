from django import forms
#from .models import Token


class SearchForm(forms.Form):
    query = forms.CharField()
    
#class SingleButton(forms.Form):  
